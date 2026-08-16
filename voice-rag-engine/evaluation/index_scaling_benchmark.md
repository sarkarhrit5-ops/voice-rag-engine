# Index scaling benchmark

- Sampled Hindi validation queries: 5000
- Indexed chunks: 50000
- Index size on disk: 92.91 MB
- Chunking time: 0.78s
- Embedding time: 2923.12s
- FAISS build time: 0.13s

## Retrieval latency percentiles (ms)

| stage | P50 | P70 | P100 |
| --- | ---: | ---: | ---: |
| query_embedding_ms | 59.89 | 66.45 | 292.00 |
| faiss_search_ms | 11.43 | 13.03 | 69.27 |
| retrieval_total_ms | 72.36 | 80.10 | 304.65 |
