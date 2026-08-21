"""Verify whether the local extracted MSMARCO-XI dataset is ready to index."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from ingestion.inspect_msmarco_xi import print_text_report
from ingestion.msmarco_xi_local import DatasetNotFoundError, inspect_dataset
from retrieval.index_store import get_dataset_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify local MSMARCO-XI readiness.")
    parser.add_argument("--dataset-path", type=Path, default=get_dataset_path(), help="Local extracted MSMARCO-XI root.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        inspection = inspect_dataset(args.dataset_path)
    except DatasetNotFoundError as exc:
        print(f"[Not Ready] {exc}")
        sys.exit(1)

    print_text_report(inspection)
    files = inspection.parquet_files
    missing_train = inspection.missing_languages_by_split.get("train", [])
    missing_validation = inspection.missing_languages_by_split.get("validation", [])
    unusable = [info for info in files if not info.passage_fields]

    print("=" * 72)
    if not files:
        print("[Not Ready] No local Parquet files were discovered.")
        sys.exit(1)
    if unusable:
        print("[Not Ready] Some Parquet files have no detectable passage/document text field:")
        for info in unusable:
            print(f"  - {info.path}")
        sys.exit(1)
    if missing_train and missing_validation:
        print("[Not Ready] Supported language files are missing from both train and validation splits.")
        print(f"Missing train: {', '.join(missing_train)}")
        print(f"Missing validation: {', '.join(missing_validation)}")
        sys.exit(1)

    print("[Ready] Local MSMARCO-XI files are discoverable and expose indexable text fields.")
    if missing_train:
        print(f"[Warning] Missing train languages: {', '.join(missing_train)}")
    if missing_validation:
        print(f"[Warning] Missing validation languages: {', '.join(missing_validation)}")


if __name__ == "__main__":
    main()
