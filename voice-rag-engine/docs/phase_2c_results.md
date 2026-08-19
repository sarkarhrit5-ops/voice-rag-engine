# Phase 2C Results

## Scope and constraints

This Phase 2C work preserves the current retrieval-first architecture and evaluates the production decision points without redesigning the stack. The system remains retrieval confidence gated, with a deterministic threshold before the LLM is invoked. The mock provider is retained and the live provider path is optional via environment variables.

## Threshold sweep (0.65 to 0.85, step 0.02)

Threshold benchmarking is implemented in `evaluation/threshold_benchmark.py` and writes both CSV and Markdown outputs for machine-readable and human-readable review.

The script samples the Hindi validation set and evaluates:

- answerable queries correctly answered
- answerable queries incorrectly refused
- no-answer queries correctly refused
- no-answer queries incorrectly answered
- false-answer rate
- false-refusal rate
- grounded-answer rate
- refusal accuracy
- precision
- recall
- F1

The benchmark should be executed with the project venv using the commands listed in the repository README or the procedure below.

## Scaling benchmark (5,000 queries / ~50,000 passages)

The scaling benchmark requires a representative subset of the validation dataset and a recreated index matching the current sentence_aware_plain strategy. The objective is to record index construction, embedding, FAISS build, latency, and disk footprint, including P50/P70/P100 for the query-time stages.

## Real LLM integration

The provider abstraction in `rag/llm_client.py` supports a real API path for Gemini, Groq, or OpenAI while keeping the mock provider as the default for local development. The project remains runnable without credentials in explicit mock mode; live-provider failures are surfaced as errors rather than being converted into mock answers.

The implementation preserves the requirement that:

- the answer must stay strictly grounded in retrieved context
- the LLM must never use outside knowledge
- retrieval confidence guard runs before the LLM call
- high similarity alone is not treated as automatically answerable

## Known limitations

- No real API credentials were available in the current environment, so the live provider path could not be field-validated end-to-end.
- A production threshold chosen from the mock benchmark is still provisional until a real-provider dataset sweep is run.
- Scaling results are representative of the local CPU environment and may differ on GPU or cloud nodes.
- The benchmark intentionally avoids a full retrieval redesign and focuses on the validated retrieval baseline.

## Recommended architecture for the voice phase

- Keep the current sentence_aware_plain retrieval baseline.
- Keep the deterministic retrieval threshold gate, but preserve the capability to tune it from benchmark output.
- Use the same multi-provider LLM abstraction, with mock mode for local tests and a latency-optimized real provider for production.
- Preserve short-answer, short-context prompting and strict refusal behavior.
- Delay voice/STT integration until after the final threshold and provider benchmark are locked.
