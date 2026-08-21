"""Local-only MSMARCO-XI dataset discovery and schema inference.

This module intentionally does not import Hugging Face helpers or download
anything. It inspects copied Parquet files only when they exist locally.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

from retrieval.languages import DEFAULT_LANGUAGES, normalize_language_code, to_msmarco_xi_code


DATASET_MISSING_MESSAGE = (
    "MSMARCO-XI dataset not found. Set MSMARCO_XI_DATASET_PATH to the extracted dataset directory."
)

SPLITS = ("train", "validation")


class DatasetNotFoundError(FileNotFoundError):
    """Raised when the configured local dataset directory is absent."""


class SchemaInferenceError(RuntimeError):
    """Raised when local Parquet files do not expose usable text fields."""


@dataclass(frozen=True)
class ParquetFileInfo:
    path: Path
    split: str | None
    language: str | None
    dataset_code: str | None
    rows: int
    columns: list[str]
    schema: str
    query_fields: list[str]
    passage_fields: list[str]
    answer_fields: list[str]
    language_fields: list[str]


@dataclass(frozen=True)
class DatasetInspection:
    dataset_path: Path
    exists: bool
    parquet_files: list[ParquetFileInfo]
    missing_languages_by_split: dict[str, list[str]]


def require_dataset_path(dataset_path: Path) -> Path:
    path = Path(dataset_path)
    is_unset = str(path) in {"", "."}
    if is_unset or not path.exists() or not path.is_dir():
        display_path = "<unset>" if is_unset else str(path)
        raise DatasetNotFoundError(
            f"{DATASET_MISSING_MESSAGE} Configured path: {display_path}. "
            "Copy the extracted MSMARCO-XI folder outside this Git repository, then set MSMARCO_XI_DATASET_PATH."
        )
    return path


def discover_parquet_files(dataset_path: Path) -> list[Path]:
    require_dataset_path(dataset_path)
    return sorted(p for p in dataset_path.rglob("*.parquet") if p.is_file())


def _flatten_schema(schema: pa.Schema) -> list[tuple[str, pa.DataType]]:
    fields: list[tuple[str, pa.DataType]] = []

    def visit(prefix: str, field: pa.Field) -> None:
        name = f"{prefix}.{field.name}" if prefix else field.name
        dtype = field.type
        fields.append((name, dtype))
        if pa.types.is_struct(dtype):
            for child in dtype:
                visit(name, child)

    for field in schema:
        visit("", field)
    return fields


def _score_query_field(path: str, dtype: pa.DataType) -> int:
    lower = path.lower()
    if not pa.types.is_string(dtype) and not pa.types.is_large_string(dtype):
        return -1
    score = 0
    if "query" in lower or "question" in lower:
        score += 5
    if "eng" in lower or "english" in lower or "source" in lower:
        score -= 2
    return score


def _score_passage_field(path: str, dtype: pa.DataType) -> int:
    lower = path.lower()
    value_type = dtype.value_type if pa.types.is_list(dtype) or pa.types.is_large_list(dtype) else dtype
    if not (pa.types.is_string(value_type) or pa.types.is_large_string(value_type)):
        return -1
    score = 0
    if any(token in lower for token in ("passage", "document", "doc", "text", "context")):
        score += 5
    if pa.types.is_list(dtype) or pa.types.is_large_list(dtype):
        score += 2
    if any(token in lower for token in ("translated", "target")):
        score += 2
    if "english" in lower or lower.startswith("eng"):
        score -= 2
    if "query" in lower or "answer" in lower:
        score -= 4
    return score


def _matching_fields(schema: pa.Schema, scorer) -> list[str]:
    scored = []
    for path, dtype in _flatten_schema(schema):
        score = scorer(path, dtype)
        if score > 0:
            scored.append((score, path))
    scored.sort(key=lambda item: (-item[0], item[1]))
    return [path for _, path in scored]


def infer_fields(schema: pa.Schema) -> dict[str, list[str]]:
    flat = _flatten_schema(schema)
    answer_fields = [
        path
        for path, dtype in flat
        if "answer" in path.lower() and (pa.types.is_string(dtype) or pa.types.is_large_string(dtype))
    ]
    language_fields = [
        path
        for path, dtype in flat
        if "lang" in path.lower() and (pa.types.is_string(dtype) or pa.types.is_large_string(dtype))
    ]
    return {
        "query_fields": _matching_fields(schema, _score_query_field),
        "passage_fields": _matching_fields(schema, _score_passage_field),
        "answer_fields": sorted(answer_fields),
        "language_fields": sorted(language_fields),
    }


def infer_split(path: Path, dataset_root: Path) -> str | None:
    parts = {part.lower() for part in path.relative_to(dataset_root).parts[:-1]}
    for split in SPLITS:
        if split in parts:
            return split
    name = path.stem.lower()
    if name.endswith("train"):
        return "train"
    if name.endswith("val") or name.endswith("validation"):
        return "validation"
    return None


def infer_language(path: Path) -> tuple[str | None, str | None]:
    stem = path.stem.lower()
    for iso in DEFAULT_LANGUAGES:
        dataset_code = to_msmarco_xi_code(iso)
        if dataset_code and stem.startswith(dataset_code):
            return iso, dataset_code
    return None, None


def inspect_parquet_file(path: Path, dataset_root: Path) -> ParquetFileInfo:
    parquet = pq.ParquetFile(path)
    schema = parquet.schema_arrow
    fields = infer_fields(schema)
    language, dataset_code = infer_language(path)
    return ParquetFileInfo(
        path=path,
        split=infer_split(path, dataset_root),
        language=language,
        dataset_code=dataset_code,
        rows=int(parquet.metadata.num_rows),
        columns=[field.name for field in schema],
        schema=str(schema),
        **fields,
    )


def inspect_dataset(dataset_path: Path) -> DatasetInspection:
    root = require_dataset_path(dataset_path)
    infos = [inspect_parquet_file(path, root) for path in discover_parquet_files(root)]
    present = {(info.split, info.language) for info in infos if info.split and info.language}
    missing = {
        split: [lang for lang in DEFAULT_LANGUAGES if (split, lang) not in present]
        for split in SPLITS
    }
    return DatasetInspection(dataset_path=root, exists=True, parquet_files=infos, missing_languages_by_split=missing)


def find_language_file(dataset_path: Path, language: str, split: str) -> ParquetFileInfo:
    normalized = normalize_language_code(language)
    if normalized not in DEFAULT_LANGUAGES:
        raise ValueError(f"Unsupported MSMARCO-XI language: {language}")
    matches = [
        info
        for info in inspect_dataset(dataset_path).parquet_files
        if info.language == normalized and info.split == split
    ]
    if not matches:
        dataset_code = to_msmarco_xi_code(normalized)
        raise FileNotFoundError(
            f"MSMARCO-XI {split} Parquet file for language '{normalized}' ({dataset_code}) was not found under "
            f"{dataset_path}. Run python -m ingestion.inspect_msmarco_xi to see discovered files."
        )
    return matches[0]


def get_nested_value(row: dict[str, Any], field_path: str) -> Any:
    value: Any = row
    for part in field_path.split("."):
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    return value


def values_as_texts(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        stripped = value.strip()
        return [stripped] if stripped else []
    if isinstance(value, (list, tuple)):
        texts = []
        for item in value:
            if isinstance(item, str) and item.strip():
                texts.append(item.strip())
        return texts
    return []


def first_text(row: dict[str, Any], fields: list[str]) -> str | None:
    for field in fields:
        texts = values_as_texts(get_nested_value(row, field))
        if texts:
            return texts[0]
    return None
