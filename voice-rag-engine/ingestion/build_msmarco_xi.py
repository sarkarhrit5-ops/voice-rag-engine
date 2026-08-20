"""
Controlled multilingual index builder for ``ai4bharat/MSMARCO-XI``.

Builds a single FAISS multilingual index over representative subsets of
Indic-language passages without ever downloading the full ~55 GB dataset.
Hugging Face ``datasets`` streaming is used so only the consumed subset is
fetched from the Hub.

The process is bounded and restartable:

* each language is capped at ``--max-records-per-language`` records
  (default ``50000``, overridable via ``MSMARCO_XI_MAX_RECORDS_PER_LANGUAGE``);
* per-language checkpoints are written to ``<output>/checkpoints/`` so a run
  interrupted mid-way can continue with ``--resume`` without re-streaming
  languages that already completed.

Example:

    python -m ingestion.build_msmarco_xi \\
        --languages hi,bn,ta,te,mr,gu \\
        --max-records-per-language 200 \\
        --benchmark-queries 100

The existing English index (``retrieval/indexes/eng_sentence_aware_plain``) is
never touched.
"""

import argparse
import itertools
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

from datasets import load_dataset

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from retrieval.chunking import chunk_sentence_aware
from retrieval.indexer import VectorIndexer
from retrieval.languages import (
    DEFAULT_LANGUAGES,
    ISO_639_1_TO_MSMARCO_XI,
    SPLIT_FILE_SUFFIX,
    normalize_language_code,
    to_msmarco_xi_code,
)

REPO_ID = "ai4bharat/MSMARCO-XI"
DEFAULT_EMBEDDING_MODEL = "intfloat/multilingual-e5-small"
DEFAULT_OUTPUT_INDEX = "retrieval/indexes/msmarco_xi_multilingual"
DEFAULT_SPLIT = "validation"
DEFAULT_MAX_RECORDS_PER_LANGUAGE = 50000

CHECKPOINT_COLUMNS = [
    "text",
    "query_id",
    "passage_index",
    "chunk_index",
    "is_selected",
    "query_type",
    "language",
    "target_lang",
    "source_lang",
    "dataset",
    "record_id",
    "meta_json",
]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Build a bounded multilingual FAISS index from MSMARCO-XI subsets."
    )
    parser.add_argument(
        "--languages",
        type=str,
        default=os.getenv("MSMARCO_XI_LANGUAGES", ",".join(DEFAULT_LANGUAGES)),
        help="Comma-separated ISO 639-1 language codes to index (default: hi,bn,ta,te,mr,gu).",
    )
    parser.add_argument(
        "--max-records-per-language",
        type=int,
        default=int(os.getenv("MSMARCO_XI_MAX_RECORDS_PER_LANGUAGE", DEFAULT_MAX_RECORDS_PER_LANGUAGE)),
        help="Maximum number of dataset records consumed per language.",
    )
    parser.add_argument(
        "--split",
        type=str,
        default=os.getenv("MSMARCO_XI_SPLIT", DEFAULT_SPLIT),
        choices=["validation", "train"],
        help="Dataset split to stream from (default: validation).",
    )
    parser.add_argument(
        "--output-index",
        type=str,
        default=os.getenv("MSMARCO_XI_OUTPUT_INDEX", DEFAULT_OUTPUT_INDEX),
        help="Directory where the FAISS index + metadata are written.",
    )
    parser.add_argument(
        "--index-name",
        type=str,
        default="faiss_index",
        help="Index file stem used by VectorIndexer (default: faiss_index).",
    )
    parser.add_argument(
        "--embedding-model",
        type=str,
        default=DEFAULT_EMBEDDING_MODEL,
        help="Embedding model (must be compatible with the existing retriever).",
    )
    parser.add_argument(
        "--device",
        type=str,
        default="cpu",
        help="Device for the embedding model (cpu or cuda).",
    )
    parser.add_argument(
        "--max-chars",
        type=int,
        default=400,
        help="Sentence-aware chunking character budget.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=128,
        help="Embedding batch size.",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Skip languages that already have a non-empty checkpoint.",
    )
    parser.add_argument(
        "--benchmark-queries",
        type=int,
        default=int(os.getenv("MSMARCO_XI_BENCHMARK_QUERIES", 100)),
        help="Number of queries per language to retain for the latency benchmark (0 disables).",
    )
    parser.add_argument(
        "--benchmark-only",
        action="store_true",
        help="Skip the build and benchmark an already-built index.",
    )
    parser.add_argument(
        "--benchmark-output",
        type=str,
        default="evaluation/multilingual_retrieval_benchmark.json",
        help="Path for the retrieval latency benchmark JSON report.",
    )
    return parser.parse_args()


