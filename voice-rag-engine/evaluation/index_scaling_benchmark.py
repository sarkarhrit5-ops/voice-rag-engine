import argparse
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from huggingface_hub import hf_hub_download

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from retrieval.chunking import chunk_sentence_aware
from retrieval.indexer import VectorIndexer
from retrieval.retriever import DenseRetriever


def parse_args():
    parser = argparse.ArgumentParser(description="Benchmark index construction and retrieval latency for the sentence_aware_plain strategy.")
    parser.add_argument("--samples", type=int, default=5000, help="Number of Hindi validation queries to sample")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--target_docs", type=int, default=50000, help="Target number of chunks in the index")
    parser.add_argument("--output_json", type=str, default="evaluation/index_scaling_benchmark.json", help="JSON output path")
    parser.add_argument("--output_md", type=str, default="evaluation/index_scaling_benchmark.md", help="Markdown output path")
    parser.add_argument("--index_dir", type=str, default="retrieval/indexes/scaling_sentence_aware_plain", help="Directory to store the benchmark index")
    parser.add_argument("--latency_queries", type=int, default=500, help="How many queries to sample for latency percentiles")
    return parser.parse_args()


def load_sample(samples: int, seed: int) -> pd.DataFrame:
    repo_id = "ai4bharat/MSMARCO-XI"
    filename = "validation/hinval.parquet"
    local_path = hf_hub_download(repo_id=repo_id, filename=filename, repo_type="dataset")
    df = pd.read_parquet(local_path)
    return df.sample(n=min(samples, len(df)), random_state=seed).copy()


def build_documents(sample_df: pd.DataFrame, target_docs: int):
    documents = []
    metadata = []
    seen = 0
    for _, row in sample_df.iterrows():
        passages = row.get("passages")
        if not isinstance(passages, dict):
            continue
        english_passages = passages.get("English_passages", [])
        is_selected = passages.get("is_selected", [])
        for p_idx, (passage_text, selected_flag) in enumerate(zip(english_passages, is_selected)):
            chunks = chunk_sentence_aware(passage_text, max_chars=400)
            for c_idx, chunk in enumerate(chunks):
                if len(documents) >= target_docs:
                    return documents, metadata
                documents.append(chunk)
                metadata.append({
                    "query_id": int(row["query_id"]),
                    "passage_index": int(p_idx),
                    "chunk_index": int(c_idx),
                    "is_selected": int(selected_flag),
                    "language": "eng",
                    "text": chunk,
                })
                seen += 1
    return documents, metadata


def summarize_latency(values):
    if not values:
        return {"p50": None, "p70": None, "p100": None}
    return {
        "p50": float(np.percentile(values, 50)),
        "p70": float(np.percentile(values, 70)),
        "p100": float(np.percentile(values, 100)),
    }


def main():
    args = parse_args()
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    sample_df = load_sample(args.samples, args.seed)
    print(f"Loaded {len(sample_df)} Hindi validation rows")

    t_chunk_start = time.time()
    documents, metadata = build_documents(sample_df, args.target_docs)
    chunking_time = time.time() - t_chunk_start
    print(f"Built {len(documents)} documents in {chunking_time:.2f}s")

    indexer = VectorIndexer(model_name="intfloat/multilingual-e5-small", device="cpu")
    t_build_start = time.time()
    build_stats = indexer.build_index(documents, metadata, batch_size=128, show_progress_bar=False)
    t_build_end = time.time()
    build_total = t_build_end - t_build_start

    index_dir = Path(args.index_dir)
    index_dir.mkdir(parents=True, exist_ok=True)
    save_stats = indexer.save_index(str(index_dir))

    index_file = Path(save_stats["index_path"])
    metadata_file = Path(save_stats["metadata_path"])
    size_bytes = index_file.stat().st_size + metadata_file.stat().st_size

    retriever = DenseRetriever(indexer)
    latency_sample = sample_df.sample(n=min(args.latency_queries, len(sample_df)), random_state=args.seed).to_dict("records")
    query_embedding = []
    faiss_search = []
    retrieval_total = []

    for row in latency_sample:
        query = row["query"]
        results, lat = retriever.retrieve(query, k=10)
        query_embedding.append(lat["query_embedding_ms"])
        faiss_search.append(lat["faiss_search_ms"])
        retrieval_total.append(lat["total_retrieval_ms"])

    latency_summary = {
        "query_embedding_ms": summarize_latency(query_embedding),
        "faiss_search_ms": summarize_latency(faiss_search),
        "retrieval_total_ms": summarize_latency(retrieval_total),
    }

    result = {
        "sample_size_queries": int(len(sample_df)),
        "target_document_count": int(args.target_docs),
        "actual_document_count": int(len(documents)),
        "chunking_time_sec": float(chunking_time),
        "embedding_time_sec": float(build_stats["embedding_time_sec"]),
        "faiss_build_time_sec": float(build_stats["faiss_build_time_sec"]),
        "index_save_time_sec": float(save_stats["save_time_sec"]),
        "index_size_bytes": int(size_bytes),
        "index_size_mb": float(size_bytes / (1024 * 1024)),
        "vector_dimension": int(build_stats["vector_dimension"]),
        "index_build_total_sec": float(build_total),
        "query_latency_ms": latency_summary,
    }

    json_path = Path(args.output_json)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    md_lines = [
        "# Index scaling benchmark",
        "",
        f"- Sampled Hindi validation queries: {result['sample_size_queries']}",
        f"- Indexed chunks: {result['actual_document_count']}",
        f"- Index size on disk: {result['index_size_mb']:.2f} MB",
        f"- Chunking time: {result['chunking_time_sec']:.2f}s",
        f"- Embedding time: {result['embedding_time_sec']:.2f}s",
        f"- FAISS build time: {result['faiss_build_time_sec']:.2f}s",
        "",
        "## Retrieval latency percentiles (ms)",
        "",
        "| stage | P50 | P70 | P100 |",
        "| --- | ---: | ---: | ---: |",
        f"| query_embedding_ms | {latency_summary['query_embedding_ms']['p50']:.2f} | {latency_summary['query_embedding_ms']['p70']:.2f} | {latency_summary['query_embedding_ms']['p100']:.2f} |",
        f"| faiss_search_ms | {latency_summary['faiss_search_ms']['p50']:.2f} | {latency_summary['faiss_search_ms']['p70']:.2f} | {latency_summary['faiss_search_ms']['p100']:.2f} |",
        f"| retrieval_total_ms | {latency_summary['retrieval_total_ms']['p50']:.2f} | {latency_summary['retrieval_total_ms']['p70']:.2f} | {latency_summary['retrieval_total_ms']['p100']:.2f} |",
    ]
    Path(args.output_md).write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    print(json.dumps({
        "sample_size_queries": result["sample_size_queries"],
        "actual_document_count": result["actual_document_count"],
        "index_size_mb": result["index_size_mb"],
        "query_embedding_ms": result["query_latency_ms"]["query_embedding_ms"],
        "faiss_search_ms": result["query_latency_ms"]["faiss_search_ms"],
        "retrieval_total_ms": result["query_latency_ms"]["retrieval_total_ms"],
    }, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
