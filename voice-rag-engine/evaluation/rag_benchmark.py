# Evaluation script for the RAG pipeline on MSMARCO-XI Hindi validation subset

import os
import sys
import json
import time
import argparse
import numpy as np
import pandas as pd
from huggingface_hub import hf_hub_download

# Inject local pkg path and root path
pkg_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'pkg'))
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if pkg_path not in sys.path:
    sys.path.insert(0, pkg_path)
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from rag.pipeline import TextRAGPipeline
from rag.prompts import get_refusal_response

def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate the Text RAG pipeline on MSMARCO-XI.")
    parser.add_argument("--samples", type=int, default=100, help="Number of queries to evaluate (default: 100)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for sampling (default: 42)")
    parser.add_argument("--min_score", type=float, default=0.70, help="Minimum retrieval confidence score threshold")
    parser.add_argument("--top_k", type=int, default=5, help="Number of passages to retrieve (default: 5)")
    parser.add_argument("--index_dir", type=str, default="retrieval/indexes/eng_sentence_aware_plain", help="Path to index directory")
    return parser.parse_args()

def is_translation_loop(text: str) -> bool:
    """
    Detects repeating word loops (NMT translation errors) in the dataset.
    """
    if not isinstance(text, str):
        return False
    words = text.split()
    if len(words) > 15:
        # Check unique word ratio
        ratio = len(set(words)) / len(words)
        if ratio < 0.35:
            return True
    return False

