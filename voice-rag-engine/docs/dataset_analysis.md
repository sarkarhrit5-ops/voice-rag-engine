# Dataset Analysis Report: MSMARCO-XI

This report contains the findings from the inspection of the AI4Bharat MSMARCO-XI dataset (`ai4bharat/MSMARCO-XI`) and outlines architectural recommendations for a low-latency voice-enabled RAG pipeline.

---

## 1. Measured Facts

The following statistics are measured directly from the `ai4bharat/MSMARCO-XI` dataset using a reproducible sample size of 1,000 queries (random seed = 42) from the validation split of two target languages: Hindi (`hin`) and Assamese (`asm`).

### A. Dataset Overview & Volume
- **Train split:** 10,080,140 examples (~129.8 GB)
- **Validation split:** 1,371,174 examples (~16.7 GB)
- **Language configuration:** The dataset uses a single `default` configuration, but data files are split by language directories.
- **Available Languages (Train):** Assamese (`asm`), Bengali (`ben`), Gujarati (`guj`), Hindi (`hin`), Kannada (`kan`), Malayalam (`mal`), Marathi (`mar`), Nepali (`nep`), Oriya (`ori`), Punjabi (`pan`), Santhali (`san`), Tamil (`tam`), Urdu (`urd`).
- **Available Languages (Validation):** Same as train, plus Telugu (`tel`). (Note: Telugu is validation-only in this dataset).
- **Parallel Translation Structure:** The validation subsets for both Hindi and Assamese contain the exact same number of examples (**97,941**) and share identical `query_id` listings. This indicates that MSMARCO-XI is a parallel dataset where the same underlying English MS MARCO queries and passages are translated across all 13-14 target Indic languages.

### B. Schema & Data Types
The schema consists of 10 columns:
1. `source_lang` (string): Source language identifier (typically `eng_Latn`).
2. `target_lang` (string): Target Indic language identifier (e.g., `hin_Deva` or `asm_Beng`).
3. `meta` (struct/dict): Metadata containing generation parameters of the translation model:
   - `frequency_penalty` (int64)
   - `max_tokens` (int64)
   - `model_name` (string) - Example: `ckpt-3epochs-sft-then-400k-kd`
   - `presence_penalty` (int64)
   - `temperature` (int64)
   - `top_p` (int64)
4. `Answer` (string): Translated ground-truth answer in the target language.
5. `query_id` (int64): Unique query identifier.
6. `query_type` (string): Classification of the query.
7. `passages` (struct/dict): Contains list features mapping original and translated contexts:
   - `English_passages` (list of strings): Original English candidate passages.
   - `Translated_passages` (list of strings): Translated candidate passages in the target language.
   - `is_selected` (list of int64): Binary flags (0 or 1) indicating if the passage is relevant to the query.
8. `Eng_Query` (string): Original English query.
9. `Eng_Answer` (string): Original English answer.
10. `query` (string): Translated query in the target language.

### C. Text Length Statistics (Validation Split, 1000 Sample Queries, Seed 42)

| Statistic | English (Query / Answer / Passage) | Hindi (`hin`) (Query / Answer / Passage) | Assamese (`asm`) (Query / Answer / Passage) |
| :--- | :--- | :--- | :--- |
| **Query Char Length** (Mean / P50 / Max) | 36.3 / 34 / 134 | 45.2 / 34 / 7,562 | 35.8 / 33 / 141 |
| **Query Word Count** (Mean / P50 / Max) | 6.4 / 6 / 21 | 8.6 / 7 / 1,261 | 5.6 / 5 / 21 |
| **Answer Char Length** (Mean / P50 / Max) | 60.1 / 18 / 539 | 84.3 / 20 / 7,524 | 65.4 / 26 / 3,275 |
| **Answer Word Count** (Mean / P50 / Max) | 10.4 / 4 / 94 | 17.8 / 4 / 2,020 | 10.5 / 5 / 456 |
| **Passage Char Length** (Mean / P50 / P90 / Max) | 320.7 / 296 / 504 / 1,262 | 326.6 / 292 / 489 / 9,486 | 316.9 / 282 / 473 / 4,787 |
| **Passage Word Count** (Mean / P50 / P90 / Max) | 56.4 / 52 / 88 / 222 | 62.2 / 56 / 93 / 4,000 | 48.6 / 43 / 73 / 1,419 |