def stream_records(dataset_code: str, split: str, max_records: int):
    """
    Stream up to ``max_records`` records for a single MSMARCO-XI language
    directly from the Hub.

    Only the consumed subset is fetched thanks to ``streaming=True``.
    """
    suffix = SPLIT_FILE_SUFFIX.get(split, "val")
    data_file = f"{split}/{dataset_code}{suffix}.parquet"
    print(f"[Streaming] {dataset_code}: {data_file} (max {max_records} records)")
    ds = load_dataset(REPO_ID, data_files=data_file, streaming=True)
    split_name = list(ds.keys())[0]
    for record in itertools.islice(ds[split_name], max_records):
        yield record


def extract_passage_rows(record: dict, dataset_code: str, max_chars: int) -> tuple[list[dict], int]:
    """
    Convert one dataset record into (chunked passage rows, passage count).

    Each row is a metadata dict identical to the existing index contract plus
    MSMARCO-XI dataset metadata (target/source language, translation params).
    """
    passages = record.get("passages")
    if not isinstance(passages, dict):
        return [], 0
    translated = passages.get("Translated_passages", []) or []
    is_selected = passages.get("is_selected", []) or []
    record_id = int(record.get("query_id", -1))
    query_type = record.get("query_type")
    rows = []
    for p_idx, (passage_text, selected_flag) in enumerate(zip(translated, is_selected)):
        chunks = chunk_sentence_aware(passage_text, max_chars=max_chars)
        for c_idx, chunk in enumerate(chunks):
            rows.append(
                {
                    "text": chunk,
                    "query_id": record_id,
                    "passage_index": int(p_idx),
                    "chunk_index": int(c_idx),
                    "is_selected": int(selected_flag),
                    "query_type": query_type,
                    "language": dataset_code,
                    "target_lang": record.get("target_lang"),
                    "source_lang": record.get("source_lang"),
                    "dataset": REPO_ID,
                    "record_id": record_id,
                    "meta_json": json.dumps(record.get("meta"), ensure_ascii=False, default=str),
                }
            )
    return rows, len(translated)


def process_language(lang: str, args, output_dir: Path) -> dict:
    """Stream, chunk and checkpoint one language. Returns its stats dict."""
    dataset_code = to_msmarco_xi_code(lang)
    if dataset_code is None:
        print(f"[Skip] Unsupported language code '{lang}' (not part of MSMARCO-XI).")
        return None

    checkpoint_dir = output_dir / "checkpoints"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_path = checkpoint_dir / f"{dataset_code}.parquet"

    if args.resume and checkpoint_path.exists() and checkpoint_path.stat().st_size > 0:
        print(f"[Resume] {dataset_code}: reusing existing checkpoint {checkpoint_path.name}")
        existing = pd.read_parquet(checkpoint_path)
        return {
            "language": lang,
            "dataset_code": dataset_code,
            "records_processed": int(existing["records_processed"].iloc[0]),
            "passages_processed": int(existing["passages_processed"].iloc[0]),
            "records_indexed": int(existing.shape[0]),
            "checkpoint": str(checkpoint_path),
        }

    rows = []
    queries = []
    records_processed = 0
    passages_processed = 0

    for record in stream_records(dataset_code, args.split, args.max_records_per_language):
        records_processed += 1
        passage_rows, passage_count = extract_passage_rows(record, dataset_code, args.max_chars)
        rows.extend(passage_rows)
        passages_processed += passage_count
        if args.benchmark_queries > 0 and len(queries) < args.benchmark_queries:
            query_text = record.get("query")
            if query_text:
                queries.append({"language": lang, "query": query_text, "query_id": int(record.get("query_id", -1))})

    df = pd.DataFrame(rows, columns=CHECKPOINT_COLUMNS)
    # Persist record/streaming stats alongside the rows for accurate resume reports.
    df = df.assign(records_processed=records_processed, passages_processed=passages_processed)
    df.to_parquet(checkpoint_path, index=False)

    if queries:
        queries_path = checkpoint_dir / f"{dataset_code}_queries.json"
        queries_path.write_text(json.dumps(queries, ensure_ascii=False, indent=2), encoding="utf-8")

    stats = {
        "language": lang,
        "dataset_code": dataset_code,
        "records_processed": records_processed,
        "passages_processed": passages_processed,
        "records_indexed": int(len(rows)),
        "checkpoint": str(checkpoint_path),
    }
    print(
        f"[Done] {lang} ({dataset_code}): records_processed={records_processed} "
        f"passages_processed={passages_processed} records_indexed={stats['records_indexed']}"
    )
    return stats


