"""Build one local MSMARCO-XI language FAISS index.

The builder reads Parquet files from ``MSMARCO_XI_DATASET_PATH`` directly. It
does not use Hugging Face streaming and does not download data.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

import faiss

from retrieval.chunking import chunk_sentence_aware
from retrieval.index_store import (
    get_batch_size,
    get_dataset_path,
    get_index_root,
    get_split,
    is_complete_index,
    language_index_dir,
)
from retrieval.indexer import VectorIndexer
from retrieval.languages import normalize_language_code, to_msmarco_xi_code
from retrieval.retriever import DenseRetriever
from ingestion.msmarco_xi_local import (
    DatasetNotFoundError,
    SchemaInferenceError,
    find_language_file,
    first_text,
    get_nested_value,
    values_as_texts,
)


DATASET_NAME = "ai4bharat/MSMARCO-XI"
DEFAULT_EMBEDDING_MODEL = "intfloat/multilingual-e5-small"
PARTIAL_INDEX_NAME = "partial_faiss_index.index"
PARTIAL_METADATA_NAME = "partial_metadata.jsonl"
CHECKPOINT_NAME = "checkpoint.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def atomic_write_json(path: Path, value: dict) -> None:
    atomic_write_text(path, json.dumps(value, ensure_ascii=False, indent=2))


def write_faiss_atomic(index, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.tmp")
    faiss.write_index(index, str(tmp))
    os.replace(tmp, path)


def count_jsonl_lines(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8") as handle:
        return sum(1 for line in handle if line.strip())


def truncate_jsonl_lines(path: Path, line_count: int) -> None:
    tmp = path.with_name(f"{path.name}.tmp")
    written = 0
    with path.open("r", encoding="utf-8") as src, tmp.open("w", encoding="utf-8") as dst:
        for line in src:
            if not line.strip():
                continue
            if written >= line_count:
                break
            dst.write(line)
            written += 1
    os.replace(tmp, path)


def last_jsonl_record(path: Path) -> dict | None:
    last = None
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                last = line
    if last is None:
        return None
    return json.loads(last)


def append_jsonl(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("a", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")))
            handle.write("\n")


def publish_metadata_json(jsonl_path: Path, json_path: Path) -> int:
    tmp = json_path.with_name(f"{json_path.name}.tmp")
    count = 0
    with jsonl_path.open("r", encoding="utf-8") as src, tmp.open("w", encoding="utf-8") as dst:
        dst.write("[\n")
        first = True
        for line in src:
            line = line.strip()
            if not line:
                continue
            if not first:
                dst.write(",\n")
            dst.write(line)
            first = False
            count += 1
        dst.write("\n]\n")
    os.replace(tmp, json_path)
    return count


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build one local MSMARCO-XI language FAISS index.")
    parser.add_argument("--language", required=True, help="ISO 639-1 or MSMARCO-XI language code, e.g. hi or hin.")
    parser.add_argument("--dataset-path", type=Path, default=get_dataset_path(), help="Local MSMARCO-XI root.")
    parser.add_argument("--split", default=get_split(), choices=["train", "validation"], help="Dataset split to use.")
    parser.add_argument("--index-root", type=Path, default=get_index_root(), help="Root directory for retrieval indexes.")
    parser.add_argument("--batch-size", type=int, default=get_batch_size(), help="Embedding and Parquet batch size.")
    parser.add_argument("--max-records", type=int, default=None, help="Optional cap for verification builds.")
    parser.add_argument("--force", action="store_true", help="Rebuild even when COMPLETE exists.")
    parser.add_argument("--embedding-model", default=DEFAULT_EMBEDDING_MODEL, help="Embedding model for E5-compatible vectors.")
    parser.add_argument("--device", default="cpu", help="SentenceTransformer device.")
    parser.add_argument("--max-chars", type=int, default=400, help="sentence_aware_plain max characters per chunk.")
    parser.add_argument("--save-every-records", type=int, default=1000, help="Partial snapshot interval.")
    parser.add_argument("--benchmark-queries", type=int, default=20, help="Number of local queries for retrieval benchmark.")
    return parser.parse_args()


def read_checkpoint(index_dir: Path) -> dict:
    path = index_dir / CHECKPOINT_NAME
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def force_clean(index_dir: Path) -> None:
    for name in (
        "faiss_index.index",
        "faiss_index.json",
        "index_metadata.json",
        "benchmark.json",
        "benchmark_queries.json",
        "COMPLETE",
        CHECKPOINT_NAME,
        PARTIAL_INDEX_NAME,
        PARTIAL_METADATA_NAME,
    ):
        path = index_dir / name
        if path.exists():
            path.unlink()


def recover_resume_state(index_dir: Path) -> tuple[object | None, int, int, int]:
    partial_index_path = index_dir / PARTIAL_INDEX_NAME
    partial_metadata_path = index_dir / PARTIAL_METADATA_NAME
    checkpoint = read_checkpoint(index_dir)
    if not partial_index_path.exists() or not partial_metadata_path.exists():
        return None, 0, 0, 0

    index = faiss.read_index(str(partial_index_path))
    metadata_lines = count_jsonl_lines(partial_metadata_path)
    if metadata_lines > index.ntotal:
        truncate_jsonl_lines(partial_metadata_path, index.ntotal)
        metadata_lines = index.ntotal
    if metadata_lines < index.ntotal:
        raise RuntimeError(
            f"Unsafe partial index state in {index_dir}: index has {index.ntotal} vectors "
            f"but metadata has {metadata_lines} rows. Re-run with --force after inspecting the directory."
        )

    last = last_jsonl_record(partial_metadata_path)
    records_processed = int((last or {}).get("record_offset", -1)) + 1
    chunks_processed = metadata_lines
    checkpoint_vectors = int(checkpoint.get("vectors_created", checkpoint.get("vectors", 0)) or 0)
    if checkpoint_vectors and checkpoint_vectors != index.ntotal:
        print(f"[Resume] checkpoint vectors={checkpoint_vectors}, recovered vectors={index.ntotal}")
    return index, records_processed, chunks_processed, int(index.ntotal)


def iter_records(parquet_path: Path, batch_size: int, start_offset: int, stop_offset: int):
    pf = pq.ParquetFile(parquet_path)
    row_offset = 0
    for batch in pf.iter_batches(batch_size=batch_size):
        rows = batch.to_pylist()
        for row in rows:
            if row_offset >= stop_offset:
                return
            current = row_offset
            row_offset += 1
            if current < start_offset:
                continue
            yield current, row


def extract_rows(
    record: dict,
    record_offset: int,
    language: str,
    dataset_code: str,
    split: str,
    max_chars: int,
    passage_fields: list[str],
    query_fields: list[str],
    answer_fields: list[str],
    language_fields: list[str],
) -> tuple[list[str], list[dict], int]:
    passage_field = passage_fields[0] if passage_fields else None
    if passage_field is None:
        raise SchemaInferenceError("No passage/document text field was detected in this Parquet schema.")

    passage_texts = values_as_texts(get_nested_value(record, passage_field))
    translated_query = first_text(record, query_fields)
    answer = first_text(record, answer_fields)
    source_lang = first_text(record, [field for field in language_fields if "source" in field.lower()])
    target_lang = first_text(record, [field for field in language_fields if "target" in field.lower()])
    documents = []
    metadatas = []
    raw_query_id = record.get("query_id") or record.get("id") or record.get("_id")
    try:
        query_id = int(raw_query_id)
    except (TypeError, ValueError):
        query_id = int(record_offset)

    for passage_index, passage_text in enumerate(passage_texts):
        chunks = chunk_sentence_aware(str(passage_text), max_chars=max_chars)
        for chunk_index, chunk in enumerate(chunks):
            documents.append(chunk)
            metadatas.append(
                {
                    "text": chunk,
                    "language": dataset_code,
                    "target_language": language,
                    "source_language": source_lang,
                    "query_id": query_id,
                    "passage_index": int(passage_index),
                    "chunk_index": int(chunk_index),
                    "is_selected": None,
                    "query_type": record.get("query_type"),
                    "source_lang": source_lang,
                    "target_lang": target_lang,
                    "dataset": DATASET_NAME,
                    "split": split,
                    "record_id": query_id,
                    "record_offset": int(record_offset),
                    "query": translated_query,
                    "answer": answer,
                    "passage_field": passage_field,
                    "query_fields": query_fields,
                    "translated_text": chunk,
                }
            )
    return documents, metadatas, len(passage_texts)


def embed_and_add(indexer: VectorIndexer, index, documents: list[str], batch_size: int):
    if not documents:
        return index
    prefixed = [f"passage: {doc}" for doc in documents]
    embeddings = indexer.model.encode(
        prefixed,
        batch_size=batch_size,
        show_progress_bar=False,
        normalize_embeddings=True,
        convert_to_numpy=True,
    ).astype("float32")
    if index is None:
        index = faiss.IndexFlatIP(int(embeddings.shape[1]))
    index.add(embeddings)
    return index


def summarize_latency(values: list[float]) -> dict:
    if not values:
        return {"p50": None, "p70": None, "p100": None, "count": 0}
    return {
        "p50": round(float(np.percentile(values, 50)), 3),
        "p70": round(float(np.percentile(values, 70)), 3),
        "p100": round(float(np.percentile(values, 100)), 3),
        "count": len(values),
    }


def benchmark(index_dir: Path, embedding_model: str, device: str, queries: list[str]) -> dict:
    if not queries:
        return {"queries": 0, "error": "no benchmark queries collected"}
    indexer = VectorIndexer(model_name=embedding_model, device=device)
    indexer.load_index(str(index_dir))
    retriever = DenseRetriever(indexer)
    stages = {"query_embedding_ms": [], "faiss_search_ms": [], "metadata_lookup_ms": [], "total_retrieval_ms": []}
    for query in queries:
        _, latencies = retriever.retrieve(query, k=5)
        for stage in stages:
            stages[stage].append(float(latencies.get(stage, 0.0)))
    return {"queries": len(queries), "k": 5, "stages": {stage: summarize_latency(values) for stage, values in stages.items()}}


def main() -> None:
    args = parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    language = normalize_language_code(args.language)
    dataset_code = to_msmarco_xi_code(language)
    if dataset_code is None:
        print(f"[Error] Unsupported MSMARCO-XI language: {args.language}")
        sys.exit(1)

    index_dir = language_index_dir(language, args.index_root)
    assert index_dir is not None
    index_dir.mkdir(parents=True, exist_ok=True)

    if args.force:
        force_clean(index_dir)
    elif is_complete_index(index_dir):
        print(f"[Complete] {language}: existing complete index found at {index_dir}. Use --force to rebuild.")
        return

    try:
        parquet_info = find_language_file(args.dataset_path, language, args.split)
    except DatasetNotFoundError as exc:
        print(f"[Error] {exc}")
        sys.exit(1)
    except FileNotFoundError as exc:
        print(f"[Error] {exc}")
        sys.exit(1)

    if not parquet_info.passage_fields:
        print(
            "[Error] Could not detect an indexable passage/document text field in "
            f"{parquet_info.path}. Run python -m ingestion.inspect_msmarco_xi for schema details."
        )
        sys.exit(1)
    parquet_path = parquet_info.path

    pf = pq.ParquetFile(parquet_path)
    total_rows = int(pf.metadata.num_rows)
    target_rows = min(total_rows, int(args.max_records)) if args.max_records is not None else total_rows

    print("=" * 72)
    print("MSMARCO-XI LOCAL LANGUAGE INDEX BUILD")
    print("=" * 72)
    print(f"Language:        {language} ({dataset_code})")
    print(f"Dataset path:    {args.dataset_path}")
    print(f"Parquet file:    {parquet_path}")
    print(f"Split:           {args.split}")
    print(f"Rows available:  {total_rows}")
    print(f"Rows to process: {target_rows}")
    print(f"Index dir:       {index_dir}")
    print(f"Batch size:      {args.batch_size}")
    print("=" * 72)

    index, records_processed, chunks_processed, vectors = recover_resume_state(index_dir)
    if records_processed:
        print(f"[Resume] {language}: records_processed={records_processed}, vectors={vectors}")
    if records_processed >= target_rows and index is None:
        print("[Error] Checkpoint says target was reached, but no partial index exists.")
        sys.exit(1)

    partial_index_path = index_dir / PARTIAL_INDEX_NAME
    partial_metadata_path = index_dir / PARTIAL_METADATA_NAME
    checkpoint_path = index_dir / CHECKPOINT_NAME

    indexer = VectorIndexer(model_name=args.embedding_model, device=args.device)
    start_time = time.time()
    records_since_snapshot = 0
    passages_processed = int(read_checkpoint(index_dir).get("passages_processed", 0) or 0)
    benchmark_queries = []

    pending_docs: list[str] = []
    pending_meta: list[dict] = []

    def flush_pending(record_offset: int | None = None) -> None:
        nonlocal index, chunks_processed, vectors, pending_docs, pending_meta
        if not pending_docs:
            return
        index = embed_and_add(indexer, index, pending_docs, args.batch_size)
        append_jsonl(partial_metadata_path, pending_meta)
        chunks_processed += len(pending_docs)
        vectors = int(index.ntotal)
        pending_docs = []
        pending_meta = []
        if record_offset is not None:
            write_faiss_atomic(index, partial_index_path)
            atomic_write_json(
                checkpoint_path,
                {
                    "language": language,
                    "dataset_code": dataset_code,
                    "dataset_path": str(args.dataset_path),
                    "dataset_file": str(parquet_path),
                    "split": args.split,
                    "source_file": str(parquet_path),
                    "records_available": total_rows,
                    "records_target": target_rows,
                    "records_processed": int(record_offset) + 1,
                    "passages_processed": passages_processed,
                    "chunks_created": chunks_processed,
                    "vectors_created": vectors,
                    "batch_number": int((record_offset + 1) / max(1, args.batch_size)),
                    "embedding_model": args.embedding_model,
                    "status": "IN_PROGRESS",
                    "updated_at": utc_now(),
                },
            )

    for record_offset, record in iter_records(parquet_path, args.batch_size, records_processed, target_rows):
        documents, metadatas, passage_count = extract_rows(
            record,
            record_offset,
            language,
            dataset_code,
            args.split,
            args.max_chars,
            parquet_info.passage_fields,
            parquet_info.query_fields,
            parquet_info.answer_fields,
            parquet_info.language_fields,
        )
        pending_docs.extend(documents)
        pending_meta.extend(metadatas)
        passages_processed += passage_count
        records_processed = record_offset + 1
        records_since_snapshot += 1

        query_text = first_text(record, parquet_info.query_fields)
        if len(benchmark_queries) < args.benchmark_queries and query_text:
            benchmark_queries.append(query_text)

        if len(pending_docs) >= args.batch_size:
            flush_pending()

        if records_since_snapshot >= max(1, args.save_every_records):
            flush_pending(record_offset=record_offset)
            records_since_snapshot = 0
            print(f"[Checkpoint] records={records_processed}/{target_rows} vectors={vectors}")

    flush_pending(record_offset=max(records_processed - 1, 0))

    if index is None or index.ntotal == 0:
        print("[Error] No vectors were produced.")
        sys.exit(1)

    final_index_path = index_dir / "faiss_index.index"
    final_metadata_path = index_dir / "faiss_index.json"
    write_faiss_atomic(index, final_index_path)
    metadata_rows = publish_metadata_json(partial_metadata_path, final_metadata_path)
    if metadata_rows != index.ntotal:
        print(f"[Error] Final metadata rows ({metadata_rows}) != FAISS vectors ({index.ntotal}).")
        sys.exit(1)

    benchmark_path = index_dir / "benchmark.json"
    benchmark_queries_path = index_dir / "benchmark_queries.json"
    atomic_write_text(benchmark_queries_path, json.dumps(benchmark_queries, ensure_ascii=False, indent=2))
    latency_report = benchmark(index_dir, args.embedding_model, args.device, benchmark_queries)
    atomic_write_json(benchmark_path, latency_report)

    elapsed = time.time() - start_time
    metadata = {
        "language": language,
        "dataset_code": dataset_code,
        "dataset": DATASET_NAME,
        "dataset_path": str(args.dataset_path),
        "dataset_split": args.split,
        "dataset_file": str(parquet_path),
        "source_file": str(parquet_path),
        "embedding_model": args.embedding_model,
        "chunking_strategy": "sentence_aware_plain",
        "chunk_max_chars": args.max_chars,
        "vector_dimension": int(index.d),
        "records_available": total_rows,
        "records_processed": records_processed,
        "passages_processed": passages_processed,
        "number_of_chunks": chunks_processed,
        "number_of_vectors": int(index.ntotal),
        "created_at": utc_now(),
        "completed": True,
        "status": "COMPLETE",
        "build_seconds": round(elapsed, 3),
        "benchmark": latency_report,
        "schema_fields": {
            "columns": parquet_info.columns,
            "query_fields": parquet_info.query_fields,
            "passage_fields": parquet_info.passage_fields,
            "answer_fields": parquet_info.answer_fields,
            "language_fields": parquet_info.language_fields,
        },
    }
    atomic_write_json(index_dir / "index_metadata.json", metadata)
    atomic_write_json(
        checkpoint_path,
        {
            **metadata,
            "records_target": target_rows,
            "records_processed": records_processed,
            "chunks_created": chunks_processed,
            "vectors_created": int(index.ntotal),
            "batch_number": int(records_processed / max(1, args.batch_size)),
            "status": "COMPLETE",
            "updated_at": utc_now(),
        },
    )
    atomic_write_text(index_dir / "COMPLETE", f"completed_at={utc_now()}\n")

    print("=" * 72)
    print("COMPLETE")
    print("=" * 72)
    print(f"Index:      {final_index_path}")
    print(f"Metadata:   {final_metadata_path}")
    print(f"Vectors:    {index.ntotal}")
    print(f"Build sec:  {elapsed:.2f}")
    print("Benchmark:")
    print(json.dumps(latency_report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
