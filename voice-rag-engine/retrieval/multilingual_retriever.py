"""Language-aware retrieval for MSMARCO-XI indexes."""

from pathlib import Path

from retrieval.index_store import available_language_indexes, is_complete_index, language_index_dir
from retrieval.indexer import VectorIndexer
from retrieval.retriever import DenseRetriever
from retrieval.languages import to_msmarco_xi_code


class MultilingualRetriever(DenseRetriever):
    """
    Dense retriever with two compatible modes.

    When constructed with ``indexer`` it preserves the previous single-index
    metadata-filtering behavior. When constructed with ``index_root`` it lazily
    loads one complete ``retrieval/indexes/msmarco_xi_<lang>`` directory per
    requested language and runs the existing dense retrieval against that index.
    """

    # How many extra candidates to fetch from the global index before filtering
    # by language. Oversampling is generous but bounded so that the top-k of the
    # requested language are not silently lost to other languages.
    LANGUAGE_PROBE_MULTIPLIER = 6
    LANGUAGE_PROBE_MIN = 30

    def __init__(
        self,
        indexer=None,
        index_root: str | Path = "retrieval/indexes",
        model_name: str = "intfloat/multilingual-e5-small",
        device: str = "cpu",
        shared_model=None,
    ):
        self.single_index_mode = indexer is not None
        self.index_root = Path(index_root)
        self.model_name = model_name
        self.device = device
        self.shared_model = shared_model
        self._retrievers_by_dataset_code = {}

        if self.single_index_mode:
            super().__init__(indexer)
        else:
            self.indexer = None

    def available_dataset_codes(self) -> frozenset[str]:
        if self.single_index_mode:
            return frozenset(meta.get("language") for meta in self.indexer.metadata if meta.get("language"))
        return frozenset(available_language_indexes(self.index_root))

    def _load_language_retriever(self, language: str) -> DenseRetriever | None:
        dataset_code = to_msmarco_xi_code(language)
        if dataset_code is None:
            return None
        if dataset_code in self._retrievers_by_dataset_code:
            return self._retrievers_by_dataset_code[dataset_code]

        index_dir = language_index_dir(language, self.index_root)
        if index_dir is None or not is_complete_index(index_dir):
            return None

        indexer = VectorIndexer(model_name=self.model_name, device=self.device, shared_model=self.shared_model)
        indexer.load_index(str(index_dir))
        retriever = DenseRetriever(indexer)
        self._retrievers_by_dataset_code[dataset_code] = retriever
        return retriever

    def retrieve(self, query_text: str, k: int = 5, language: str = None) -> tuple[list[dict], dict]:
        if not self.single_index_mode:
            active = self._load_language_retriever(language) if language else None
            if active is None:
                raise FileNotFoundError(f"No complete MSMARCO-XI index is available for language={language!r}")
            return active.retrieve(query_text, k=k)

        dataset_code = to_msmarco_xi_code(language) if language else None
        if dataset_code is None:
            # No filter (or unrecognized language): fall back to global search.
            return super().retrieve(query_text, k=k)

        probe_k = max(k * self.LANGUAGE_PROBE_MULTIPLIER, self.LANGUAGE_PROBE_MIN)
        results, latencies = super().retrieve(query_text, k=probe_k)

        filtered = [r for r in results if r["metadata"].get("language") == dataset_code]
        return filtered[:k], latencies
