"""
Language code mapping and normalization for multilingual retrieval.

MSMARCO-XI (ai4bharat/MSMARCO-XI) addresses each Indic language with a
3-letter dataset code (e.g. ``hin``) while the rest of this project uses ISO
639-1 2-letter codes (e.g. ``hi``) and STT region codes (e.g. ``hi-IN``).
This module is the single place that converts between the two conventions.

The mapping covers all 14 MSMARCO-XI languages. The ingestion CLI selects a
representative subset of them; the remaining languages can be enabled later
without code changes.
"""

ISO_639_1_TO_MSMARCO_XI = {
    "as": "asm",
    "bn": "ben",
    "gu": "guj",
    "hi": "hin",
    "kn": "kan",
    "ml": "mal",
    "mr": "mar",
    "ne": "nep",
    "od": "ori",
    "or": "ori",
    "pa": "pan",
    "sa": "san",
    "ta": "tam",
    "te": "tel",
    "ur": "urd",
}

MSMARCO_XI_TO_ISO_639_1 = {v: k for k, v in ISO_639_1_TO_MSMARCO_XI.items()}

# Canonical 3-letter dataset codes, used as the value of the metadata
# ``language`` field inside the multilingual index.
MSMARCO_XI_DATASET_CODES = frozenset(MSMARCO_XI_TO_ISO_639_1)

# Full MSMARCO-XI language set supported by the local index builder.
DEFAULT_LANGUAGES = ("as", "bn", "gu", "hi", "kn", "ml", "mr", "ne", "or", "pa", "sa", "ta", "te", "ur")

# Dataset split filenames use a language-specific suffix (e.g. ``hinval``).
SPLIT_FILE_SUFFIX = {
    "validation": "val",
    "train": "train",
}


def normalize_language_code(code: str) -> str:
    """
    Normalize any supported language identifier to its ISO 639-1 code.

    Handles ``hi-IN``, ``hi``, ``HIN`` and ``hin`` -> ``hi``. Unrecognized
    codes are returned lower-cased and stripped of any region suffix so the
    caller can decide what to do with them (e.g. ``en-IN`` -> ``en``).
    """
    if not code:
        return ""
    raw = str(code).strip().lower().split("-")[0]
    if raw in ISO_639_1_TO_MSMARCO_XI:
        return raw
    if raw in MSMARCO_XI_TO_ISO_639_1:
        return MSMARCO_XI_TO_ISO_639_1[raw]
    return raw


def to_msmarco_xi_code(code: str):
    """
    Map any supported language identifier to its MSMARCO-XI 3-letter code.

    Returns ``None`` for languages that are not part of MSMARCO-XI
    (e.g. ``en``).
    """
    norm = normalize_language_code(code)
    if not norm:
        return None
    return ISO_639_1_TO_MSMARCO_XI.get(norm)
