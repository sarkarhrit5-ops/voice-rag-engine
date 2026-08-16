import os
import sys
import time
import numpy as np

# Ensure local packages in 'pkg' are importable
pkg_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'pkg'))
if pkg_path not in sys.path:
    sys.path.insert(0, pkg_path)

class DenseRetriever:
    def __init__(self, indexer):
        """
        Initializes the Dense Retriever with a VectorIndexer instance.
        """
        self.indexer = indexer

    def retrieve(self, query_text: str, k: int = 5) -> tuple[list[dict], dict]:
        """
        Executes top-K dense retrieval for a single query.
        Returns a tuple of (results, latency_metrics).
        
        results is a list of dicts, each containing:
          - score: cosine similarity score (inner product of normalized vectors)
          - rank: 1-indexed rank
          - metadata: dict of metadata for the retrieved chunk
          
        latency_metrics is a dict containing:
          - query_embedding_ms: query encoding time in milliseconds
          - faiss_search_ms: vector index search time in milliseconds
          - metadata_lookup_ms: time taken to map indices to metadata in milliseconds
          - total_retrieval_ms: sum of the above three stages in milliseconds
        """
        if self.indexer.index is None:
            raise ValueError("FAISS index is not loaded. Build or load an index first.")
            
        t_start = time.time()
        
        # 1. Query Embedding
        t_embed_start = time.time()
        # Prepend 'query: ' prefix required by multilingual-e5 models for queries
        prefixed_query = f"query: {query_text}"
        
        query_vector = self.indexer.model.encode(
            [prefixed_query],
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False
        )
        # Ensure correct type (float32) and shape (2D array for FAISS query)
        query_vector = query_vector.astype('float32')
        t_embed_end = time.time()
        query_embedding_ms = (t_embed_end - t_embed_start) * 1000.0
        
        # 2. FAISS Vector Search
        t_search_start = time.time()
        # Search index
        scores, indices = self.indexer.index.search(query_vector, k)
        t_search_end = time.time()
        faiss_search_ms = (t_search_end - t_search_start) * 1000.0
        
        # 3. Metadata Lookup
        t_lookup_start = time.time()
        results = []
        for rank, (score, idx) in enumerate(zip(scores[0], indices[0])):
            # FAISS returns -1 for indices if not enough vectors exist in the index
            if idx == -1:
                continue
            
            # Map index back to metadata
            meta = self.indexer.metadata[idx]
            results.append({
                "score": float(score),
                "rank": rank + 1,
                "metadata": meta
            })
        t_lookup_end = time.time()
        metadata_lookup_ms = (t_lookup_end - t_lookup_start) * 1000.0
        
        total_ms = (time.time() - t_start) * 1000.0
        
        latencies = {
            "query_embedding_ms": query_embedding_ms,
            "faiss_search_ms": faiss_search_ms,
            "metadata_lookup_ms": metadata_lookup_ms,
            "total_retrieval_ms": total_ms
        }
        
        return results, latencies
