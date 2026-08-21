"""
Deterministic tests for the multilingual MSMARCO-XI retrieval feature.

These tests never download MSMARCO-XI and never load the real embedding model.
A small script-aware fake encoder (same ``query:``/``passage:`` prefix contract
as multilingual-e5) is used to build and query tiny FAISS indexes in memory.
"""

import hashlib
from pathlib import Path

import numpy as np
import pytest

from retrieval.indexer import VectorIndexer
from retrieval.index_store import available_language_indexes, is_complete_index, language_index_dir
from retrieval.languages import normalize_language_code, to_msmarco_xi_code
from retrieval.multilingual_retriever import MultilingualRetriever

EMBEDDING_DIM = 384
REPO_ID = "ai4bharat/MSMARCO-XI"

_LANG_KEYS = ("hin", "ben", "tam", "tel", "mar", "guj", "eng")
_LANG_BASES = {}
_rng = np.random.RandomState(2024)
for _key in _LANG_KEYS:
    _v = _rng.standard_normal(EMBEDDING_DIM).astype("float32")
    _LANG_BASES[_key] = _v / np.linalg.norm(_v)


def _detect_script_language(text: str) -> str:
    """Map the dominant Indic script of text to a dataset language code."""
    for char in text:
        if "\u0980" <= char <= "\u09FF":
            return "ben"
        if "\u0A80" <= char <= "\u0AFF":
            return "guj"
        if "\u0B80" <= char <= "\u0BFF":
            return "tam"
        if "\u0C00" <= char <= "\u0C7F":
            return "tel"
        if "\u0900" <= char <= "\u097F":
            return "hin"
    return "eng"


def _hash_noise(text: str) -> np.ndarray:
    seed = int(hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()[:16], 16) & 0xFFFFFFFF
    local_rng = np.random.RandomState(seed)
    return local_rng.standard_normal(EMBEDDING_DIM).astype("float32") * 0.02


class FakeE5Model:
    """Deterministic stand-in for intfloat/multilingual-e5-small.

    Embeds each string near the base vector of its detected Indic script, so a
    query retrieves documents of the same script first (deterministic), while
    still exercising the real query/passage prefix contract.
    """

    def encode(self, sentences, **kwargs):
        return np.stack([self._encode_one(s) for s in sentences])

    def _encode_one(self, text: str) -> np.ndarray:
        lang = _detect_script_language(str(text))
        vector = _LANG_BASES[lang] + _hash_noise(str(text))
        return (vector / np.linalg.norm(vector)).astype("float32")


HI_DOCS = [
    "कंपनी एक कानूनी इकाई है जो व्यापार संचालित करती है।",
    "भारत की राजधानी नई दिल्ली है।",
    "जलवायु परिवर्तन एक वैश्विक समस्या है।",
    "पुस्तकालय में कई किताबें उपलब्ध हैं।",
    "चाय भारत का लोकप्रिय पेय है।",
    "विद्यालय शिक्षा का केंद्र है।",
]

BN_DOCS = [
    "কোম্পানি একটি আইনি সত্তা যা ব্যবসা পরিচালনা করে।",
    "ভারতের রাজধানী নয়াদিল্লি।",
    "জলবায়ু পরিবর্তন একটি বিশ্বব্যাপী সমস্যা।",
    "গ্রন্থাগারে অনেক বই পাওয়া যায়।",
    "চা ভারতের জনপ্রিয় পানীয়।",
    "বিদ্যালয় শিক্ষার কেন্দ্র।",
]

TA_DOCS = [
    "நிறுவனம் வணிகத்தை நடத்தும் சட்டப்பூர்வ நிறுவனம்.",
    "இந்தியாவின் தலைநகர் புது தில்லி.",
    "பருவநிலை மாற்றம் ஒரு உலகளாவிய பிரச்சனை.",
    "நூலகத்தில் பல புத்தகங்கள் உள்ளன.",
]

# language (dataset code) -> list of fixture passages
FIXTURE_LANGUAGES = {"hin": HI_DOCS, "ben": BN_DOCS, "tam": TA_DOCS}


