import os
import argparse
import sys
import pandas as pd
import numpy as np
from huggingface_hub import hf_hub_download

def parse_args():
    parser = argparse.ArgumentParser(description="Reproducible exploration and inspection of MSMARCO-XI dataset subsets.")
    parser.add_argument("--language", type=str, default="hin", 
                        choices=["asm", "ben", "guj", "hin", "kan", "mal", "mar", "nep", "ori", "pan", "san", "tam", "tel", "urd"],
                        help="Language code to explore (e.g., 'hin' for Hindi, 'asm' for Assamese).")
    parser.add_argument("--split", type=str, default="validation", choices=["train", "validation"],
                        help="Dataset split to explore ('train' or 'validation').")
    parser.add_argument("--samples", type=int, default=1000,
                        help="Number of random samples to draw for stats and detailed analysis (default: 1000).")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed for reproducible sampling (default: 42).")
    return parser.parse_args()

def main():
    args = parse_args()
    
    # Configure stdout to handle UTF-8 printing safely on all systems, especially Windows
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        
    print("=" * 60)
    print("         MSMARCO-XI DATASET EXPLORATION SCRIPT")
    print("=" * 60)
    print(f"Configured options:")
    print(f"  Language: {args.language}")
    print(f"  Split:    {args.split}")
    print(f"  Samples:  {args.samples}")
    print(f"  Seed:     {args.seed}")
    print("-" * 60)

    # Validate language split availability
    if args.language == "tel" and args.split == "train":
        print("[ERROR] Telugu ('tel') is only available in the validation split.")
        sys.exit(1)

    repo_id = "ai4bharat/MSMARCO-XI"
    
    # Build filename in repo
    # e.g., validation/hinval.parquet or train/hintrain.parquet
    val_suffix = "val" if args.split == "validation" else "train"
    filename = f"{args.split}/{args.language}{val_suffix}.parquet"
    
    print(f"Attempting to download/load subset file: {filename} from {repo_id}...")
    try:
        local_path = hf_hub_download(repo_id=repo_id, filename=filename, repo_type="dataset")
        print(f"Successfully loaded. Local cached path: {local_path}")
        print(f"File size: {os.path.getsize(local_path) / (1024 * 1024):.2f} MB")
    except Exception as e:
        print(f"[ERROR] Failed to download subset file: {e}")
        sys.exit(1)
        
    print("-" * 60)
    print("Reading data with Pandas/PyArrow...")
    try:
        df = pd.read_parquet(local_path)
    except Exception as e:
        print(f"[ERROR] Failed to read parquet file: {e}")
        sys.exit(1)
        
    total_records = len(df)
    print(f"Total records in subset split: {total_records}")
    print(f"Columns present: {df.columns.tolist()}")
    print("\nData Types:")
    for col in df.columns:
        print(f"  {col}: {df[col].dtype}")
        
    print("-" * 60)
    # Determine sample size
    sample_size = min(args.samples, total_records)
    print(f"Sampling {sample_size} records with seed={args.seed} for statistics...")
    
    sample_df = df.sample(n=sample_size, random_state=args.seed)
    
    # Statistics extraction
    # 1. Text length calculations (Character & Word Counts)
    query_chars = sample_df['query'].apply(lambda x: len(str(x)) if x else 0)
    query_words = sample_df['query'].apply(lambda x: len(str(x).split()) if x else 0)
    
    eng_query_chars = sample_df['Eng_Query'].apply(lambda x: len(str(x)) if x else 0)
    eng_query_words = sample_df['Eng_Query'].apply(lambda x: len(str(x).split()) if x else 0)
    
    answer_chars = sample_df['Answer'].apply(lambda x: len(str(x)) if x else 0)
    answer_words = sample_df['Answer'].apply(lambda x: len(str(x).split()) if x else 0)
    
    eng_answer_chars = sample_df['Eng_Answer'].apply(lambda x: len(str(x)) if x else 0)
    eng_answer_words = sample_df['Eng_Answer'].apply(lambda x: len(str(x).split()) if x else 0)
    
    # 2. Passage count & details
    passage_counts = sample_df['passages'].apply(lambda p: len(p.get('Translated_passages', [])) if isinstance(p, dict) else 0)
    selected_passage_counts = sample_df['passages'].apply(lambda p: sum(p.get('is_selected', [])) if isinstance(p, dict) else 0)
    
    # Flatten sample passages to compute sizes
    all_translated_passages = []
    all_english_passages = []
    all_passage_selected_status = []
    
    for p in sample_df['passages']:
        if isinstance(p, dict):
            all_translated_passages.extend(p.get('Translated_passages', []))
            all_english_passages.extend(p.get('English_passages', []))
            all_passage_selected_status.extend(p.get('is_selected', []))
            
    passage_chars = [len(str(p)) for p in all_translated_passages]
    passage_words = [len(str(p).split()) for p in all_translated_passages]
    
    eng_passage_chars = [len(str(p)) for p in all_english_passages]
    eng_passage_words = [len(str(p).split()) for p in all_english_passages]
    
    # Print basic text statistics
    print("\n--- Query Text Statistics ---")
    print(f"Target Lang ({args.language}) Query:")
    print(f"  Character length -> Mean: {query_chars.mean():.1f} | Median: {query_chars.median():.0f} | Min: {query_chars.min()} | Max: {query_chars.max()}")
    print(f"  Word count       -> Mean: {query_words.mean():.1f} | Median: {query_words.median():.0f} | Min: {query_words.min()} | Max: {query_words.max()}")
    print(f"Original English Query:")
    print(f"  Character length -> Mean: {eng_query_chars.mean():.1f} | Median: {eng_query_chars.median():.0f} | Min: {eng_query_chars.min()} | Max: {eng_query_chars.max()}")
    
    print("\n--- Answer Text Statistics ---")
    print(f"Target Lang ({args.language}) Answer:")
    print(f"  Character length -> Mean: {answer_chars.mean():.1f} | Median: {answer_chars.median():.0f} | Min: {answer_chars.min()} | Max: {answer_chars.max()}")
    print(f"  Word count       -> Mean: {answer_words.mean():.1f} | Median: {answer_words.median():.0f} | Min: {answer_words.min()} | Max: {answer_words.max()}")
    print(f"Original English Answer:")
    print(f"  Character length -> Mean: {eng_answer_chars.mean():.1f} | Median: {eng_answer_chars.median():.0f} | Min: {eng_answer_chars.min()} | Max: {eng_answer_chars.max()}")
    
    # Check for ungrounded answers (answers that indicate no answer found)
    no_answer_count = sum(sample_df['Answer'].apply(lambda x: 1 if "कोई उत्तर नहीं" in str(x) or "No Answer Present" in str(x) or str(x).strip() == "" else 0))
    print(f"  Ungrounded / No Answer placeholders: {no_answer_count} ({no_answer_count / sample_size * 100:.1f}%)")

    print("\n--- Passage Statistics (RAG Specifics) ---")
    print(f"Passages per query:")
    print(f"  Total passages    -> Mean: {passage_counts.mean():.2f} | Min: {passage_counts.min()} | Max: {passage_counts.max()}")
    print(f"  Selected (relevant) -> Mean: {selected_passage_counts.mean():.2f} | Min: {selected_passage_counts.min()} | Max: {selected_passage_counts.max()}")
    
    selected_ratios = selected_passage_counts / passage_counts.replace(0, 1)
    print(f"  Selected ratio per query -> Mean: {selected_ratios.mean()*100:.1f}%")
    
    queries_with_no_relevant_passages = sum(selected_passage_counts == 0)
    print(f"  Queries with 0 relevant passages: {queries_with_no_relevant_passages} ({queries_with_no_relevant_passages / sample_size * 100:.1f}%)")

    print(f"Passage text length (based on {len(all_translated_passages)} total passages):")
    print(f"  Target Lang ({args.language}) Passage:")
    print(f"    Char length -> Mean: {np.mean(passage_chars):.1f} | P50: {np.percentile(passage_chars, 50):.0f} | P90: {np.percentile(passage_chars, 90):.0f} | P99: {np.percentile(passage_chars, 99):.0f} | Max: {np.max(passage_chars)}")
    print(f"    Word count  -> Mean: {np.mean(passage_words):.1f} | P50: {np.percentile(passage_words, 50):.0f} | P90: {np.percentile(passage_words, 90):.0f} | P99: {np.percentile(passage_words, 99):.0f} | Max: {np.max(passage_words)}")
    print(f"  Original English Passage:")
    print(f"    Char length -> Mean: {np.mean(eng_passage_chars):.1f} | P50: {np.percentile(eng_passage_chars, 50):.0f} | P90: {np.percentile(eng_passage_chars, 90):.0f} | P99: {np.percentile(eng_passage_chars, 99):.0f} | Max: {np.max(eng_passage_chars)}")

    # 3. Query type distribution
    print("\n--- Query Type Distribution ---")
    qtype_dist = sample_df['query_type'].value_counts()
    for qtype, count in qtype_dist.items():
        print(f"  {qtype:<15}: {count:<5} ({count/sample_size*100:.1f}%)")
        
    # 4. Metadata details
    print("\n--- Metadata Analysis ---")
    if 'meta' in sample_df.columns:
        # Check first row meta structure
        first_meta = sample_df['meta'].iloc[0]
        print(f"Meta data structure (type: {type(first_meta)}):")
        if isinstance(first_meta, dict):
            for k, v in first_meta.items():
                print(f"  {k}: {type(v).__name__} (example: {v})")
        else:
            print(f"  Raw example: {first_meta}")
            
    # Check if there are duplicate queries
    duplicate_queries = total_records - df['query'].nunique()
    print(f"\n--- Duplicate / Redundancy Check ---")
    print(f"  Duplicate queries in full dataset: {duplicate_queries} ({duplicate_queries / total_records * 100:.2f}%)")
    
    # 5. Selected Representative Example
    print("\n" + "="*60)
    print("=== REPRESENTATIVE EXAMPLE FROM DATASET ===")
    print("="*60)
    example_row = sample_df.iloc[0]
    print(f"Query ID:   {example_row.get('query_id', 'N/A')}")
    print(f"Query Type: {example_row.get('query_type', 'N/A')}")
    print(f"Source Lang: {example_row.get('source_lang', 'N/A')} | Target Lang: {example_row.get('target_lang', 'N/A')}")
    print(f"Eng Query:  {example_row.get('Eng_Query', 'N/A')}")
    print(f"Query ({args.language}): {example_row.get('query', 'N/A')}")
    print("-" * 60)
    print(f"Eng Answer: {example_row.get('Eng_Answer', 'N/A')}")
    print(f"Answer ({args.language}): {example_row.get('Answer', 'N/A')}")
    print("-" * 60)
    
    passages = example_row.get('passages', {})
    if isinstance(passages, dict):
        eng_p = passages.get('English_passages', [])
        trans_p = passages.get('Translated_passages', [])
        is_sel = passages.get('is_selected', [])
        
        print(f"Passages Count: {len(trans_p)}")
        for idx, (ep, tp, sel) in enumerate(zip(eng_p, trans_p, is_sel)):
            sel_str = "[SELECTED - RELEVANT]" if sel == 1 else "[NOT SELECTED]"
            print(f"\nPassage {idx} {sel_str}:")
            print(f"  Eng:   {ep[:150]}...")
            print(f"  Trans: {tp[:150]}...")
    print("=" * 60)

if __name__ == "__main__":
    main()
