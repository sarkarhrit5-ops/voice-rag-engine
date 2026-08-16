import time
import os
import sys
import pandas as pd
from huggingface_hub import hf_hub_download

# Inject pkg path
pkg_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'pkg'))
if pkg_path not in sys.path:
    sys.path.insert(0, pkg_path)

import torch
from sentence_transformers import SentenceTransformer

def main():
    model = SentenceTransformer("intfloat/multilingual-e5-small", device="cpu")
    
    # Load actual passages from dataset
    repo_id = "ai4bharat/MSMARCO-XI"
    filename = "validation/hinval.parquet"
    local_path = hf_hub_download(repo_id=repo_id, filename=filename, repo_type="dataset")
    df = pd.read_parquet(local_path)
    
    # Get 300 Hindi passages
    passages = []
    for idx, row in df.head(50).iterrows():
        p_dict = row['passages']
        if isinstance(p_dict, dict):
            passages.extend(p_dict.get('Translated_passages', []))
    passages = passages[:300]
    prefixed_passages = [f"passage: {p}" for p in passages]
    
    for bs in [16, 32, 64, 128]:
        t0 = time.time()
        model.encode(prefixed_passages, batch_size=bs, show_progress_bar=False, normalize_embeddings=True)
        t_elapsed = time.time() - t0
        print(f"Batch Size {bs}: {t_elapsed:.2f}s ({len(passages)/t_elapsed:.2f} passages/sec)")

if __name__ == "__main__":
    main()