def main():
    args = parse_args()
    
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        
    print("=" * 70)
    print("           MSMARCO-XI TEXT RAG BENCHMARKING FRAMEWORK")
    print("=" * 70)
    print(f"Index:             {args.index_dir}")
    print(f"Samples count:     {args.samples}")
    print(f"Seed:              {args.seed}")
    print(f"Threshold:         {args.min_score}")
    print(f"Top-K:             {args.top_k}")
    print("-" * 70)

    # 1. Load Dataset
    repo_id = "ai4bharat/MSMARCO-XI"
    filename = "validation/hinval.parquet"
    print("Downloading and loading validation dataset...")
    try:
        local_path = hf_hub_download(repo_id=repo_id, filename=filename, repo_type="dataset")
        df = pd.read_parquet(local_path)
        print(f"Dataset loaded. Total records: {len(df)}")
    except Exception as e:
        print(f"[ERROR] Failed to load dataset: {e}")
        sys.exit(1)

    # 2. Sample and Categorize
    print(f"Sampling {args.samples} records with seed {args.seed}...")
    sample_df = df.sample(n=min(args.samples, len(df)), random_state=args.seed).copy()
    
    # Identify groups
    # Group 3: Translation-noise cases (translation loop in query or answer)
    sample_df['is_noise'] = sample_df.apply(lambda r: is_translation_loop(r['query']) or is_translation_loop(r['Answer']), axis=1)
    
    # Group 1 and Group 2 (non-noise)
    sample_df['num_selected'] = sample_df['passages'].apply(lambda p: sum(p.get('is_selected', [])) if isinstance(p, dict) else 0)
    
    group3_df = sample_df[sample_df['is_noise'] == True].copy()
    non_noise_df = sample_df[sample_df['is_noise'] == False].copy()
    
    group1_df = non_noise_df[non_noise_df['num_selected'] > 0].copy()
    group2_df = non_noise_df[non_noise_df['num_selected'] == 0].copy()
    
    print(f"Categorization:")
    print(f"  - Group 1 (Answerable):   {len(group1_df)} ({len(group1_df)/len(sample_df)*100:.1f}%)")
    print(f"  - Group 2 (No-Answer):    {len(group2_df)} ({len(group2_df)/len(sample_df)*100:.1f}%)")
    print(f"  - Group 3 (Transl. Noise): {len(group3_df)} ({len(group3_df)/len(sample_df)*100:.1f}%)")
    print("-" * 70)

    # 3. Initialize Pipeline
    print("Initializing Text RAG Pipeline...")
    pipeline = TextRAGPipeline(
        index_dir=args.index_dir,
        model_name="intfloat/multilingual-e5-small",
        device="cpu"
    )
    print("Pipeline ready.")

    # 4. Evaluation Loop
    log_file_path = "evaluation/rag_benchmark_logs.jsonl"
    log_file = open(log_file_path, "w", encoding="utf-8")
    
    # Metric accumulators
    retrieval_recalls_5 = []
    retrieval_recalls_10 = []
    retrieval_mrrs = []
    
    g1_refused = 0
    g1_grounded = 0
    
    g2_refused = 0
    g2_hallucinated = 0
    
    g3_refused = 0
    
    # Latency lists
    latencies = {
        "query_embedding": [],
        "faiss_search": [],
        "context_construction": [],
        "llm_request": [],
        "total": []
    }
    
    records = sample_df.to_dict('records')
    print("\nRunning RAG Pipeline evaluation...")
    
    for idx, row in enumerate(records):
        query_id = int(row['query_id'])
        query_text = row['query']
        eng_query = row['Eng_Query']
        gt_answer = row['Answer']
        
        # Determine actual classification group for logging
        if row['is_noise']:
            group_label = "Group 3 (Noise)"
        elif row['num_selected'] > 0:
            group_label = "Group 1 (Answerable)"
        else:
            group_label = "Group 2 (No-Answer)"
            
        print(f"[{idx+1}/{len(records)}] Evaluating ID: {query_id} ({group_label})...")
        
        # Execute RAG
        t_start = time.time()
        res = pipeline.answer(
            query=query_text,
            language="hi",
            top_k=args.top_k,
            min_score=args.min_score,
            query_id=query_id
        )
        t_end = time.time()
        
        # Record pipeline execution latencies
        lat = res["latency_ms"]
        latencies["query_embedding"].append(lat["query_embedding_ms"])
        latencies["faiss_search"].append(lat["faiss_search_ms"])
        latencies["context_construction"].append(lat["context_construction_ms"])
        latencies["llm_request"].append(lat["llm_request_ms"])
        latencies["total"].append(lat["total_ms"])
        
        # Log entry for tracing
        log_entry = {
            "query_id": query_id,
            "query": query_text,
            "eng_query": eng_query,
            "group": group_label,
            "answer": res["answer"],
            "gt_answer": gt_answer,
            "grounded": res["grounded"],
            "refused": res["refused"],
            "scores": res["scores"],
            "retrieved_ids": [f"{p.get('query_id')}_{p.get('passage_index')}" for p in res["retrieved_passages"]],
            "latency_ms": lat
        }
        log_file.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        
        # Compute generation metrics based on group
        is_ref = res["refused"]
        is_gro = res["grounded"]
        
        if group_label == "Group 3 (Noise)":
            if is_ref:
                g3_refused += 1
        elif group_label == "Group 2 (No-Answer)":
            if is_ref:
                g2_refused += 1
            else:
                g2_hallucinated += 1
        elif group_label == "Group 1 (Answerable)":
            if is_ref:
                g1_refused += 1
            elif is_gro:
                g1_grounded += 1
                
            # Compute retrieval metrics (compare retrieved items against Ground Truth selected list)
            passages_dict = row['passages']
            is_selected_list = passages_dict.get('is_selected', [])
            selected_indices = [i for i, sel in enumerate(is_selected_list) if sel == 1]
            
            # Map retrieved items to passage indices
            hits = []
            for rank_idx, ret_p in enumerate(res["retrieved_passages"]):
                # Hit conditions: match query_id and verify it represents a selected passage index
                is_hit = (ret_p["query_id"] == query_id and ret_p["is_selected"] == 1)
                hits.append({
                    "is_hit": is_hit,
                    "rank": rank_idx + 1
                })
            
            # Calculate Recall@5, Recall@10, and MRR
            # Note: recall here is whether at least one relevant passage is retrieved (Recall@K)
            has_hit_5 = any(h["is_hit"] for h in hits[:5])
            has_hit_10 = any(h["is_hit"] for h in hits[:10])
            
            retrieval_recalls_5.append(1.0 if has_hit_5 else 0.0)
            retrieval_recalls_10.append(1.0 if has_hit_10 else 0.0)
            
            mrr_val = 0.0
            for h in hits:
                if h["is_hit"]:
                    mrr_val = 1.0 / h["rank"]
                    break
            retrieval_mrrs.append(mrr_val)

    log_file.close()
    print(f"\nAudit logs saved successfully to: {log_file_path}")

    # 5. Summarize metrics
    total_g1 = len(group1_df)
    total_g2 = len(group2_df)
    total_g3 = len(group3_df)
    
    mean_rec_5 = np.mean(retrieval_recalls_5) if retrieval_recalls_5 else 0.0
    mean_rec_10 = np.mean(retrieval_recalls_10) if retrieval_recalls_10 else 0.0
    mean_mrr = np.mean(retrieval_mrrs) if retrieval_mrrs else 0.0
    
    g1_grounded_pct = (g1_grounded / total_g1 * 100) if total_g1 else 0.0
    g1_refused_pct = (g1_refused / total_g1 * 100) if total_g1 else 0.0
    g1_other_pct = 100.0 - g1_grounded_pct - g1_refused_pct
    
    g2_refused_pct = (g2_refused / total_g2 * 100) if total_g2 else 0.0
    g2_hallucinated_pct = (g2_hallucinated / total_g2 * 100) if total_g2 else 0.0
    
    g3_refused_pct = (g3_refused / total_g3 * 100) if total_g3 else 0.0

    print("\n" + "=" * 70)
    print("                   EVALUATION METRICS SUMMARY")
    print("=" * 70)
    print("1. RETRIEVAL METRICS (Evaluated on Group 1)")
    print(f"  - Recall@5:              {mean_rec_5:.4f}")
    print(f"  - Recall@10:             {mean_rec_10:.4f}")
    print(f"  - MRR:                   {mean_mrr:.4f}")
    print("-" * 70)
    print("2. GENERATION & GROUNDING METRICS")
    print(f"  Group 1 (Answerable - Total: {total_g1})")
    print(f"    - Grounded Answers:    {g1_grounded} ({g1_grounded_pct:.2f}%)")
    print(f"    - Refusals (Threshold): {g1_refused} ({g1_refused_pct:.2f}%)")
    print(f"    - Other (Ungrounded):  {total_g1 - g1_grounded - g1_refused} ({g1_other_pct:.2f}%)")
    print(f"  Group 2 (No-Answer - Total: {total_g2})")
    print(f"    - Correct Refusals:    {g2_refused} ({g2_refused_pct:.2f}%)  [Goal: High]")
    print(f"    - Hallucinations:      {g2_hallucinated} ({g2_hallucinated_pct:.2f}%)  [Goal: Low]")
    print(f"  Group 3 (Transl. Noise - Total: {total_g3})")
    print(f"    - Noise Refusals:      {g3_refused} ({g3_refused_pct:.2f}%)")
    print("-" * 70)
    
    # Calculate Latency Percentiles
    print("3. LATENCY METRICS (in Milliseconds)")
    print("| Component | P50 (ms) | P70 (ms) | P100 (ms) |")
    print("| :--- | :--- | :--- | :--- |")
    for key, val_list in latencies.items():
        if not val_list:
            print(f"| {key} | N/A | N/A | N/A |")
            continue
        p50 = np.percentile(val_list, 50)
        p70 = np.percentile(val_list, 70)
        p100 = np.percentile(val_list, 100)
        print(f"| {key:20s} | {p50:8.2f} | {p70:8.2f} | {p100:8.2f} |")
    print("=" * 70)

if __name__ == "__main__":
    main()
