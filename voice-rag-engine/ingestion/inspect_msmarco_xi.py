"""Inspect a local extracted MSMARCO-XI dataset without downloading anything."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from ingestion.msmarco_xi_local import DatasetNotFoundError, inspect_dataset
from retrieval.index_store import get_dataset_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect local MSMARCO-XI Parquet files.")
    parser.add_argument("--dataset-path", type=Path, default=get_dataset_path(), help="Local extracted MSMARCO-XI root.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    return parser.parse_args()


def inspection_to_dict(inspection) -> dict:
    return {
        "dataset_path": str(inspection.dataset_path),
        "exists": inspection.exists,
        "files": [
            {
                "path": str(info.path),
                "split": info.split,
                "language": info.language,
                "dataset_code": info.dataset_code,
                "rows": info.rows,
                "columns": info.columns,
                "query_fields": info.query_fields,
                "passage_fields": info.passage_fields,
                "answer_fields": info.answer_fields,
                "language_fields": info.language_fields,
                "schema": info.schema,
            }
            for info in inspection.parquet_files
        ],
        "missing_languages_by_split": inspection.missing_languages_by_split,
    }


def print_text_report(inspection) -> None:
    print("=" * 72)
    print("MSMARCO-XI LOCAL DATASET INSPECTION")
    print("=" * 72)
    print(f"Dataset path: {inspection.dataset_path}")
    print(f"Parquet files: {len(inspection.parquet_files)}")
    print()

    for split in ("train", "validation"):
        split_files = [info for info in inspection.parquet_files if info.split == split]
        print(f"{split.title()} files: {len(split_files)}")
        for info in split_files:
            rel = info.path.relative_to(inspection.dataset_path)
            print(f"  - {rel} | language={info.language or '?'} | rows={info.rows}")
            print(f"    columns: {', '.join(info.columns) or '(none)'}")
            print(f"    query fields: {', '.join(info.query_fields) or '(not detected)'}")
            print(f"    passage fields: {', '.join(info.passage_fields) or '(not detected)'}")
            print(f"    answer fields: {', '.join(info.answer_fields) or '(not detected)'}")
            print(f"    language fields: {', '.join(info.language_fields) or '(not detected)'}")
        missing = inspection.missing_languages_by_split.get(split) or []
        print(f"  Missing supported languages: {', '.join(missing) if missing else 'none detected'}")
        print()

    unknown = [info for info in inspection.parquet_files if info.split not in ("train", "validation")]
    if unknown:
        print("Unclassified Parquet files:")
        for info in unknown:
            print(f"  - {info.path.relative_to(inspection.dataset_path)} | rows={info.rows}")


def main() -> None:
    args = parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        inspection = inspect_dataset(args.dataset_path)
    except DatasetNotFoundError as exc:
        print(f"[Error] {exc}")
        sys.exit(1)

    if args.json:
        print(json.dumps(inspection_to_dict(inspection), ensure_ascii=False, indent=2))
    else:
        print_text_report(inspection)


if __name__ == "__main__":
    main()
