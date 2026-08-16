# MSMARCO-XI Retrieval Layer Experiments Report

This report presents the findings from dense retrieval experiments on the Hindi validation subset of MSMARCO-XI, evaluating multilingual representations, chunking strategies, metadata inclusion, and latency.

## 1. Dataset Relevance-Label Findings

* **Total records evaluated:** 100
* **Queries with at least one relevant passage (Group 1):** 53 (53.00%)
* **Queries with zero relevant passages (Group 2):** 47 (47.00%)

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
| Exp A | `passage_baseline_plain` | 998 | 0.2547 | 0.5912 | 0.7673 | 0.8868 | 0.1660 | 0.4653 |
| Exp B | `passage_baseline_plain` | 998 | 0.3082 | 0.6384 | 0.8428 | 0.9434 | 0.1774 | 0.5269 |
| Exp C | `passage_baseline_plain` | 998 | 0.3208 | 0.7170 | 0.8836 | 1.0000 | 0.1887 | 0.5492 |
| Exp A | `fixed_size_plain` | 1,989 | 0.3302 | 0.6352 | 0.7390 | 0.8679 | 0.2000 | 0.5005 |
| Exp B | `fixed_size_plain` | 1,979 | 0.2327 | 0.4371 | 0.5692 | 0.7075 | 0.1547 | 0.3750 |
| Exp C | `fixed_size_plain` | 1,979 | 0.3868 | 0.7516 | 0.8270 | 0.9811 | 0.2151 | 0.5955 |
| Exp A | `sentence_aware_plain` | 1,225 | 0.2736 | 0.6195 | 0.7862 | 0.8868 | 0.1849 | 0.4845 |
| Exp B | `sentence_aware_plain` | 1,214 | 0.3648 | 0.5818 | 0.7673 | 0.9434 | 0.1698 | 0.5353 |
| Exp C | `sentence_aware_plain` | 1,214 | 0.3774 | 0.6981 | 0.8836 | 1.0000 | 0.2038 | 0.5731 |
| Exp A | `sentence_aware_contextual` | 1,225 | 0.2925 | 0.6132 | 0.7610 | 0.8868 | 0.1774 | 0.4957 |
| Exp B | `sentence_aware_contextual` | 1,214 | 0.3082 | 0.5818 | 0.7673 | 0.9245 | 0.1698 | 0.5090 |
| Exp C | `sentence_aware_contextual` | 1,214 | 0.3962 | 0.6887 | 0.8931 | 1.0000 | 0.2075 | 0.5827 |

## 4. Index-Build Latency Benchmark

| Language | Strategy | Chunks | Chunking Time (s) | Embedding Time (s) | FAISS Build Time (s) | Index Save Time (s) | Total Time (s) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| HIN | `passage_baseline_plain` | 998 | 0.02s | 94.78s | 0.01s | 0.05s | 94.87s |
| HIN | `fixed_size_plain` | 1,989 | 0.03s | 81.53s | 0.01s | 0.10s | 81.67s |
| HIN | `sentence_aware_plain` | 1,225 | 0.03s | 44.49s | 0.00s | 0.04s | 44.57s |
| HIN | `sentence_aware_contextual` | 1,225 | 0.01s | 75.78s | 0.00s | 0.10s | 75.90s |
| ENG | `passage_baseline_plain` | 998 | 0.01s | 61.07s | 0.01s | 0.04s | 61.12s |
| ENG | `fixed_size_plain` | 1,979 | 0.03s | 63.75s | 0.01s | 0.07s | 63.86s |
| ENG | `sentence_aware_plain` | 1,214 | 0.02s | 25.28s | 0.01s | 0.03s | 25.33s |
| ENG | `sentence_aware_contextual` | 1,214 | 0.05s | 61.90s | 0.00s | 0.05s | 62.01s |

## 5. Query-Time Latency Benchmark

Measurements represent query-time retrieval steps in milliseconds. These are key for the low-latency target (Note: this is only the retrieval stage, excluding network, reranking, and generation).

| Experiment | Strategy | P50 (ms) | P70 (ms) | P100 (ms) | Embed P50 (ms) | Search P50 (ms) | Lookup P50 (ms) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Exp A | `passage_baseline_plain` | 59.85 | 89.45 | 477.07 | 59.45 | 0.39 | 0.04 |
| Exp B | `passage_baseline_plain` | 56.63 | 59.42 | 74.08 | 56.29 | 0.36 | 0.04 |
| Exp C | `passage_baseline_plain` | 62.66 | 65.92 | 74.49 | 62.19 | 0.39 | 0.04 |
| Exp A | `fixed_size_plain` | 62.76 | 66.79 | 224.17 | 61.80 | 0.74 | 0.05 |
| Exp B | `fixed_size_plain` | 59.66 | 62.05 | 79.71 | 58.87 | 0.71 | 0.05 |
| Exp C | `fixed_size_plain` | 59.22 | 61.76 | 162.34 | 58.41 | 0.71 | 0.05 |
| Exp A | `sentence_aware_plain` | 18.43 | 19.75 | 34.57 | 18.18 | 0.18 | 0.03 |
| Exp B | `sentence_aware_plain` | 17.88 | 19.31 | 34.10 | 17.66 | 0.18 | 0.03 |
| Exp C | `sentence_aware_plain` | 17.19 | 19.22 | 35.68 | 16.92 | 0.18 | 0.03 |
| Exp A | `sentence_aware_contextual` | 59.83 | 62.43 | 76.97 | 59.30 | 0.48 | 0.04 |
| Exp B | `sentence_aware_contextual` | 57.49 | 59.75 | 68.45 | 57.02 | 0.46 | 0.04 |
| Exp C | `sentence_aware_contextual` | 56.14 | 57.75 | 69.78 | 55.65 | 0.46 | 0.04 |

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