*Note on Outliers:* There are a small number of extremely long queries and answers (e.g., maximum Hindi query is 7,562 characters / 1,261 words, and maximum passage is 9,486 characters / 4,000 words). These likely represent raw lists, tables, or parsing errors in the underlying MS MARCO source dataset.

### D. Query Type Distribution (Measured across 1,000 samples)
- **DESCRIPTION:** 56.3%
- **NUMERIC:** 24.8%
- **ENTITY:** 8.5%
- **PERSON:** 5.6%
- **LOCATION:** 4.8%

### E. Ground Truth & Redundancy
- **Duplicate Queries in Full Validation Set:** 
  - Hindi: 234 duplicate queries out of 97,941 (0.24%)
  - Assamese: 168 duplicate queries out of 97,941 (0.17%)
  This indicates that query duplication is extremely low, and almost all rows represent unique query IDs.

---

## 2. Retrieval-Oriented Analysis (RAG Specifics)

### A. Passage-Query Cardinality & Selection
- **Passages per Query:** The dataset contains a mean of **9.97** passages per query (ranging between a minimum of 4 and a maximum of 10).
- **Selected (Relevant) Passages:** The mean number of selected (ground-truth relevant) passages per query is only **0.59** (ranging between 0 and 4).
- **Selected Ratio:** On average, only **5.9%** of candidate passages are marked as relevant.
- **Zero Relevant Passages (Ungrounded Queries):**
  - **46.0%** of the sample queries (460 out of 1000) have **exactly 0 relevant passages** (i.e. `is_selected` is a list of all zeros).
  - This matches the answer distributions: **45.7%** of Hindi queries have the placeholder answer `"कोई उत्तर नहीं मिला।"` (and English `"No Answer Present."`).
  - **Key RAG Implication:** Almost half of the query space consists of ungrounded queries where the retriever should yield low similarity scores, and the generator must output a refusal response rather than hallucinating an answer.

### B. Query-Passage Relationships as Evaluation Set
- Because we have a clear mapping between `query_id`, `query`, and the specific subset of `Translated_passages` marked `is_selected = 1`, **this dataset serves as an ideal ground-truth retrieval evaluation set.**
- We can index all `Translated_passages` from the validation set (or a subset of it) and measure retrieval metrics (MRR, Recall@K, nDCG) by checking if our vector retrieval returns the passages marked `is_selected = 1`.

---

## 3. Engineering Recommendations

The following recommendations are proposed based on the observed dataset features and the requirement for a voice-enabled RAG pipeline.

### A. Suitable Chunking Strategies to Test
1. **Document-Level Preservation (No Chunking):** 
   - *Rationale:* Since the P90 passage length is under 500 characters (~90 words) and P99 is under 750 characters (~140 words), the passages in MSMARCO-XI are already naturally chunked. Testing the indexing of the raw passages as complete documents is highly recommended.
2. **Semantic / Sentence-Level Splitting:**
   - *Rationale:* A small percentage of passages contain outlier lengths (up to 9,500 characters). We should test a hybrid chunker that preserves the raw passage if it is below 1,000 characters, but uses sentence boundary splitting (using Indic NLP tools or spaCy) for longer outliers to ensure dense embeddings remain focused.
3. **Fixed-Size Overlapping Chunking (Baseline):**
   - *Rationale:* To serve as a control group, test a standard 256-character chunk size with a 50-character overlap.

### B. Useful Metadata to Preserve
- `query_id`: Crucial to map retrieved passages back to their parent query for benchmarking.
- `passage_index` (within the parent query): Useful to check context positioning.
- `target_lang`: Required to filter vector queries by the language of the voice input.
- `query_type`: Helpful for error logging and evaluating performance across different question formats (e.g. numeric vs description).

