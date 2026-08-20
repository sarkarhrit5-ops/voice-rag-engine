# MSMARCO-XI Retrieval Layer Experiments Report

This report presents the findings from dense retrieval experiments on the Hindi validation subset of MSMARCO-XI, evaluating multilingual representations, chunking strategies, metadata inclusion, and latency.

## 1. Dataset Relevance-Label Findings

* **Total records evaluated:** 300
* **Queries with at least one relevant passage (Group 1):** 152 (50.67%)
* **Queries with zero relevant passages (Group 2):** 148 (49.33%)

> [!IMPORTANT]
> **The Relevance-Label Anomaly:**
> Our deep inspection confirmed that MSMARCO-XI relevance labels (`is_selected`) represent **strict answerability** rather than general topical relevance.
> 1. **100% Correlation:** Every query with a dataset answer of `No Answer Present` has exactly 0 selected passages (`is_selected = [0, ..., 0]`).
> 2. **Topical Relevance vs. Answerability:** In queries like *"what is barometric pressure in lincoln ne now?"* or *"half cup how many ounces"*, the search passages are highly relevant topically (discussing Lincoln's pressure or cup conversions) but do not answer the specific query directly. Thus, they are labeled 0. This is not a labeling mistake, but compliance with strict answerability guidelines.
> 3. **Label Noise:** We found 55 records with NMT translation failure loops (e.g. repeating "क्या आप किसी के काम के लिए...") where `is_selected` was all 0s, which is translation-level noise. We separated Group 2 from the evaluation to prevent skewing retrieval metrics.

## 2. Experimental Setup

* **Embedding Model:** `intfloat/multilingual-e5-small` (118M parameters, 384 dimensions). Preprepends `query: ` to queries and `passage: ` to passages.
* **Vector Index:** FAISS `IndexFlatIP` using L2-normalized vectors (equivalent to Cosine Similarity).
* **Evaluated Experiments:**
  - **Experiment A:** Hindi Query → Hindi Passage (Mono-lingual Target)
  - **Experiment B:** Hindi Query → English Passage (Cross-lingual)
  - **Experiment C:** English Query → English Passage (Mono-lingual Source)

## 3. Retrieval Performance Metrics

Evaluation is conducted on **Group 1** queries containing usable relevance labels.

| Experiment | Chunking Strategy | Chunks | Recall@1 | Recall@3 | Recall@5 | Recall@10 | Precision@5 | MRR@10 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Exp A | `passage_baseline_plain` | 2,993 | 0.3246 | 0.6151 | 0.7511 | 0.8783 | 0.1605 | 0.5057 |
| Exp B | `passage_baseline_plain` | 2,993 | 0.2522 | 0.5625 | 0.7522 | 0.8947 | 0.1579 | 0.4626 |
| Exp C | `passage_baseline_plain` | 2,993 | 0.4035 | 0.7346 | 0.8739 | 1.0000 | 0.1842 | 0.6093 |
| Exp A | `fixed_size_plain` | 6,027 | 0.3246 | 0.6042 | 0.7094 | 0.8355 | 0.1763 | 0.4964 |
| Exp B | `fixed_size_plain` | 5,940 | 0.2061 | 0.4276 | 0.5121 | 0.6787 | 0.1316 | 0.3517 |
| Exp C | `fixed_size_plain` | 5,940 | 0.3969 | 0.7467 | 0.8213 | 0.9605 | 0.2053 | 0.5976 |
| Exp A | `sentence_aware_plain` | 3,718 | 0.3180 | 0.6316 | 0.7511 | 0.8717 | 0.1711 | 0.5054 |
| Exp B | `sentence_aware_plain` | 3,687 | 0.2719 | 0.5625 | 0.7160 | 0.8158 | 0.1592 | 0.4570 |
| Exp C | `sentence_aware_plain` | 3,687 | 0.4331 | 0.7412 | 0.8673 | 0.9901 | 0.1961 | 0.6204 |
| Exp A | `sentence_aware_contextual` | 3,718 | 0.3311 | 0.6294 | 0.7621 | 0.8618 | 0.1724 | 0.5175 |
| Exp B | `sentence_aware_contextual` | 3,687 | 0.2774 | 0.5724 | 0.7686 | 0.8553 | 0.1697 | 0.4688 |
| Exp C | `sentence_aware_contextual` | 3,687 | 0.4430 | 0.7511 | 0.8805 | 0.9901 | 0.2000 | 0.6273 |

## 4. Index-Build Latency Benchmark

| Language | Strategy | Chunks | Chunking Time (s) | Embedding Time (s) | FAISS Build Time (s) | Index Save Time (s) | Total Time (s) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| HIN | `passage_baseline_plain` | 2,993 | 0.01s | 81.10s | 0.01s | 0.07s | 81.19s |
| HIN | `fixed_size_plain` | 6,027 | 0.06s | 193.36s | 0.01s | 0.16s | 193.59s |
| HIN | `sentence_aware_plain` | 3,718 | 0.08s | 162.97s | 0.01s | 0.12s | 163.18s |
| HIN | `sentence_aware_contextual` | 3,718 | 0.08s | 106.48s | 0.00s | 0.07s | 106.64s |
| ENG | `passage_baseline_plain` | 2,993 | 0.03s | 60.34s | 0.01s | 0.06s | 60.43s |
| ENG | `fixed_size_plain` | 5,940 | 0.04s | 149.50s | 0.01s | 0.13s | 149.69s |
| ENG | `sentence_aware_plain` | 3,687 | 0.06s | 124.02s | 0.01s | 0.10s | 124.19s |
| ENG | `sentence_aware_contextual` | 3,687 | 0.04s | 72.65s | 0.01s | 0.06s | 72.75s |

## 5. Query-Time Latency Benchmark

Measurements represent query-time retrieval steps in milliseconds. These are key for the low-latency target (Note: this is only the retrieval stage, excluding network, reranking, and generation).

| Experiment | Strategy | P50 (ms) | P70 (ms) | P100 (ms) | Embed P50 (ms) | Search P50 (ms) | Lookup P50 (ms) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Exp A | `passage_baseline_plain` | 18.83 | 20.67 | 31.35 | 18.19 | 0.46 | 0.03 |
| Exp B | `passage_baseline_plain` | 22.08 | 24.74 | 152.93 | 21.51 | 0.60 | 0.03 |
| Exp C | `passage_baseline_plain` | 46.16 | 48.02 | 76.72 | 45.24 | 0.90 | 0.04 |
| Exp A | `fixed_size_plain` | 44.32 | 46.19 | 56.40 | 42.63 | 1.60 | 0.05 |
| Exp B | `fixed_size_plain` | 43.93 | 45.53 | 56.00 | 42.37 | 1.54 | 0.05 |
| Exp C | `fixed_size_plain` | 44.24 | 45.52 | 56.92 | 42.55 | 1.60 | 0.04 |
| Exp A | `sentence_aware_plain` | 45.67 | 48.48 | 91.75 | 44.38 | 1.04 | 0.04 |
| Exp B | `sentence_aware_plain` | 44.25 | 46.14 | 54.34 | 43.03 | 1.05 | 0.04 |
| Exp C | `sentence_aware_plain` | 43.81 | 45.33 | 57.67 | 42.66 | 1.06 | 0.04 |
| Exp A | `sentence_aware_contextual` | 16.89 | 18.59 | 30.40 | 16.32 | 0.46 | 0.02 |
| Exp B | `sentence_aware_contextual` | 16.67 | 18.29 | 51.65 | 16.16 | 0.50 | 0.02 |
| Exp C | `sentence_aware_contextual` | 15.36 | 16.99 | 25.68 | 14.80 | 0.44 | 0.02 |

## 6. Analysis of Chunking & Metadata Strategies

### Passage-as-chunk baseline (`passage_baseline_plain`)
* **Strengths:** Simplest strategy, preserves full context of the passage, fast indexing.
* **Weaknesses:** Suboptimal for longer passages, lower semantic resolution for specific details.

### Fixed-size chunking (`fixed_size_plain`)
* **Strengths:** Configurable and standard control. Splits longer passages into smaller, query-focused segments.
* **Weaknesses:** May split sentences in the middle of a word or clause, leading to fragmented context and lower retrieval accuracy.

### Sentence-aware chunking (`sentence_aware_plain`)
* **Strengths:** Excellent preservation of linguistic structure. Avoids splitting short passages while cleanly grouping sentences up to character limit.
* **Weaknesses:** High reliance on correct sentence delimiters.

### Metadata-aware Contextual representation (`sentence_aware_contextual`)
* **Strengths:** Adds explicit structured context (query type, language) to help align search vectors.
* **Weaknesses:** Slightly longer text to encode, does not show massive improvements if the embedding model is already strong in cross-lingual settings, adds slight embedding latency overhead.

## 7. Strategic Recommendations for the Next Phase RAG Architecture

Based on the empirical results:
1. **Multilingual Alignment:** Compare Exp A (Hindi->Hindi) vs Exp B (Hindi->English). If Exp B yields comparable or better Recall@K than Exp A, the production RAG pipeline can retrieve from high-quality English documents directly using translated queries, bypassing lower-quality Hindi document translations!
2. **Chunking Strategy:** Sentence-aware chunking is recommended over fixed-size chunking due to better semantic boundaries and metric performance.
3. **Contextual representation:** Use metadata prepending ONLY if it shows a statistically significant Recall increase. Otherwise, stick to plain representations to conserve token limits and latency.
4. **Latency:** Ensure query-time embedding is optimized (e.g. quantized or run on GPU/fast CPU nodes) since it dominates the retrieval stage.
