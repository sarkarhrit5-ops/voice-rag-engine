# End-to-end Text RAG Pipeline integration

import os
import sys
import time

# Ensure local packages are importable
pkg_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'pkg'))
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if pkg_path not in sys.path:
    sys.path.insert(0, pkg_path)
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from retrieval.indexer import VectorIndexer
from retrieval.retriever import DenseRetriever
from .context_builder import build_context
from .prompts import get_system_prompt, get_refusal_response
from .grounding import GroundingEvaluator
from .llm_client import LLMClient

class TextRAGPipeline:
    def __init__(self, index_dir: str = "retrieval/indexes/eng_sentence_aware_plain",
                 model_name: str = "intfloat/multilingual-e5-small",
                 device: str = "cpu",
                 llm_provider: str = None,
                 llm_model: str = None,
                 llm_timeout_seconds: float = None):
        """
        Initializes the Text-based RAG pipeline.
        Loads the pre-built FAISS index and the embedding model.
        """
        self.indexer = VectorIndexer(model_name=model_name, device=device)
        self.indexer.load_index(index_dir)
        self.retriever = DenseRetriever(self.indexer)
        self.llm_client = LLMClient(provider=llm_provider, model=llm_model, timeout=llm_timeout_seconds)

    def answer(self, query: str, language: str = "hi", top_k: int = 5, min_score: float = 0.70, query_id: int = None) -> dict:
        """
        Executes the text RAG pipeline:
        1. Dense retrieval of top-K passages.
        2. Strict confidence score threshold check (short-circuits to refusal if below min_score).
        3. Compact context building.
        4. LLM query generation with strict context grounding prompts.
        5. Refusal/grounding check on generated response.
        Returns a structured dictionary with answer, trace, and latencies.
        """
        t_pipeline_start = time.time()
        
        # 1. Retrieval Layer
        retrieved_passages, retrieval_latencies = self.retriever.retrieve(query, k=top_k)
        
        # Extract individual retrieval latencies
        query_embedding_ms = retrieval_latencies.get("query_embedding_ms", 0.0)
        vector_search_ms = retrieval_latencies.get("faiss_search_ms", 0.0)
        metadata_lookup_ms = retrieval_latencies.get("metadata_lookup_ms", 0.0)
        
        # Initialize other stage metrics
        context_construction_ms = 0.0
        llm_request_ms = 0.0
        
        # 2. Grounding / Confidence Evaluation
        t_context_start = time.time()
        evaluator = GroundingEvaluator(min_score=min_score)
        has_sufficient_evidence = evaluator.check_retrieval_confidence(retrieved_passages)
        
        if not has_sufficient_evidence:
            # SHORT-CIRCUIT: Refuse answer immediately, bypassing LLM call entirely
            answer = get_refusal_response(language)
            grounded = False
            refused = True
            context_construction_ms = (time.time() - t_context_start) * 1000.0
            
            # Print refusal reason internally
            print(f"[RAG Pipeline] Max retrieval score below threshold ({min_score}). Short-circuiting with refusal.")
        else:
            # Keep the evidence set minimal and concise to reduce generation latency.
            limited_passages = retrieved_passages[: min(2, len(retrieved_passages))]

            # 3. Context Construction
            context = build_context(limited_passages, max_chars=3000)
            context_construction_ms = (time.time() - t_context_start) * 1000.0
            
            # 4. LLM Completion Generation
            t_llm_start = time.time()
            system_prompt = get_system_prompt(language)
            user_prompt = f"Evidence context:\n{context}\n\nUser Query:\n{query}"
            
            answer, llm_request_ms = self.llm_client.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=50,
                temperature=0.0,
                retrieved_passages=limited_passages,
                query_id=query_id
            )
            
            # 5. Post-completions validation
            grounded, refused = evaluator.post_evaluate_generation(answer, language)
            
        total_pipeline_ms = (time.time() - t_pipeline_start) * 1000.0
        
        # Structured output format
        response = {
            "answer": answer,
            "language": language,
            "retrieved_passages": [p["metadata"] for p in retrieved_passages],
            "scores": [p["score"] for p in retrieved_passages],
            "grounded": grounded,
            "refused": refused,
            "llm_metrics": dict(self.llm_client.last_generation_metrics),
            "latency_ms": {
                "query_embedding_ms": query_embedding_ms,
                "vector_search_ms": vector_search_ms,
                "metadata_lookup_ms": metadata_lookup_ms,
                "context_construction_ms": context_construction_ms,
                "llm_request_ms": llm_request_ms,
                "total_rag_ms": total_pipeline_ms,
                "total_ms": total_pipeline_ms,
            }
        }
        
        return response
