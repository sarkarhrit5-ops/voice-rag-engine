# Local MSMARCO-XI Retrieval

The multilingual RAG integration uses the already-downloaded local AI4Bharat
MSMARCO-XI dataset at:

```env
MSMARCO_XI_DATASET_PATH=D:\MSMARCO-XI
```

Ingestion reads local Parquet files directly. It must not use Hugging Face
streaming, must not download data, and must not copy the 55 GB dataset into
this Git repository.

## Discovered Local Dataset Structure

`D:\MSMARCO-XI` contains:

```text
D:\MSMARCO-XI
  README.md
  ms_marco_translations.py
  .gitattributes
  train\
  validation\
  .cache\
```

Train files discovered:

| File | Rows |
| --- | ---: |
| `train/asmtrain.parquet` | 778,638 |
| `train/bentrain.parquet` | 778,638 |
| `train/gujtrain.parquet` | 778,638 |
| `train/hintrain.parquet` | 778,638 |
| `train/kantrain.parquet` | 778,638 |
| `train/maltrain.parquet` | 778,638 |
| `train/martrain.parquet` | 765,873 |
| `train/neptrain.parquet` | 754,154 |
| `train/oritrain.parquet` | 782,282 |
| `train/pantrain.parquet` | 778,638 |
| `train/santrain.parquet` | 778,638 |
| `train/tamtrain.parquet` | 778,638 |
| `train/urdtrain.parquet` | 770,089 |

No `train/teltrain.parquet` file was present in the local copy during
inspection. Telugu exists in validation.

Validation files discovered:

| File | Rows |
| --- | ---: |
| `validation/asmval.parquet` | 97,941 |
| `validation/benval.parquet` | 97,941 |
| `validation/gujval.parquet` | 97,941 |
| `validation/hinval.parquet` | 97,941 |
| `validation/kanval.parquet` | 97,941 |
| `validation/malval.parquet` | 97,941 |
| `validation/marval.parquet` | 97,941 |
| `validation/nepval.parquet` | 97,941 |
| `validation/orival.parquet` | 97,941 |
| `validation/panval.parquet` | 97,941 |
| `validation/sanval.parquet` | 97,941 |
| `validation/tamval.parquet` | 97,941 |
| `validation/telval.parquet` | 97,941 |
| `validation/urdval.parquet` | 97,941 |

All inspected Parquet files share this schema:

```text
source_lang: string
target_lang: string
meta: struct<
  frequency_penalty: int64,
  max_tokens: int64,
  model_name: string,
  presence_penalty: int64,
  temperature: int64,
  top_p: int64
>
Answer: string
query_id: int64
query_type: string
passages: struct<
  English_passages: list<string>,
  Translated_passages: list<string>,
  is_selected: list<int64>
>
Eng_Query: string
Eng_Answer: string
query: string
```

Each record contains a translated query/answer and candidate passages. The
builder indexes `passages.Translated_passages`, keeps selected English passage
context in metadata, and preserves relevance flags from `passages.is_selected`.

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

## Configuration

```env
MSMARCO_XI_DATASET_PATH=D:\MSMARCO-XI
MSMARCO_XI_SPLIT=train
MSMARCO_XI_INDEX_ROOT=retrieval/indexes
MSMARCO_XI_BATCH_SIZE=64
```

`MSMARCO_XI_INDEX_DIR` is retained only as a legacy single-index override. Leave
it blank to use the language-specific indexes.

## Building Indexes

Build one language from the configured split:

```bash
python -m ingestion.build_msmarco_xi --language hi
```

Build a bounded verification index:

```bash
python -m ingestion.build_msmarco_xi --language hi --max-records 100
```

Force a rebuild when `COMPLETE` already exists:

```bash
python -m ingestion.build_msmarco_xi --language hi --force
```

Build all available languages one-by-one:

```powershell
foreach ($lang in "as","bn","gu","hi","kn","ml","mr","ne","or","pa","sa","ta","ur") {
  python -m ingestion.build_msmarco_xi --language $lang
}
```

For Telugu with the currently inspected local files, use validation unless a
local `train/teltrain.parquet` is added:

```bash
python -m ingestion.build_msmarco_xi --language te --split validation
```

## Index Format

Each complete language directory contains:

```text
faiss_index.index
faiss_index.json
index_metadata.json
checkpoint.json
benchmark.json
benchmark_queries.json
COMPLETE
```

Partial builds use `partial_faiss_index.index` and
`partial_metadata.jsonl`. The production retriever only considers an index
available when `COMPLETE`, final FAISS/JSON files, and `index_metadata.json`
with `"completed": true` all exist.

Metadata includes language, source language, query id, passage index, chunk
index, dataset split, original English query/passage context, translated query,
and translated chunk text. The `text` field remains the translated retrieval
chunk expected by the existing context builder.

## Chunking And Embeddings

The builder reuses `sentence_aware_plain` behavior through
`chunk_sentence_aware(..., max_chars=400)`.

E5 prefixes remain unchanged:

```text
query: <query>
passage: <passage>
```

The embedding model remains `intfloat/multilingual-e5-small`. FAISS remains
`IndexFlatIP` unless benchmark data proves that a future IVF/HNSW/PQ/sharded
design is required.

## Resume Behavior

The build is resumable per language:

1. Existing `COMPLETE` indexes are skipped unless `--force` is supplied.
2. Incomplete builds recover from `partial_faiss_index.index` and
   `partial_metadata.jsonl`.
3. If metadata has extra rows after an interrupted append, it is truncated to
   the partial FAISS vector count.
4. If FAISS has more vectors than metadata, the builder stops rather than
   risking corrupted lookup state.

The final `COMPLETE` marker is written only after FAISS, metadata, checkpoint,
index metadata, and benchmark outputs are saved.

## Runtime Routing

The voice pipeline already passes STT language information into RAG:

```text
hi-IN -> hi -> retrieval/indexes/msmarco_xi_hi/
bn-IN -> bn -> retrieval/indexes/msmarco_xi_bn/
ta-IN -> ta -> retrieval/indexes/msmarco_xi_ta/
```

When a complete language-specific MSMARCO-XI index exists, the RAG pipeline
uses it for that language. English continues to use the existing English index.
If a requested MSMARCO-XI index is missing or incomplete, the existing
English/Hindi fallback behavior is preserved.

Grounding thresholds, refusal behavior, STT, TTS, LLM provider logic, and the
frontend are unchanged.

## Storage And Latency

The 100-record Hindi verification build produced 1,334 vectors and about
4.8 MiB of final FAISS/metadata files in `retrieval/indexes/msmarco_xi_hi/`.

The full per-language FAISS vector storage for 384-dim float32 embeddings is
approximately:

```text
vectors * 384 * 4 bytes
```

Metadata JSON can be larger than the vector file because it stores text. A full
Hindi train build may therefore require many gigabytes of index storage. Build
one language at a time and monitor disk usage.

The 100-record Hindi benchmark observed:

| Stage | P50 ms | P70 ms | P100 ms |
| --- | ---: | ---: | ---: |
| Query embedding | 37.388 | 39.234 | 57.356 |
| FAISS search | 0.324 | 0.344 | 3.571 |
| Metadata lookup | 0.028 | 0.030 | 0.051 |
| Total retrieval | 37.706 | 39.592 | 60.985 |

This excludes STT, LLM, and TTS. The <200 ms retrieval target is maintained for
the verification index. Full-language builds should be benchmarked after each
language completes; if `IndexFlatIP` becomes too slow, evaluate IVF, HNSW,
product quantization, sharding, or memory mapping as a separate measured
architecture change.
