"""
Language-aware retrieval over a single multilingual FAISS index.

The multilingual index stores passages from several MSMARCO-XI languages in a
single FAISS ``IndexFlatIP``. FAISS does not support native metadata filtering,
so language filtering is implemented by oversampling the global index and then
re-ranking the surviving candidates by their metadata language. When no
language filter is supplied the underlying dense search is used unchanged,
which keeps cross-language retrieval possible.
"""

from retrieval.retriever import DenseRetriever
from retrieval.languages import to_msmarco_xi_code


class MultilingualRetriever(DenseRetriever):
    """
    Dense retriever over a single multilingual index with an optional
    language filter.

    ``retrieve(query_text, k=5, language=None)`` is backward compatible with
    ``DenseRetriever.retrieve``: without a ``language`` value it searches the
    whole index normally.
    """

    # How many extra candidates to fetch from the global index before filtering
    # by language. Oversampling is generous but bounded so that the top-k of the
    # requested language are not silently lost to other languages.
    LANGUAGE_PROBE_MULTIPLIER = 6
    LANGUAGE_PROBE_MIN = 30

    def retrieve(self, query_text: str, k: int = 5, language: str = None) -> tuple[list[dict], dict]:
        dataset_code = to_msmarco_xi_code(language) if language else None
        if dataset_code is None:
            # No filter (or unrecognized language): fall back to global search.
            return super().retrieve(query_text, k=k)

        probe_k = max(k * self.LANGUAGE_PROBE_MULTIPLIER, self.LANGUAGE_PROBE_MIN)
        results, latencies = super().retrieve(query_text, k=probe_k)

        filtered = [r for r in results if r["metadata"].get("language") == dataset_code]
        return filtered[:k], latencies