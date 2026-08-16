# Manual verification script for Text RAG Pipeline

import os
import sys
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

def is_translation_loop(text: str) -> bool:
    if not isinstance(text, str):
        return False
    words = text.split()
    if len(words) > 15:
        ratio = len(set(words)) / len(words)
        if ratio < 0.35:
            return True
    return False

def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        
    print("=" * 70)
    print("               RAG PIPELINE MANUAL VERIFICATION")
    print("=" * 70)
    
    # 1. Initialize Pipeline
    pipeline = TextRAGPipeline(
        index_dir="retrieval/indexes/eng_sentence_aware_plain",
        model_name="intfloat/multilingual-e5-small",
        device="cpu"
    )
    
    # 2. Load dataset
    repo_id = "ai4bharat/MSMARCO-XI"
    local_path = hf_hub_download(repo_id=repo_id, filename="validation/hinval.parquet", repo_type="dataset")
    df = pd.read_parquet(local_path)
    
    # Sample the exact 100 queries indexed in the FAISS index
    sample_df = df.sample(n=100, random_state=42).copy()
    sample_df['num_selected'] = sample_df['passages'].apply(lambda p: sum(p.get('is_selected', [])) if isinstance(p, dict) else 0)
    sample_df['is_noise'] = sample_df.apply(lambda r: is_translation_loop(r['query']) or is_translation_loop(r['Answer']), axis=1)
    
    clean_sample = sample_df[sample_df['is_noise'] == False]
    
    # Get answerable query and no-answer query from the indexed sample
    answerable_row = clean_sample[clean_sample['num_selected'] > 0].iloc[0]
    no_answer_row = clean_sample[clean_sample['num_selected'] == 0].iloc[0]
    
    test_cases = [
        {
            "name": "Case 1: Answerable Hindi Query (from indexed subset)",
            "query": answerable_row['query'],
            "query_id": int(answerable_row['query_id']),
            "lang": "hi",
            "min_score": 0.70,
            "top_k": 5
        },
        {
            "name": "Case 2: Hindi Query with No Answer (from indexed subset)",
            "query": no_answer_row['query'],
            "query_id": int(no_answer_row['query_id']),
            "lang": "hi",
            "min_score": 0.70,
            "top_k": 5
        },
        {
            "name": "Case 3: Query retrieving multiple passages (top_k = 10)",
            "query": answerable_row['query'],
            "query_id": int(answerable_row['query_id']),
            "lang": "hi",
            "min_score": 0.60,
            "top_k": 10
        },
        {
            "name": "Case 4: Obviously Off-domain Query",
            "query": "Who won the 2026 FIFA World Cup soccer tournament?",
            "query_id": None,
            "lang": "hi",
            "min_score": 0.75,
            "top_k": 5
        }
    ]
    
    for case in test_cases:
        print("\n" + "-" * 50)
        print(f"RUNNING: {case['name']}")
        print(f"Query:    {case['query']}")
        print(f"Query ID: {case['query_id']}")
        print(f"Top-K:    {case['top_k']} | Min Score: {case['min_score']}")
        print("-" * 50)
        
        res = pipeline.answer(
            query=case['query'],
            language=case['lang'],
            top_k=case['top_k'],
            min_score=case['min_score'],
            query_id=case['query_id']
        )
        
        print(f"Structured Output:")
        print(f"  - Answer:    {res['answer']}")
        print(f"  - Language:  {res['language']}")
        print(f"  - Grounded:  {res['grounded']}")
        print(f"  - Refused:   {res['refused']}")
        print(f"  - Passages retrieved: {len(res['retrieved_passages'])}")
        if res['retrieved_passages']:
            print(f"  - Top Match Score: {res['scores'][0]:.4f}")
            print(f"  - Top Match ID:    {res['retrieved_passages'][0].get('query_id')}_{res['retrieved_passages'][0].get('passage_index')}")
        print(f"  - Latencies (ms):")
        for k, v in res['latency_ms'].items():
            print(f"      {k:25s}: {v:.2f} ms")
            
    print("\n" + "=" * 70)
    print("Verification completed.")
    print("=" * 70)

if __name__ == "__main__":
    main()