### C. Retrieval Approach
- **Dense Retrieval (Semantic Search):** Essential for voice-enabled input to capture semantic meaning, especially to handle speech-to-text transcription noise, typos, and phonetic variants.
- **Sparse Retrieval (BM25):** Good for `NUMERIC` (24.8%) and `ENTITY` (8.5%) queries which rely on exact keyword matches (names, quantities, dates).
- **Hybrid Retrieval (Dense + Sparse):** Highly recommended. Combining dense semantic embeddings with sparse indexes (e.g. BM25 on Indic text) is likely to provide the highest retrieval accuracy across the different query types.

### D. Possible Reranking Strategy
- *Recommendation:* Test a lightweight, low-latency multilingual cross-encoder (e.g. `BAAI/bge-reranker-base` or Cohere Multilingual Rerank) on the top 10 retrieved documents.
- *Caveat:* Rerankers add CPU/GPU overhead. We must measure if the accuracy gain justifies the latency cost under the 200 ms budget.

### E. Evaluation Metrics
1. **Retrieval Layer:**
   - **Recall@K (K=3, 5, 10):** Percentage of queries where the ground-truth relevant passage (`is_selected=1`) is retrieved.
   - **MRR (Mean Reciprocal Rank):** Evaluates how high the first relevant passage is ranked.
2. **Generation Layer:**
   - **Groundedness / Hallucination Rate:** Percentage of generated answers that are strictly supported by the retrieved context.
   - **Refusal Rate Accuracy:** Precision of generating a "No Answer" response when no relevant passages exist.
3. **Voice Layer:**
   - **Word Error Rate (WER):** To evaluate speech-to-text accuracy.

---

## 4. Engineering Hypotheses (To Be Benchmarked)

The following hypotheses must be validated through experimental benchmarks in subsequent development phases:

### Hypothesis 1: Pipeline Latency Budget
We hypothesize that to meet the **200 ms target** for the RAG pipeline (from query text input to answer generation), the sub-components must be budgeted as follows:
- **Query Preprocessing:** < 5 ms
- **Vector Retrieval:** < 15 ms (requires in-memory DB or index optimized for speed)
- **Reranking:** < 20 ms
- **Prompt Construction:** < 5 ms
- **LLM Answer Generation:** < 150 ms (requires ultra-fast inference APIs, such as Groq or Gemini Flash, with short max token limits of 50-100 tokens, or token-by-token streaming).

### Hypothesis 2: Multilingual Embedding Performance
We hypothesize that native Indic-trained embedding models (such as AI4Bharat's `IndicBERT` or multilingual models like `text-embedding-3-small` or `intfloat/multilingual-e5-base`) will yield higher retrieval recall on translated Indic text than general English-first models.

### Hypothesis 3: Transcribed Query Noise Robustness
We hypothesize that dense retrieval will degrade less than sparse retrieval (BM25) when query transcripts contain phonetically similar but incorrectly spelled words introduced by the Speech-to-Text engine.

---

## 5. Proposed Next Phase

Based on the dataset findings and latency constraints, the recommended plan for the next phase (Phase 2) is:

1. **Embedding & Vector DB Setup:**
   - Spin up a local low-latency vector database (e.g., Qdrant or Milvus).
   - Select candidate multilingual embedding models (e.g. `multilingual-e5-small`, `cohere-embed-multilingual-v3.0`).
2. **Benchmark Environment Ingestion:**
   - Index the validation passages for a subset of the languages (e.g., Hindi and Assamese).
   - Keep the metadata (`query_id`, `target_lang`) intact.
3. **Retrieval Evaluation Benchmarking:**
   - Build a benchmark runner that executes the 1,000 sampled queries.
   - Run retrieval experiments comparing Dense, Sparse, and Hybrid approaches.
   - Measure P50, P70, and P100 latency for each retrieval configuration.
4. **LLM Generation & Grounding Tests:**
   - Construct RAG prompts using retrieved context.
   - Test low-latency LLM endpoints (e.g. Groq Llama-3-8b, Gemini 1.5 Flash).
   - Implement basic guardrails to check for ungrounded queries and verify if the LLM successfully output Refusals for the 46.0% "No Answer" cases.
