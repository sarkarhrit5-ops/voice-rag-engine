import os
import sys
import json
import time
import numpy as np

# Add local pkg directory to sys.path to ensure we can load faiss and sentence_transformers
pkg_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'pkg'))
if pkg_path not in sys.path:
    sys.path.insert(0, pkg_path)

import faiss
from sentence_transformers import SentenceTransformer

class VectorIndexer:
    def __init__(self, model_name: str = "intfloat/multilingual-e5-small", device: str = None, shared_model=None):
        """
        Initializes the VectorIndexer.
        Loads the SentenceTransformer model and prepares the FAISS index container.
        """
        self.model_name = model_name
        # Auto-detect device (use CPU if not specified)
        if device is None:
            self.device = "cpu"
        else:
            self.device = device
            
        if shared_model is not None:
            self.model = shared_model
        else:
            print(f"Loading embedding model '{self.model_name}' on device '{self.device}'...")
            t0 = time.time()
            self.model = SentenceTransformer(self.model_name, device=self.device)
            print(f"Model loaded in {time.time() - t0:.2f} seconds.")
        
        self.index = None
        self.metadata = []  # List of dicts mapping 1-to-1 with index vectors

    def build_index(self, documents: list[str], metadatas: list[dict], batch_size: int = 128, show_progress_bar: bool = False) -> dict:
        """
        Embeds a list of documents and builds a FAISS IndexFlatIP index.
        Appends the required "passage: " prefix for E5 model formatting.
        Returns build metrics (chunking, embedding, index build time).
        """
        if not documents:
            raise ValueError("No documents provided to build the index.")
        if len(documents) != len(metadatas):
            raise ValueError("Size mismatch between documents and metadatas lists.")
            
        t_embed_start = time.time()
        
        # Prepend 'passage: ' prefix required by multilingual-e5 models for asymmetric retrieval
        prefixed_docs = [f"passage: {doc}" for doc in documents]
        
        print(f"Embedding {len(prefixed_docs)} documents (batch_size={batch_size})...")
        # Generate normalized embeddings to use L2-normalized Inner Product (equivalent to Cosine Similarity)
        embeddings = self.model.encode(
            prefixed_docs, 
            batch_size=batch_size, 
            show_progress_bar=show_progress_bar,
            normalize_embeddings=True,
            convert_to_numpy=True
        )
        
        t_embed_end = time.time()
        embedding_time = t_embed_end - t_embed_start
        print(f"Embedding generation completed in {embedding_time:.2f} seconds.")
        
        t_index_start = time.time()
        
        # Retrieve vector dimensions
        dimension = embeddings.shape[1]
        
        # FAISS IndexFlatIP stands for Inner Product.
        # Combined with L2 normalization, inner product is mathematically identical to Cosine Similarity.
        self.index = faiss.IndexFlatIP(dimension)
        
        # Add embeddings to FAISS index
        self.index.add(embeddings.astype('float32'))
        self.metadata = list(metadatas)
        
        t_index_end = time.time()
        index_build_time = t_index_end - t_index_start
        
        return {
            "embedding_time_sec": embedding_time,
            "faiss_build_time_sec": index_build_time,
            "total_documents": len(documents),
            "vector_dimension": dimension
        }

    def save_index(self, directory: str, index_name: str = "faiss_index") -> dict:
        """
        Saves the FAISS index and the associated metadata mapping to disk.
        """
        if self.index is None:
            raise ValueError("No index has been built or loaded yet.")
            
        os.makedirs(directory, exist_ok=True)
        index_path = os.path.join(directory, f"{index_name}.index")
        meta_path = os.path.join(directory, f"{index_name}.json")
        
        t0 = time.time()
        # Save FAISS index
        faiss.write_index(self.index, index_path)
        
        # Save Metadata
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)
            
        save_time = time.time() - t0
        print(f"Index and metadata saved successfully to {directory} in {save_time:.2f} seconds.")
        return {
            "index_path": index_path,
            "metadata_path": meta_path,
            "save_time_sec": save_time
        }

    def load_index(self, directory: str, index_name: str = "faiss_index"):
        """
        Loads the FAISS index and the associated metadata mapping from disk.
        """
        index_path = os.path.join(directory, f"{index_name}.index")
        meta_path = os.path.join(directory, f"{index_name}.json")
        
        if not os.path.exists(index_path) or not os.path.exists(meta_path):
            raise FileNotFoundError(f"Index files not found in directory: {directory}")
            
        t0 = time.time()
        # Load FAISS index
        self.index = faiss.read_index(index_path)
        
        # Load Metadata
        with open(meta_path, 'r', encoding='utf-8') as f:
            self.metadata = json.load(f)
            
        print(f"Index loaded successfully from {directory} in {time.time() - t0:.2f} seconds.")
        print(f"Loaded index size: {self.index.ntotal} vectors.")