def _build_fixture_metadata():
    """Deterministic metadata list matching the multilingual index contract."""
    documents = []
    metadatas = []
    for lang, docs in FIXTURE_LANGUAGES.items():
        for i, text in enumerate(docs):
            documents.append(text)
            metadatas.append(
                {
                    "query_id": 1000 + i,
                    "passage_index": i,
                    "chunk_index": 0,
                    "is_selected": 1,
                    "query_type": "DESCRIPTION",
                    "language": lang,
                    "target_lang": f"{lang}_script",
                    "source_lang": "eng_Latn",
                    "dataset": REPO_ID,
                    "record_id": 1000 + i,
                    "text": text,
                }
            )
    return documents, metadatas


@pytest.fixture
def tiny_multilingual_index(tmp_path):
    documents, metadatas = _build_fixture_metadata()
    indexer = VectorIndexer(model_name="fake", shared_model=FakeE5Model())
    indexer.build_index(documents, metadatas, batch_size=8)
    indexer.save_index(str(tmp_path))
    return str(tmp_path)


def _build_complete_language_index(root: Path, iso_language: str, docs: list[str]) -> Path:
    dataset_code = to_msmarco_xi_code(iso_language)
    index_dir = language_index_dir(iso_language, root)
    assert index_dir is not None
    documents = list(docs)
    metadatas = [
        {
            "query_id": 2000 + i,
            "passage_index": i,
            "chunk_index": 0,
            "language": dataset_code,
            "target_language": iso_language,
            "dataset": REPO_ID,
            "record_id": 2000 + i,
            "text": text,
        }
        for i, text in enumerate(documents)
    ]
    indexer = VectorIndexer(model_name="fake", shared_model=FakeE5Model())
    indexer.build_index(documents, metadatas, batch_size=8)
    indexer.save_index(str(index_dir))
    (index_dir / "index_metadata.json").write_text(
        '{"completed": true, "language": "%s", "dataset_code": "%s"}' % (iso_language, dataset_code),
        encoding="utf-8",
    )
    (index_dir / "checkpoint.json").write_text('{"completed": true}', encoding="utf-8")
    (index_dir / "COMPLETE").write_text("complete\n", encoding="utf-8")
    return index_dir


@pytest.fixture
def multilingual_retriever(tiny_multilingual_index):
    indexer = VectorIndexer(model_name="fake", shared_model=FakeE5Model())
    indexer.load_index(tiny_multilingual_index)
    return MultilingualRetriever(indexer)


# --- 4. Language code normalization ------------------------------------------

def test_language_code_normalization():
    assert normalize_language_code("hi-IN") == "hi"
    assert normalize_language_code("hin") == "hi"
    assert normalize_language_code("HIN") == "hi"
    assert normalize_language_code("en-IN") == "en"
    assert to_msmarco_xi_code("hi") == "hin"
    assert to_msmarco_xi_code("hi-IN") == "hin"
    assert to_msmarco_xi_code("bn") == "ben"
    assert to_msmarco_xi_code("ta") == "tam"
    assert to_msmarco_xi_code("te") == "tel"
    assert to_msmarco_xi_code("mr") == "mar"
    assert to_msmarco_xi_code("gu") == "guj"
    assert to_msmarco_xi_code("en") is None
    assert to_msmarco_xi_code("") is None


def test_language_mapping_covers_all_supported_languages():
    for iso in ("as", "bn", "gu", "hi", "kn", "ml", "mr", "ne", "or", "pa", "sa", "ta", "te", "ur"):
        assert to_msmarco_xi_code(iso) is not None


# --- 1. Existing English index still loads -----------------------------------

def test_existing_english_index_still_loads():
    eng_dir = Path(__file__).resolve().parents[1] / "retrieval" / "indexes" / "eng_sentence_aware_plain"
    indexer = VectorIndexer(model_name="fake", shared_model=FakeE5Model())
    indexer.load_index(str(eng_dir))
    assert indexer.index.ntotal > 0
    sample_langs = {meta.get("language") for meta in indexer.metadata[:200]}
    assert "eng" in sample_langs


# --- 2/3. Multilingual index format + metadata -------------------------------

def test_multilingual_index_format_loads(tiny_multilingual_index):
    total_docs = sum(len(docs) for docs in FIXTURE_LANGUAGES.values())
    indexer = VectorIndexer(model_name="fake", shared_model=FakeE5Model())
    indexer.load_index(tiny_multilingual_index)
    assert indexer.index.ntotal == total_docs
    assert len(indexer.metadata) == total_docs


