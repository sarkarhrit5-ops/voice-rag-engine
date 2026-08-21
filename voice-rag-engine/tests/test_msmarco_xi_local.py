import json
import subprocess
import sys

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from ingestion.build_msmarco_xi import read_checkpoint
from ingestion.msmarco_xi_local import DatasetNotFoundError, find_language_file, inspect_dataset


def write_fixture_dataset(root):
    train = root / "train"
    validation = root / "validation"
    train.mkdir()
    validation.mkdir()

    schema = pa.schema(
        [
            ("source_lang", pa.string()),
            ("target_lang", pa.string()),
            ("Answer", pa.string()),
            ("query_id", pa.int64()),
            ("query", pa.string()),
            (
                "passages",
                pa.struct(
                    [
                        ("Translated_passages", pa.list_(pa.string())),
                        ("English_passages", pa.list_(pa.string())),
                    ]
                ),
            ),
        ]
    )
    table = pa.Table.from_pylist(
        [
            {
                "source_lang": "eng",
                "target_lang": "hin",
                "Answer": "answer",
                "query_id": 1,
                "query": "question",
                "passages": {
                    "Translated_passages": ["first passage", "second passage"],
                    "English_passages": ["first English passage"],
                },
            }
        ],
        schema=schema,
    )
    pq.write_table(table, train / "hintrain.parquet")
    pq.write_table(table, validation / "hinval.parquet")


def test_missing_dataset_path_fails_gracefully(tmp_path):
    with pytest.raises(DatasetNotFoundError, match="MSMARCO-XI dataset not found"):
        inspect_dataset(tmp_path / "missing")


def test_inspection_reports_schema_and_inferred_fields(tmp_path):
    write_fixture_dataset(tmp_path)

    inspection = inspect_dataset(tmp_path)
    info = find_language_file(tmp_path, "hi-IN", "train")

    assert len(inspection.parquet_files) == 2
    assert info.language == "hi"
    assert info.dataset_code == "hin"
    assert info.rows == 1
    assert "query" in info.query_fields
    assert "passages.Translated_passages" in info.passage_fields
    assert "Answer" in info.answer_fields
    assert "source_lang" in info.language_fields


def test_verify_command_reports_absent_dataset(tmp_path):
    result = subprocess.run(
        [sys.executable, "-m", "ingestion.verify_msmarco_xi", "--dataset-path", str(tmp_path / "missing")],
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    assert "MSMARCO-XI dataset not found" in result.stdout


def test_build_command_reports_absent_dataset_before_embedding_model(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ingestion.build_msmarco_xi",
            "--language",
            "hi",
            "--max-records",
            "10",
            "--dataset-path",
            str(tmp_path / "missing"),
            "--index-root",
            str(tmp_path / "indexes"),
        ],
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    assert "MSMARCO-XI dataset not found" in result.stdout
    assert "Loading embedding model" not in result.stdout


def test_checkpoint_complete_detection_fields(tmp_path):
    index_dir = tmp_path / "msmarco_xi_hi"
    index_dir.mkdir()
    checkpoint = {
        "language": "hi",
        "source_file": str(tmp_path / "train" / "hintrain.parquet"),
        "records_processed": 10,
        "chunks_created": 20,
        "vectors_created": 20,
        "batch_number": 1,
        "embedding_model": "intfloat/multilingual-e5-small",
        "updated_at": "2026-08-21T00:00:00+00:00",
        "status": "COMPLETE",
    }
    (index_dir / "checkpoint.json").write_text(json.dumps(checkpoint), encoding="utf-8")

    assert read_checkpoint(index_dir)["status"] == "COMPLETE"
