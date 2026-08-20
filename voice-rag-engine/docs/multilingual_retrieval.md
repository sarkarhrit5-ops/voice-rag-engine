# Multilingual Retrieval with MSMARCO-XI

This document describes the multilingual retrieval feature: a single FAISS
index over representative subsets of the AI4Bharat
[`ai4bharat/MSMARCO-XI`](https://huggingface.co/datasets/ai4bharat/MSMARCO-XI)
dataset, served by the existing dense retrieval layer without 14 separate RAG
pipelines.

> [!IMPORTANT]
> The full MSMARCO-XI dataset is ~55 GB in converted form. This feature
> **never requires the full dataset locally**. It streams only the bounded
> subset actually consumed (per-language record caps), so a representative
> multilingual index can be built from a few hundred records per language.

---

## 1. Source dataset

* **Repo:** `ai4bharat/MSMARCO-XI` (Hugging Face Hub, `repo_type="dataset"`)
* **Content:** MS MARCO (English) queries/answers/passages machine-translated
  into 14 Indic languages (`as, bn, gu, hi, kn, ml, mr, ne, or, pa, sa, ta,
  te, ur`).
* **Structure:** one parquet file per language per split, e.g.
  `validation/hinval.parquet`, `validation/benval.parquet`.
* **Schema (inspect, do not assume):**
  * `query` / `Eng_Query` — target-language / English query
  * `query_id` — unique record id
  * `query_type` — `DESCRIPTION`, `NUMERIC`, `ENTITY`, `PERSON`, `LOCATION`
  * `passages.Translated_passages` / `passages.English_passages` — candidate passages
  * `passages.is_selected` — 1 when the passage answers the query
  * `Answer` / `Eng_Answer`, `source_lang` / `target_lang` (e.g. `eng_Latn` / `hin_Deva`),
    `meta` (translation-model generation params)

Only `Translated_passages` (the target-language passages) are indexed.

## 2. Supported languages

Language codes exist in two conventions; `retrieval/languages.py` is the single
conversion point.

| ISO 639-1 (query/STT) | MSMARCO-XI dataset code | Script range (for reference) |
| --- | --- | --- |
| `hi` | `hin` | Devanagari |
| `bn` | `ben` | Bengali |
| `ta` | `tam` | Tamil |
| `te` | `tel` | Telugu |
| `mr` | `mar` | Devanagari |
| `gu` | `guj` | Gujarati |
| `kn` | `kan` | Kannada |
| `ml` | `mal` | Malayalam |
| `pa` | `pan` | Gurmukhi |
| `ur` | `urd` | Urdu |
| `as` | `asm` | Assamese |
| `ne` | `nep` | Devanagari |
| `or` / `od` | `ori` | Odia |
| `sa` | `san` | Devanagari |

The first wave enables `hi, bn, ta, te, mr, gu`. All 14 are already mapped in
`retrieval/languages.py`; enabling more is a CLI argument change (see §5).

## 3. Controlled subset behavior

* Per-language record cap, configurable:
  * CLI: `--max-records-per-language`
  * Env: `MSMARCO_XI_MAX_RECORDS_PER_LANGUAGE` (default `50000`)
* Streaming only: `datasets.load_dataset(..., streaming=True)` fetches only the
  consumed subset from the Hub — no full-file download.
* Bounded + restartable:
  * per-language checkpoints are written to
    `<output>/checkpoints/<dataset_code>.parquet` before embedding;
  * an interrupted run can continue with `--resume`, skipping languages that
    already completed;
  * the embedding/index step is then driven entirely from the local checkpoints.
* Per-language reporting: language, records processed, passages processed,
  records (chunks) indexed; plus global embedding time, index creation time and
  final index size. A `build_report.json` is written next to the index.

## 4. Index format & metadata

The multilingual index uses the exact same contract as the existing English
index (`VectorIndexer` → FAISS `IndexFlatIP` + a parallel metadata JSON), so the
existing `DenseRetriever`/pipeline code paths work unchanged.

* Embedding model: `intfloat/multilingual-e5-small` (reused — not replaced).
* Query prefix `query: ` and passage prefix `passage: ` are preserved.
* Output: `retrieval/indexes/msmarco_xi_multilingual/faiss_index.index` +
  `faiss_index.json`.

Each metadata entry carries the existing fields (`query_id`, `passage_index`,
`chunk_index`, `is_selected`, `query_type`, `language`, `text`) plus:

```json
{
  "target_lang": "hin_Deva",
  "source_lang": "eng_Latn",
  "dataset": "ai4bharat/MSMARCO-XI",
  "record_id": 1102432,
  "meta": { "model_name": "ckpt-3epochs-sft-then-400k-kd", "temperature": 0 }
}
```

`language` holds the MSMARCO-XI dataset code (`hin`, `ben`, ...) so language
filtering is unambiguous. The existing English index
(`retrieval/indexes/eng_sentence_aware_plain`) is never modified.

## 5. Building the multilingual index

```bash
# Representative subset, all six first-wave languages
python -m ingestion.build_msmarco_xi \
    --languages hi,bn,ta,te,mr,gu \
    --max-records-per-language 100 \
    --benchmark-queries 60
```

Configuration (CLI or env):

| Option | Env var | Default |
| --- | --- | --- |
| languages | `MSMARCO_XI_LANGUAGES` | `hi,bn,ta,te,mr,gu` |
| max records / language | `MSMARCO_XI_MAX_RECORDS_PER_LANGUAGE` | `50000` |
| split | `MSMARCO_XI_SPLIT` | `validation` |
| output index dir | `MSMARCO_XI_OUTPUT_INDEX` | `retrieval/indexes/msmarco_xi_multilingual` |
| benchmark queries / lang | `MSMARCO_XI_BENCHMARK_QUERIES` | `100` |

To benchmark an already-built index without re-embedding:

```bash
python -m ingestion.build_msmarco_xi \
    --languages hi,bn,ta,te,mr,gu \
    --benchmark-queries 60 \
    --benchmark-only
```

### Adding more languages

The code mapping already covers all 14 MSMARCO-XI languages. To enable, for
example, Kannada and Malayalam:

```bash
python -m ingestion.build_msmarco_xi \
    --languages hi,bn,ta,te,mr,gu,kn,ml \
    --max-records-per-language 50000
```

The retriever derives routable languages from the index metadata at load time,
so no pipeline code changes are required.

## 6. RAG integration

The existing flow is unchanged:

```
STT → query → embedding → FAISS → context → LLM → answer
```

Only index selection became multilingual-aware. Enable the multilingual index
in the RAG pipeline with the `MSMARCO_XI_INDEX_DIR` environment variable (or
the `multilingual_index_dir` constructor argument):

```env
MSMARCO_XI_INDEX_DIR=retrieval/indexes/msmarco_xi_multilingual
```

Routing rules (`rag/pipeline.py`):

* English queries always use the existing English index.
* Non-English queries whose language is present in the multilingual index use
  the multilingual retriever with that language's filter.
* Everything else falls back to the existing English/Hindi routing — fully
  backward compatible when the multilingual index is absent.
* Language-aware filtering oversamples the global index then filters by the
  metadata `language`; with no language supplied, the whole index is searched
  normally (cross-language retrieval stays possible).
* Grounding thresholds, refusal behavior, LLM response parsing, STT and TTS
  are untouched.

## 7. Expected storage requirements

Local disk usage equals **only the subset you build**:

* Demonstration build (100 records/language × 6 languages → 7,202 chunks):
  **~19 MB** index (FAISS + metadata), plus tiny per-language checkpoints.
* Default cap (50,000 records/language × 6 languages → ~3.5 M chunks): roughly
  **10–15 GB** on disk and many hours of streaming + CPU embedding. This is
  optional and not needed for the feature to work.

The full ~55 GB dataset is never downloaded.

## 8. Retrieval benchmark results

Measured on the demonstration index (7,202 vectors, 60 queries stratified
10/language, mock mode, CPU) — `evaluation/multilingual_retrieval_benchmark.json`:

| Stage | P50 (ms) | P70 (ms) | P100 (ms) |
| --- | ---: | ---: | ---: |
| Query embedding | 16.2 | 16.8 | 42.0 |
| FAISS search | 0.6 | 0.7 | 1.0 |
| Metadata lookup | 0.05 | 0.06 | 0.08 |
| **Total retrieval** | **16.9** | **17.5** | **42.8** |

Retrieval stays well below the <200 ms target. These figures exclude LLM, STT
and TTS; the mock LLM's translation fallback is **not** counted as retrieval
latency. FAISS search scales near-linearly with vector count for this
`IndexFlatIP` layout, so a larger index mainly raises the embedding stage of
the same budget.