def test_metadata_contains_language_and_dataset(tiny_multilingual_index):
    indexer = VectorIndexer(model_name="fake", shared_model=FakeE5Model())
    indexer.load_index(tiny_multilingual_index)
    assert all("language" in meta for meta in indexer.metadata)
    assert all(meta.get("dataset") == REPO_ID for meta in indexer.metadata)
    assert all("record_id" in meta for meta in indexer.metadata)
    assert all("target_lang" in meta for meta in indexer.metadata)
    assert {meta["language"] for meta in indexer.metadata} == {"hin", "ben", "tam"}


# --- 5/6. Language-filtered retrieval ----------------------------------------

def test_hindi_query_retrieves_hindi_fixture(multilingual_retriever):
    results, latencies = multilingual_retriever.retrieve("भारत की राजधानी क्या है?", k=5, language="hi")
    assert results
    assert all(r["metadata"]["language"] == "hin" for r in results)
    assert latencies["total_retrieval_ms"] >= 0.0
    assert latencies["query_embedding_ms"] >= 0.0
    assert latencies["faiss_search_ms"] >= 0.0
    assert latencies["metadata_lookup_ms"] >= 0.0


def test_bengali_query_retrieves_bengali_fixture(multilingual_retriever):
    results, _ = multilingual_retriever.retrieve("ভারতের রাজধানী কী?", k=5, language="bn")
    assert results
    assert all(r["metadata"]["language"] == "ben" for r in results)


def test_region_code_filter_matches_same_language(multilingual_retriever):
    results, _ = multilingual_retriever.retrieve("ভারতের রাজধানী কী?", k=5, language="bn-IN")
    assert results
    assert all(r["metadata"]["language"] == "ben" for r in results)


# --- 7. Cross-language retrieval stays possible ------------------------------

def test_cross_language_retrieval_without_filter(multilingual_retriever):
    results, _ = multilingual_retriever.retrieve("भारत की राजधानी क्या है?", k=5)
    assert results
    # Global search may surface any language; the language filter is disabled.
    assert len(results) == 5
    scores = [r["score"] for r in results]
    assert scores == sorted(scores, reverse=True)


def test_unrecognized_language_falls_back_to_global_search(multilingual_retriever):
    results, _ = multilingual_retriever.retrieve("भारत की राजधानी क्या है?", k=5, language="en")
    assert results
    assert len(results) == 5


def test_local_dataset_path_configuration(monkeypatch):
    monkeypatch.setenv("MSMARCO_XI_DATASET_PATH", r"D:\MSMARCO-XI")
    monkeypatch.setenv("MSMARCO_XI_INDEX_ROOT", "retrieval/indexes")
    monkeypatch.setenv("MSMARCO_XI_BATCH_SIZE", "64")

    from retrieval.index_store import get_batch_size, get_dataset_path, get_index_root

    assert str(get_dataset_path()) == r"D:\MSMARCO-XI"
    assert str(get_index_root()) == "retrieval\\indexes" or str(get_index_root()) == "retrieval/indexes"
    assert get_batch_size() == 64


def test_language_index_selection(tmp_path):
    hi_dir = language_index_dir("hi-IN", tmp_path)
    bn_dir = language_index_dir("bn", tmp_path)

    assert hi_dir == tmp_path / "msmarco_xi_hi"
    assert bn_dir == tmp_path / "msmarco_xi_bn"
    assert language_index_dir("en", tmp_path) is None


def test_completed_index_detection(tmp_path):
    index_dir = tmp_path / "msmarco_xi_hi"
    index_dir.mkdir()
    assert is_complete_index(index_dir) is False

    (index_dir / "faiss_index.index").write_bytes(b"index")
    (index_dir / "faiss_index.json").write_text("[]", encoding="utf-8")
    (index_dir / "index_metadata.json").write_text('{"completed": false}', encoding="utf-8")
    (index_dir / "COMPLETE").write_text("complete\n", encoding="utf-8")
    assert is_complete_index(index_dir) is False

    (index_dir / "index_metadata.json").write_text('{"completed": true}', encoding="utf-8")
    assert is_complete_index(index_dir) is True


def test_incomplete_index_without_complete_is_not_available(tmp_path):
    index_dir = _build_complete_language_index(tmp_path, "hi", HI_DOCS[:2])
    (index_dir / "COMPLETE").unlink()

    assert is_complete_index(index_dir) is False
    assert available_language_indexes(tmp_path) == {}


