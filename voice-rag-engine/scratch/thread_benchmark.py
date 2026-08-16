import os
import sys

# Inject local pkg path and virtual environment site-packages to resolve all imports
pkg_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'pkg'))
venv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.venv', 'Lib', 'site-packages'))

if pkg_path not in sys.path:
    sys.path.insert(0, pkg_path)
if venv_path not in sys.path:
    sys.path.insert(0, venv_path)

import time
import pandas as pd
from huggingface_hub import hf_hub_download
import torch

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("Error: sentence_transformers package not found. Please install it using:")
    print("pip install sentence-transformers")
    sys.exit(1)

def main():
    print(f"PyTorch default num_threads: {torch.get_num_threads()}")
    
    # Load model
    model = SentenceTransformer("intfloat/multilingual-e5-small", device="cpu")
    
    # Load actual passages from dataset
    repo_id = "ai4bharat/MSMARCO-XI"
    filename = "validation/hinval.parquet"
    local_path = hf_hub_download(repo_id=repo_id, filename=filename, repo_type="dataset")
    df = pd.read_parquet(local_path)
    
    # Get 500 Hindi passages
    passages = []
    for idx, row in df.head(50).iterrows():
        p_dict = row['passages']
        if isinstance(p_dict, dict):
            passages.extend(p_dict.get('Translated_passages', []))
    passages = passages[:500]
    prefixed_passages = [f"passage: {p}" for p in passages]
    print(f"Loaded {len(prefixed_passages)} actual passages for benchmark.")
    
    # Test 1: Default threads
    t0 = time.time()
    model.encode(prefixed_passages, batch_size=128, show_progress_bar=False, normalize_embeddings=True)
    t_default = time.time() - t0
    print(f"Default threads: {t_default:.2f}s ({len(passages)/t_default:.2f} passages/sec)")
    
    # Test 2: 1 thread
    torch.set_num_threads(1)
    print(f"Configuring PyTorch threads = 1")
    t0 = time.time()
    model.encode(prefixed_passages, batch_size=128, show_progress_bar=False, normalize_embeddings=True)
    t_1 = time.time() - t0
    print(f"1 thread: {t_1:.2f}s ({len(passages)/t_1:.2f} passages/sec)")
    
    # Test 3: 4 threads
    torch.set_num_threads(4)
    print(f"Configuring PyTorch threads = 4")
    t0 = time.time()
    model.encode(prefixed_passages, batch_size=128, show_progress_bar=False, normalize_embeddings=True)
    t_4 = time.time() - t0
    print(f"4 threads: {t_4:.2f}s ({len(passages)/t_4:.2f} passages/sec)")
    
    # Test 4: 8 threads
    torch.set_num_threads(8)
    print(f"Configuring PyTorch threads = 8")
    t0 = time.time()
    model.encode(prefixed_passages, batch_size=128, show_progress_bar=False, normalize_embeddings=True)
    t_8 = time.time() - t0
    print(f"8 threads: {t_8:.2f}s ({len(passages)/t_8:.2f} passages/sec)")

if __name__ == "__main__":
    main()
