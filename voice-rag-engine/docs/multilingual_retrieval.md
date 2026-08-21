# Local MSMARCO-XI Retrieval

The multilingual RAG integration consumes an already-extracted local copy of
AI4Bharat MSMARCO-XI. It does not download data, stream from Hugging Face, or
require the dataset to exist during tests.

Configure the dataset path outside this repository:

```env
MSMARCO_XI_DATASET_PATH=
MSMARCO_XI_SPLIT=train
MSMARCO_XI_INDEX_ROOT=retrieval/indexes
MSMARCO_XI_BATCH_SIZE=64
```

Set `MSMARCO_XI_DATASET_PATH` to the extracted dataset root after the folder is
copied onto this machine.

## Inspection And Verification

Inspect local Parquet files:

```bash
python -m ingestion.inspect_msmarco_xi
```

Verify indexing readiness:

```bash
python -m ingestion.verify_msmarco_xi
```

Both commands fail gracefully when the configured dataset path is missing. When
the dataset exists, they report discovered train and validation files, row
counts from Parquet metadata, columns, nested schema text, language inference,
query fields, passage fields, answer fields, and language fields.

The builder uses the same inspected schema information at runtime, so source
code does not need per-language edits.

## Supported Languages

`retrieval/languages.py` normalizes STT/query codes such as `hi-IN` to ISO
639-1 codes and maps them to MSMARCO-XI dataset codes.

| ISO code | Dataset code | Index directory |
| --- | --- | --- |
| `as` | `asm` | `retrieval/indexes/msmarco_xi_as/` |
| `bn` | `ben` | `retrieval/indexes/msmarco_xi_bn/` |
| `gu` | `guj` | `retrieval/indexes/msmarco_xi_gu/` |
| `hi` | `hin` | `retrieval/indexes/msmarco_xi_hi/` |
| `kn` | `kan` | `retrieval/indexes/msmarco_xi_kn/` |
| `ml` | `mal` | `retrieval/indexes/msmarco_xi_ml/` |
| `mr` | `mar` | `retrieval/indexes/msmarco_xi_mr/` |
| `ne` | `nep` | `retrieval/indexes/msmarco_xi_ne/` |
| `or` | `ori` | `retrieval/indexes/msmarco_xi_or/` |
| `pa` | `pan` | `retrieval/indexes/msmarco_xi_pa/` |
| `sa` | `san` | `retrieval/indexes/msmarco_xi_sa/` |
| `ta` | `tam` | `retrieval/indexes/msmarco_xi_ta/` |
| `te` | `tel` | `retrieval/indexes/msmarco_xi_te/` |
| `ur` | `urd` | `retrieval/indexes/msmarco_xi_ur/` |

## Building Indexes

Build one complete language from the configured split:

```bash
python -m ingestion.build_msmarco_xi --language hi
```

Build a bounded fixture or smoke index:

```bash
python -m ingestion.build_msmarco_xi --language hi --max-records 100
```

Force a rebuild when `COMPLETE` already exists:

```bash
python -m ingestion.build_msmarco_xi --language hi --force
```

The builder writes `retrieval/indexes/msmarco_xi_<lang>/` and reuses the
existing `sentence_aware_plain` chunking behavior with
`intfloat/multilingual-e5-small`.

## Resume Behavior

Each language build writes:

```text
partial_faiss_index.index
partial_metadata.jsonl
checkpoint.json
```

`checkpoint.json` records language, source file, records processed, chunks
created, vectors created, batch number, embedding model, timestamp, and status.
`COMPLETE` is written only after the final FAISS index, metadata JSON, index
metadata, checkpoint, and benchmark output are saved.

If `COMPLETE` exists, the builder skips the language unless `--force` is used.
Incomplete builds recover from the partial FAISS index and JSONL metadata when
their counts match. If the partial state is unsafe, the builder stops with an
actionable error instead of silently corrupting metadata lookup.

## Runtime Routing

The backend keeps the existing API contract. `POST /voice/query` can pass
language-aware requests through the same pipeline:

```text
hi-IN -> hi -> retrieval/indexes/msmarco_xi_hi/
bn-IN -> bn -> retrieval/indexes/msmarco_xi_bn/
ta-IN -> ta -> retrieval/indexes/msmarco_xi_ta/
te-IN -> te -> retrieval/indexes/msmarco_xi_te/
mr-IN -> mr -> retrieval/indexes/msmarco_xi_mr/
gu-IN -> gu -> retrieval/indexes/msmarco_xi_gu/
kn-IN -> kn -> retrieval/indexes/msmarco_xi_kn/
ml-IN -> ml -> retrieval/indexes/msmarco_xi_ml/
pa-IN -> pa -> retrieval/indexes/msmarco_xi_pa/
ur-IN -> ur -> retrieval/indexes/msmarco_xi_ur/
as-IN -> as -> retrieval/indexes/msmarco_xi_as/
ne-IN -> ne -> retrieval/indexes/msmarco_xi_ne/
or-IN -> or -> retrieval/indexes/msmarco_xi_or/
sa-IN -> sa -> retrieval/indexes/msmarco_xi_sa/
```

English continues to use the existing English index. Grounding thresholds,
refusal behavior, STT, TTS, LLM provider logic, and frontend responses are
unchanged.

## Benchmarking

The builder saves `benchmark.json` after a successful build using sampled local
queries from the indexed file. Do not treat any benchmark numbers as available
until the real dataset has been copied here and a real language index has been
built.