def load_checkpoints(output_dir: Path) -> tuple[list[str], list[dict]]:
    """Load all per-language checkpoints into (documents, metadata) lists."""
    checkpoint_dir = output_dir / "checkpoints"
    documents = []
    metadatas = []
    for checkpoint in sorted(checkpoint_dir.glob("*.parquet")):
        df = pd.read_parquet(checkpoint, columns=CHECKPOINT_COLUMNS)
        meta_list = []
        for raw in df["meta_json"]:
            if isinstance(raw, str):
                try:
                    meta_list.append(json.loads(raw))
                except ValueError:
                    meta_list.append({})
            else:
                meta_list.append(raw or {})
        for text, query_id, p_idx, c_idx, sel, qtype, lang, tlang, slang, dataset, rid, meta in zip(
            df["text"],
            df["query_id"],
            df["passage_index"],
            df["chunk_index"],
            df["is_selected"],
            df["query_type"],
            df["language"],
            df["target_lang"],
            df["source_lang"],
            df["dataset"],
            df["record_id"],
            meta_list,
        ):
            documents.append(str(text))
            metadatas.append(
                {
                    "query_id": int(query_id),
                    "passage_index": int(p_idx),
                    "chunk_index": int(c_idx),
                    "is_selected": int(sel),
                    "query_type": qtype,
                    "language": lang,
                    "target_lang": tlang,
                    "source_lang": slang,
                    "dataset": dataset,
                    "record_id": int(rid),
                    "meta": meta,
                    "text": str(text),
                }
            )
    return documents, metadatas


