"""Helpers for MSMARCO-XI language-specific FAISS index locations."""

from __future__ import annotations

import json
import os
from pathlib import Path

from voice.config import load_env_config
from retrieval.languages import normalize_language_code, to_msmarco_xi_code


DEFAULT_MSMARCO_XI_DATASET_PATH = r"D:\MSMARCO-XI"
DEFAULT_MSMARCO_XI_SPLIT = "train"
DEFAULT_MSMARCO_XI_INDEX_ROOT = "retrieval/indexes"
DEFAULT_MSMARCO_XI_BATCH_SIZE = 64


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def get_dataset_path() -> Path:
    load_env_config()
    return Path(os.getenv("MSMARCO_XI_DATASET_PATH", DEFAULT_MSMARCO_XI_DATASET_PATH))


def get_split() -> str:
    load_env_config()
    return os.getenv("MSMARCO_XI_SPLIT", DEFAULT_MSMARCO_XI_SPLIT)


def get_index_root() -> Path:
    load_env_config()
    return Path(os.getenv("MSMARCO_XI_INDEX_ROOT", DEFAULT_MSMARCO_XI_INDEX_ROOT))


def get_batch_size() -> int:
    load_env_config()
    return max(1, _get_int("MSMARCO_XI_BATCH_SIZE", DEFAULT_MSMARCO_XI_BATCH_SIZE))


def language_index_dir(language: str, index_root: str | Path | None = None) -> Path | None:
    iso = normalize_language_code(language)
    if not iso or to_msmarco_xi_code(iso) is None:
        return None
    root = Path(index_root) if index_root is not None else get_index_root()
    return root / f"msmarco_xi_{iso}"


def is_complete_index(index_dir: str | Path) -> bool:
    directory = Path(index_dir)
    if not (directory / "COMPLETE").is_file():
        return False
    if not (directory / "faiss_index.index").is_file():
        return False
    if not (directory / "faiss_index.json").is_file():
        return False
    metadata_path = directory / "index_metadata.json"
    if not metadata_path.is_file():
        return False
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    return bool(metadata.get("completed"))


def available_language_indexes(index_root: str | Path | None = None) -> dict[str, Path]:
    root = Path(index_root) if index_root is not None else get_index_root()
    if not root.exists():
        return {}
    available = {}
    for child in root.glob("msmarco_xi_??"):
        if not child.is_dir() or not is_complete_index(child):
            continue
        iso = child.name.removeprefix("msmarco_xi_")
        dataset_code = to_msmarco_xi_code(iso)
        if dataset_code:
            available[dataset_code] = child
    return available
