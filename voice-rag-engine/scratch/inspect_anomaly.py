import os
import sys
import pandas as pd
from huggingface_hub import hf_hub_download

def main():
    output_file = "scratch/anomaly_inspection.txt"
    sys.stdout = open(output_file, "w", encoding="utf-8")
    
    repo_id = "ai4bharat/MSMARCO-XI"
    filename = "validation/hinval.parquet"
    local_path = hf_hub_download(repo_id=repo_id, filename=filename, repo_type="dataset")
    df = pd.read_parquet(local_path)
    
    no_answer_mask = df['Eng_Answer'].str.contains("No Answer Present", case=False, na=False)
    no_ans_df = df[no_answer_mask]
    
    print(f"Total 'No Answer Present' records: {len(no_ans_df)}")
    
    # We will search for queries that contain some common query terms where we might expect answers,
    # or just sample some queries that look very specific and check if their passages contain the answer.
    # Let's inspect a few records and print the full query and first 3 passages to see if they actually contain the answer.
    
    queries_to_inspect = [
        "chattanooga", "temperature", "population", "distance", "who is", "what is", "how many"
    ]
    
    found_count = 0
    for idx, row in no_ans_df.iterrows():
        query_lower = row['Eng_Query'].lower()
        if any(term in query_lower for term in queries_to_inspect):
            print(f"\n=========================================")
            print(f"Query ID: {row['query_id']}")
            print(f"Query (Eng): {row['Eng_Query']}")
            print(f"Query (Hin): {row['query']}")
            print(f"Answer (Eng): {row['Eng_Answer']}")
            print(f"Answer (Hin): {row['Answer']}")
            
            passages = row['passages']
            eng_p = passages.get('English_passages', [])
            trans_p = passages.get('Translated_passages', [])
            is_sel = passages.get('is_selected', [])
            
            print(f"Passages:")
            for p_idx, (ep, tp, sel) in enumerate(zip(eng_p, trans_p, is_sel)):
                print(f"  Passage {p_idx} (selected={sel}):")
                print(f"    Eng: {ep}")
                print(f"    Hin: {tp}")
            found_count += 1
            if found_count >= 10:
                break
                
    sys.stdout.close()

if __name__ == "__main__":
    main()
