# voice-rag-engine
Low-latency voice-enabled RAG pipeline with intelligent chunking, vector retrieval, grounded answer generation, latency analytics, and model guardrails.

## Backend API

Install dependencies:

```bash
pip install -r requirements.txt
```

Create `.env` from `.env.example` and fill only the provider keys you intend to use. Keep local development on the mock LLM unless you are explicitly testing a live model:

```env
LLM_PROVIDER=mock
LLM_MODEL=mock-low-latency
VOICE_RAG_ENABLE_TTS=false
VOICE_RAG_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

Start the API:

```bash
uvicorn api.main:app --host 127.0.0.1 --port 8000
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Voice query example:

```bash
curl -X POST http://127.0.0.1:8000/voice/query \
  -H "X-Request-ID: local-smoke-1" \
  -F "audio=@voice/test_audio/audio.wav;type=audio/wav"
```

Interactive API docs are available at `http://127.0.0.1:8000/docs`.

Current limitation: real Groq authentication has worked in this environment, but the accessible Groq text models have not produced usable final `message.content` answers. The backend preserves that failure honestly; it does not use reasoning text or mock fallback as a fake live-model success path.

## Multilingual retrieval (MSMARCO-XI)

The retrieval layer supports multilingual retrieval over representative subsets
of the AI4Bharat MSMARCO-XI dataset through a single FAISS index — no 14
separate RAG pipelines, and no full 55 GB dataset download. See
[`docs/multilingual_retrieval.md`](docs/multilingual_retrieval.md).

Enable the built index in the RAG pipeline:

```env
MSMARCO_XI_INDEX_DIR=retrieval/indexes/msmarco_xi_multilingual
```

Build (or extend) the index:

```bash
python -m ingestion.build_msmarco_xi \
    --languages hi,bn,ta,te,mr,gu \
    --max-records-per-language 100 \
    --benchmark-queries 60
```

The existing English index and the STT → query → embedding → FAISS → context →
LLM → answer flow are unchanged.
