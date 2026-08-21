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
from retrieval.multilingual_retriever import MultilingualRetriever
from retrieval.index_store import available_language_indexes, language_index_dir
from retrieval.languages import normalize_language_code, to_msmarco_xi_code
from .context_builder import build_context
from .prompts import get_system_prompt, get_refusal_response
from .grounding import GroundingEvaluator
from .llm_client import LLMClient

class TextRAGPipeline:
    def __init__(self, index_dir: str = None,
                 model_name: str = "intfloat/multilingual-e5-small",
                 device: str = "cpu",
                 llm_provider: str = None,
                 llm_model: str = None,
                 llm_timeout_seconds: float = None,
                 multilingual_index_dir: str = None):
        """
        Initializes the Text-based RAG pipeline supporting both Hindi and English indexes.

        If ``multilingual_index_dir`` (or the ``MSMARCO_XI_INDEX_DIR`` environment
        variable) points to a built multilingual index, non-English queries for the
        languages present in that index are routed through the multilingual retriever.
        The existing English/Hindi behavior is preserved when the multilingual index
        is absent.
        """
        self.indexer_en = VectorIndexer(model_name=model_name, device=device)
        self.indexer_en.load_index(index_dir or "retrieval/indexes/eng_sentence_aware_plain")
        self.retriever_en = DenseRetriever(self.indexer_en)

        # Share the loaded embedding model with Hindi indexer to avoid loading weights twice
        self.indexer_hi = VectorIndexer(model_name=model_name, device=device, shared_model=self.indexer_en.model)
        self.indexer_hi.load_index("retrieval/indexes/hin_sentence_aware_plain")
        self.retriever_hi = DenseRetriever(self.indexer_hi)

        # Optional multilingual indexes. The new local MSMARCO-XI path uses one
        # FAISS directory per language and lazy-loads the requested language.
        # The legacy single-index environment variable is kept for compatibility.
        self.retriever_multi = None
        self.supported_multilingual_codes = frozenset()
        self.multilingual_index_dir = None
        multilingual_index_dir = multilingual_index_dir or os.getenv("MSMARCO_XI_INDEX_DIR")
        multilingual_index_root = os.getenv("MSMARCO_XI_INDEX_ROOT", "retrieval/indexes")
        self.multilingual_index_root = multilingual_index_root
        if multilingual_index_dir:
            try:
                self.multilingual_index_dir = multilingual_index_dir
                self.indexer_multi = VectorIndexer(model_name=model_name, device=device, shared_model=self.indexer_en.model)
                self.indexer_multi.load_index(multilingual_index_dir)
                self.retriever_multi = MultilingualRetriever(self.indexer_multi)
                self.supported_multilingual_codes = frozenset(
                    meta.get("language") for meta in self.indexer_multi.metadata if meta.get("language")
                )
                print(f"[RAG Pipeline] Multilingual index loaded from {multilingual_index_dir} "
                      f"({self.indexer_multi.index.ntotal} vectors, {len(self.supported_multilingual_codes)} languages)")
            except (FileNotFoundError, OSError, ValueError, KeyError) as exc:
                print(f"[RAG Pipeline] Multilingual index at {multilingual_index_dir} could not be loaded: {exc}")
        else:
            available_indexes = available_language_indexes(multilingual_index_root)
            if available_indexes:
                self.retriever_multi = MultilingualRetriever(
                    index_root=multilingual_index_root,
                    model_name=model_name,
                    device=device,
                    shared_model=self.indexer_en.model,
                )
                self.supported_multilingual_codes = frozenset(available_indexes)
                print(f"[RAG Pipeline] MSMARCO-XI language indexes available at {multilingual_index_root}: "
                      f"{sorted(self.supported_multilingual_codes)}")

        self.retriever = self.retriever_hi
        self.llm_client = LLMClient(provider=llm_provider, model=llm_model, timeout=llm_timeout_seconds)

    def _should_use_multilingual(self, active_lang: str) -> bool:
        """
        True when the active language should be served by the multilingual index.

        English queries always stay on the English index; unrecognized or
        absent languages fall back to the existing Hindi/English routing.
        """
        if self.retriever_multi is None or active_lang.startswith("en"):
            return False
        dataset_code = to_msmarco_xi_code(active_lang)
        return dataset_code in self.supported_multilingual_codes

    def answer(self, query: str, language: str = "hi", top_k: int = 5, min_score: float = 0.70, query_id: int = None) -> dict:
        """
        Executes the text RAG pipeline:
        1. Dense retrieval of top-K passages from matching language index.
        2. Strict confidence score threshold check (short-circuits to refusal if below min_score).
        3. Compact context building.
        4. LLM query generation with strict context grounding prompts.
        5. Refusal/grounding check on generated response.
        Returns a structured dictionary with answer, trace, and latencies.
        """
        t_pipeline_start = time.time()
        
        # Route query to Hindi or English index based on language flag or Devanagari script detection
        clean_lang = (language or "hi").strip().lower()
        if clean_lang == "auto":
            active_lang = "hi" if any('\u0900' <= char <= '\u097F' for char in (query or "")) else "en"
        else:
            active_lang = normalize_language_code(clean_lang)

        is_english = active_lang.startswith("en")

        # Route to the multilingual index when it is loaded and the requested
        # language is present in it. English queries keep using the English index.
        use_multi = self._should_use_multilingual(active_lang)

        if use_multi:
            active_retriever = self.retriever_multi
            selected_index = str(
                self.multilingual_index_dir
                or language_index_dir(active_lang, self.multilingual_index_root)
                or ""
            )
        else:
            active_retriever = self.retriever_en if is_english else self.retriever_hi
            selected_index = "retrieval/indexes/eng_sentence_aware_plain" if is_english else "retrieval/indexes/hin_sentence_aware_plain"

        # 1. Retrieval Layer
        retrieve_kwargs = {}
        if use_multi:
            retrieve_kwargs["language"] = active_lang
        retrieved_passages, retrieval_latencies = active_retriever.retrieve(query, k=top_k, **retrieve_kwargs)
        
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
            answer = get_refusal_response(active_lang)
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
            system_prompt = get_system_prompt(active_lang)
            user_prompt = f"Evidence context:\n{context}\n\nUser Query:\n{query}"
            
            answer, llm_request_ms = self.llm_client.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=150,
                temperature=0.0,
                retrieved_passages=limited_passages,
                query_id=query_id,
                language=active_lang
            )
            
            # 5. Post-completions validation
            grounded, refused = evaluator.post_evaluate_generation(answer, active_lang)
            
        total_pipeline_ms = (time.time() - t_pipeline_start) * 1000.0
        
        # Structured output format
        response = {
            "answer": answer,
            "language": active_lang,
            "normalized_language": active_lang,
            "selected_index": selected_index,
            "retrieved_result_count": len(retrieved_passages),
            "top_similarity_score": max([p["score"] for p in retrieved_passages], default=None),
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