def load_benchmark_queries(output_dir: Path, benchmark_queries: int) -> list[dict]:
    """
    Collect benchmark queries stratified across languages.

    The total is capped at ``benchmark_queries``; each language contributes an
    equal share so the latency report covers every indexed language.
    """
    checkpoint_dir = output_dir / "checkpoints"
    per_language = {}
    for query_path in sorted(checkpoint_dir.glob("*_queries.json")):
        lang = query_path.name.replace("_queries.json", "")
        try:
            per_language[lang] = json.loads(query_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
    if not per_language:
        return []
    per_lang_budget = max(1, benchmark_queries // len(per_language))
    queries = []
    for lang, items in sorted(per_language.items()):
        queries.extend(items[:per_lang_budget])
    return queries[:benchmark_queries]


def summarize_latency(values) -> dict:
    if not values:
        return {"p50": None, "p70": None, "p100": None, "count": 0}
    return {
        "p50": round(float(np.percentile(values, 50)), 3),
        "p70": round(float(np.percentile(values, 70)), 3),
        "p100": round(float(np.percentile(values, 100)), 3),
        "count": len(values),
    }


def run_benchmark(indexer: VectorIndexer, queries: list[dict], k: int = 10) -> dict:
    """Measure retrieval latency on the freshly built multilingual index."""
    from retrieval.multilingual_retriever import MultilingualRetriever

    if not queries:
        return {"error": "no benchmark queries available", "queries": 0}

    retriever = MultilingualRetriever(indexer)
    stages = {"query_embedding_ms": [], "faiss_search_ms": [], "metadata_lookup_ms": [], "total_retrieval_ms": []}
    language_hits = {}

    for entry in queries:
        query_text = entry["query"]
        lang = entry["language"]
        results, latencies = retriever.retrieve(query_text, k=k, language=lang)
        for stage in stages:
            stages[stage].append(float(latencies.get(stage, 0.0)))
        language_hits[lang] = language_hits.get(lang, 0) + 1

    return {
        "queries": len(queries),
        "k": k,
        "languages_covered": {lang: count for lang, count in language_hits.items()},
        "stages": {stage: summarize_latency(values) for stage, values in stages.items()},
    }


def main():
    args = parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    languages = [normalize_language_code(l) for l in args.languages.split(",") if normalize_language_code(l)]
    unsupported = [l for l in languages if l not in ISO_639_1_TO_MSMARCO_XI]
    if unsupported:
        print(f"[Error] Unsupported language codes: {unsupported}")
        sys.exit(1)

    print("=" * 64)
    print("        MSMARCO-XI CONTROLLED MULTILINGUAL INDEX BUILD")
    print("=" * 64)
    print(f"  Languages:            {languages}")
    print(f"  Split:                {args.split}")
    print(f"  Max records/language: {args.max_records_per_language}")
    print(f"  Output index:         {args.output_index}")
    print(f"  Embedding model:      {args.embedding_model}")
    print("=" * 64)

    output_dir = Path(args.output_index)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.benchmark_only:
        index_path = output_dir / f"{args.index_name}.index"
        if not index_path.exists():
            print(f"[Error] No existing index at {index_path}. Run the full build first.")
            sys.exit(1)
        indexer = VectorIndexer(model_name=args.embedding_model, device=args.device)
        indexer.load_index(str(output_dir), index_name=args.index_name)
        benchmark_queries = load_benchmark_queries(output_dir, args.benchmark_queries)
        print(f"Running retrieval latency benchmark on {len(benchmark_queries)} queries...")
        benchmark = run_benchmark(indexer, benchmark_queries)
        benchmark_path = Path(args.benchmark_output)
        benchmark_path.parent.mkdir(parents=True, exist_ok=True)
        benchmark_path.write_text(json.dumps(benchmark, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Benchmark report written to {benchmark_path}")
        print(json.dumps(benchmark, ensure_ascii=False, indent=2))
        return

    total_start = time.time()
    per_language = {}
    for lang in languages:
        stats = process_language(lang, args, output_dir)
        if stats is not None:
            per_language[lang] = stats

    if not per_language:
        print("[Error] No languages produced any data.")
        sys.exit(1)

    t_chunk_start = time.time()
    documents, metadatas = load_checkpoints(output_dir)
    chunking_time = time.time() - t_chunk_start
    print(f"Loaded {len(documents)} indexed documents from checkpoints in {chunking_time:.2f}s")

    if not documents:
        print("[Error] No documents collected. Nothing to index.")
        sys.exit(1)

    indexer = VectorIndexer(model_name=args.embedding_model, device=args.device)
    build_stats = indexer.build_index(documents, metadatas, batch_size=args.batch_size, show_progress_bar=False)
    save_stats = indexer.save_index(str(output_dir), index_name=args.index_name)

    index_file = Path(save_stats["index_path"])
    metadata_file = Path(save_stats["metadata_path"])
    index_size_bytes = index_file.stat().st_size + metadata_file.stat().st_size
    total_time = time.time() - total_start

    print("=" * 64)
    print("INDEX BUILD REPORT")
    print("=" * 64)
    for lang, stats in per_language.items():
        print(
            f"  {lang:<4} -> records_processed={stats['records_processed']} "
            f"records_indexed={stats['records_indexed']}"
        )
    print(f"  Embedding time:        {build_stats['embedding_time_sec']:.2f}s")
    print(f"  FAISS build time:      {build_stats['faiss_build_time_sec']:.2f}s")
    print(f"  Index save time:       {save_stats['save_time_sec']:.2f}s")
    print(f"  Total build time:      {total_time:.2f}s")
    print(f"  Final index size:      {index_size_bytes / (1024 * 1024):.2f} MB")
    print(f"  Vectors:               {indexer.index.ntotal}")
    print("=" * 64)

    report = {
        "dataset": REPO_ID,
        "split": args.split,
        "embedding_model": args.embedding_model,
        "languages": {lang: {"records_processed": s["records_processed"], "records_indexed": s["records_indexed"]} for lang, s in per_language.items()},
        "totals": {
            "records_processed": sum(s["records_processed"] for s in per_language.values()),
            "records_indexed": sum(s["records_indexed"] for s in per_language.values()),
        },
        "timing": {
            "chunking_time_sec": round(chunking_time, 3),
            "embedding_time_sec": round(build_stats["embedding_time_sec"], 3),
            "faiss_build_time_sec": round(build_stats["faiss_build_time_sec"], 3),
            "index_save_time_sec": round(save_stats["save_time_sec"], 3),
            "total_time_sec": round(total_time, 3),
        },
        "index": {
            "path": str(output_dir),
            "index_size_bytes": int(index_size_bytes),
            "index_size_mb": round(index_size_bytes / (1024 * 1024), 2),
            "num_vectors": int(indexer.index.ntotal),
            "vector_dimension": int(build_stats["vector_dimension"]),
        },
    }

    report_path = output_dir / "build_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Build report written to {report_path}")

    if args.benchmark_queries > 0:
        benchmark_queries = load_benchmark_queries(output_dir, args.benchmark_queries)
        print(f"Running retrieval latency benchmark on {len(benchmark_queries)} queries...")
        benchmark = run_benchmark(indexer, benchmark_queries)
        benchmark["index"] = report["index"]
        benchmark_path = Path(args.benchmark_output)
        benchmark_path.parent.mkdir(parents=True, exist_ok=True)
        benchmark_path.write_text(json.dumps(benchmark, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Benchmark report written to {benchmark_path}")
        print(json.dumps(benchmark, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()