def test_language_specific_lazy_retrieval_routes_hindi_and_bengali(tmp_path):
    _build_complete_language_index(tmp_path, "hi", HI_DOCS)
    _build_complete_language_index(tmp_path, "bn", BN_DOCS)

    retriever = MultilingualRetriever(index_root=tmp_path, model_name="fake", shared_model=FakeE5Model())

    hi_results, hi_latencies = retriever.retrieve("à¤­à¤¾à¤°à¤¤ à¤•à¥€ à¤°à¤¾à¤œà¤§à¤¾à¤¨à¥€ à¤•à¥à¤¯à¤¾ à¤¹à¥ˆ?", k=3, language="hi-IN")
    bn_results, _ = retriever.retrieve("à¦­à¦¾à¦°à¦¤à§‡à¦° à¦°à¦¾à¦œà¦§à¦¾à¦¨à§€ à¦•à§€?", k=3, language="bn")

    assert hi_results
    assert bn_results
    assert all(r["metadata"]["language"] == "hin" for r in hi_results)
    assert all(r["metadata"]["language"] == "ben" for r in bn_results)
    assert hi_latencies["metadata_lookup_ms"] >= 0.0


def test_missing_language_specific_index_raises(tmp_path):
    retriever = MultilingualRetriever(index_root=tmp_path, model_name="fake", shared_model=FakeE5Model())

    with pytest.raises(FileNotFoundError):
        retriever.retrieve("à¤­à¤¾à¤°à¤¤ à¤•à¥€ à¤°à¤¾à¤œà¤§à¤¾à¤¨à¥€ à¤•à¥à¤¯à¤¾ à¤¹à¥ˆ?", k=3, language="hi")


def test_available_language_indexes_reports_completed_only(tmp_path):
    _build_complete_language_index(tmp_path, "hi", HI_DOCS[:2])
    incomplete_bn = _build_complete_language_index(tmp_path, "bn", BN_DOCS[:2])
    (incomplete_bn / "index_metadata.json").write_text('{"completed": false}', encoding="utf-8")

    available = available_language_indexes(tmp_path)
    assert set(available) == {"hin"}


# --- 8. Pipeline routing decision (deterministic, no model/index load) -------

def test_pipeline_routing_uses_multilingual_for_supported_languages():
    from rag.pipeline import TextRAGPipeline

    pipe = object.__new__(TextRAGPipeline)
    pipe.retriever_multi = object()
    pipe.supported_multilingual_codes = frozenset({"hin", "ben", "tam", "tel", "mar", "guj"})
    assert pipe._should_use_multilingual("hi") is True
    assert pipe._should_use_multilingual("bn") is True
    assert pipe._should_use_multilingual("ta") is True
    assert pipe._should_use_multilingual("te") is True

    pipe.retriever_multi = None
    assert pipe._should_use_multilingual("hi") is False

    pipe.retriever_multi = object()
    pipe.supported_multilingual_codes = frozenset({"hin"})
    assert pipe._should_use_multilingual("en") is False
    assert pipe._should_use_multilingual("fr") is False


def test_language_specific_index_paths_for_required_languages(tmp_path):
    assert language_index_dir("bn-IN", tmp_path) == tmp_path / "msmarco_xi_bn"
    assert language_index_dir("hi-IN", tmp_path) == tmp_path / "msmarco_xi_hi"
    assert language_index_dir("ta-IN", tmp_path) == tmp_path / "msmarco_xi_ta"


# --- 10. No production provider APIs during pytest ---------------------------

def test_no_network_calls_during_multilingual_retrieval(tmp_path, monkeypatch):
    def _fail(*args, **kwargs):
        raise AssertionError("Unexpected network/provider call during pytest")

    import requests

    monkeypatch.setattr(requests, "post", _fail)
    monkeypatch.setattr(requests, "get", _fail)
    monkeypatch.setattr("datasets.load_dataset", _fail)

    documents, metadatas = _build_fixture_metadata()
    indexer = VectorIndexer(model_name="fake", shared_model=FakeE5Model())
    indexer.build_index(documents, metadatas, batch_size=8)
    indexer.save_index(str(tmp_path))

    loaded = VectorIndexer(model_name="fake", shared_model=FakeE5Model())
    loaded.load_index(str(tmp_path))
    retriever = MultilingualRetriever(loaded)

    results, _ = retriever.retrieve("भारत की राजधानी क्या है?", k=3, language="hi")
    assert results
    assert all(r["metadata"]["language"] == "hin" for r in results)
