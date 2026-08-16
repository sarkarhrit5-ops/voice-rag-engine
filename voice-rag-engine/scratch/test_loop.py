import os
import sys
import pandas as pd
from huggingface_hub import hf_hub_download

def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        
    repo_id = "ai4bharat/MSMARCO-XI"
    local_path = hf_hub_download(repo_id=repo_id, filename="validation/hinval.parquet", repo_type="dataset")
    df = pd.read_parquet(local_path)

    def is_loop(text):
        if not isinstance(text, str):
            return False
        words = text.split()
        if len(words) > 15:
            ratio = len(set(words)) / len(words)
            if ratio < 0.35:
                return True
        return False

    loops = df[df['query'].apply(is_loop) | df['Answer'].apply(is_loop)]
    print(f"Detected loops in full validation set: {len(loops)}")
    for idx, row in loops.head(5).iterrows():
        print(f"ID: {row['query_id']}")
        # Encode with backslashreplace or print directly since stdout is utf-8
        print(f"  Query: {row['query'][:100]}")
        print(f"  Answer: {row['Answer'][:100]}")

if __name__ == "__main__":
    main()
