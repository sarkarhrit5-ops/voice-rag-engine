import os
import sys
import pandas as pd
import numpy as np
from huggingface_hub import hf_hub_download

def main():
    # Redirect stdout to a file for easy viewing
    output_file = "scratch/inspection_output.txt"
    sys.stdout = open(output_file, "w", encoding="utf-8")
    
    repo_id = "ai4bharat/MSMARCO-XI"
    filename = "validation/hinval.parquet"
    print("Downloading dataset...")
    local_path = hf_hub_download(repo_id=repo_id, filename=filename, repo_type="dataset")
    print(f"Loaded parquet from {local_path}")
    
    df = pd.read_parquet(local_path)
    print(f"Loaded {len(df)} rows.")
    
    # Filter rows where Answer is "No Answer Present" or Hindi translation of it, or has empty answer,
    # and check what is_selected says.
    no_answer_eng_mask = df['Eng_Answer'].str.contains("No Answer Present", case=False, na=False)
    no_answer_hin_mask = df['Answer'].str.contains("कोई उत्तर नहीं", case=False, na=False)
    no_ans_df = df[no_answer_eng_mask | no_answer_hin_mask]
    
    print(f"Number of rows with 'No Answer Present': {len(no_ans_df)}")
    
    # Sample a few to check passages and is_selected
    print("\n--- Examining 5 samples with 'No Answer Present' but having passages ---")
    count = 0
    for idx, row in no_ans_df.iterrows():
        passages = row['passages']
        if isinstance(passages, dict):
            is_selected = passages.get('is_selected', [])
            translated = passages.get('Translated_passages', [])
            english = passages.get('English_passages', [])
            
            # Print if there is a discrepancy (e.g. is_selected has all 0s, or has 1s)
            sum_selected = sum(is_selected)
            print(f"\nQuery ID: {row['query_id']}")
            print(f"Query (Hin): {row['query']}")
            print(f"Query (Eng): {row['Eng_Query']}")
            print(f"Answer (Hin): {row['Answer']}")
            print(f"Answer (Eng): {row['Eng_Answer']}")
            print(f"Passage count: {len(translated)}, Sum of selected: {sum_selected}")
            print(f"Is Selected list: {is_selected}")
            
            for p_idx, (trans_p, eng_p, sel) in enumerate(zip(translated, english, is_selected)):
                if sel == 1 or p_idx < 3: # print selected or first few
                    sel_lbl = "[SELECTED]" if sel == 1 else "[UNSELECTED]"
                    print(f"  Passage {p_idx} {sel_lbl}:")
                    print(f"    Eng: {eng_p[:200]}...")
                    print(f"    Hin: {trans_p[:200]}...")
            
            count += 1
            if count >= 5:
                break
                
    # Also find examples where Answer is NOT "No Answer Present" but sum(is_selected) == 0
    ans_present_mask = ~(no_answer_eng_mask | no_answer_hin_mask)
    ans_present_df = df[ans_present_mask]
    no_selected_passages_but_ans_present = ans_present_df[ans_present_df['passages'].apply(lambda p: sum(p.get('is_selected', [])) == 0 if isinstance(p, dict) else False)]
    
    print(f"\nNumber of rows with Answer Present but sum(is_selected) == 0: {len(no_selected_passages_but_ans_present)}")
    if len(no_selected_passages_but_ans_present) > 0:
        print("\n--- Examining 3 samples with Answer Present but sum(is_selected) == 0 ---")
        for idx, row in no_selected_passages_but_ans_present.head(3).iterrows():
            passages = row['passages']
            is_selected = passages.get('is_selected', [])
            translated = passages.get('Translated_passages', [])
            print(f"\nQuery ID: {row['query_id']}")
            print(f"Query: {row['query']}")
            print(f"Answer: {row['Answer']}")
            print(f"Is Selected list: {is_selected}")
            for p_idx, trans_p in enumerate(translated[:2]):
                print(f"  Passage {p_idx}: {trans_p[:200]}...")
                
    # Also find examples where Answer is "No Answer Present" but sum(is_selected) > 0
    selected_passages_but_no_ans = no_ans_df[no_ans_df['passages'].apply(lambda p: sum(p.get('is_selected', [])) > 0 if isinstance(p, dict) else False)]
    print(f"\nNumber of rows with 'No Answer Present' but sum(is_selected) > 0: {len(selected_passages_but_no_ans)}")
    if len(selected_passages_but_no_ans) > 0:
        print("\n--- Examining 3 samples with 'No Answer Present' but sum(is_selected) > 0 ---")
        for idx, row in selected_passages_but_no_ans.head(3).iterrows():
            passages = row['passages']
            is_selected = passages.get('is_selected', [])
            translated = passages.get('Translated_passages', [])
            print(f"\nQuery ID: {row['query_id']}")
            print(f"Query: {row['query']}")
            print(f"Answer: {row['Answer']}")
            print(f"Is Selected list: {is_selected}")
            for p_idx, (trans_p, sel) in enumerate(zip(translated, is_selected)):
                if sel == 1:
                    print(f"  Passage {p_idx} [SELECTED]: {trans_p[:200]}...")
                    
    sys.stdout.close()

if __name__ == "__main__":
    main()
