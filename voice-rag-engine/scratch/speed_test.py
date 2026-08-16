import time
import os
import sys
import numpy as np

# Inject pkg path
pkg_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'pkg'))
if pkg_path not in sys.path:
    sys.path.insert(0, pkg_path)

from sentence_transformers import SentenceTransformer

def main():
    print("Loading model...")
    t0 = time.time()
    model = SentenceTransformer("intfloat/multilingual-e5-small", device="cpu")
    print(f"Model loaded in {time.time() - t0:.2f}s")
    
    # Generate 1000 dummy passages
    dummy_passages = [f"passage: This is dummy passage number {i} for testing embedding performance and speed." for i in range(1000)]
    
    print("Encoding 1000 passages...")
    t1 = time.time()
    model.encode(dummy_passages, batch_size=128, show_progress_bar=False, normalize_embeddings=True)
    t2 = time.time()
    elapsed = t2 - t1
    print(f"Encoded 1000 passages in {elapsed:.2f}s ({1000/elapsed:.2f} passages/sec)")

if __name__ == "__main__":
    main()
