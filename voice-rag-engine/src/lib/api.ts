import type { VoiceQueryError, VoiceQueryResponse } from "../types";

type BackendVoiceResponse = VoiceQueryResponse & {
  transcript?: string;
  refused?: boolean;
  tts_audio_base64?: string | null;
  retrieved_passages?: Array<Record<string, unknown>>;
  scores?: number[];
  latency_ms?: {
    query_embedding_ms?: number;
    vector_search_ms?: number;
    faiss_search_ms?: number;
    metadata_lookup_ms?: number;
    context_construction_ms?: number;
    llm_request_ms?: number;
    total_rag_ms?: number;
    total_ms?: number;
  };
  retrieval_latency_ms?: number;
  generation_latency_ms?: number;
  stt_latency_ms?: number;
  query_embedding_ms?: number;
  vector_search_ms?: number;
  faiss_search_ms?: number;
  metadata_lookup_ms?: number;
  context_construction_ms?: number;
  rag_latency_ms?: number;
  llm_latency_ms?: number;
  tts_latency_ms?: number;
  total_latency_ms?: number;
};

export interface BackendHealthResponse {
  status: string;
  service: string;
  version: string;
  request_id: string;
}

const CONFIGURED_API_BASE_URL = (
  import.meta.env.VITE_VOICE_RAG_API_URL ??
  import.meta.env.VITE_API_BASE_URL ??
  ""
).trim();

const REQUEST_TIMEOUT_MS = 70_000;

export function getApiBaseUrl() {
  return CONFIGURED_API_BASE_URL;
}

export function isBackendConfigured() {
  return getApiBaseUrl().length > 0;
}

export async function getBackendHealth(): Promise<BackendHealthResponse> {
  if (!isBackendConfigured()) {
    throw new Error("BACKEND_NOT_CONFIGURED");
  }

  try {
    const response = await fetch(buildApiUrl("/health"));
    const payload = (await response.json().catch(() => null)) as BackendHealthResponse | VoiceQueryError | null;

    if (!response.ok) {
      throw new Error(extractErrorMessage(payload, "Backend health check failed."));
    }
    if (!payload || !("status" in payload)) {
      throw new Error("Backend health check returned an invalid response.");
    }

    return payload;
  } catch (error) {
    throw normalizeFetchError(error);
  }
}

export async function sendVoiceQuery(audio: Blob, language: string): Promise<VoiceQueryResponse> {
  if (!isBackendConfigured()) {
    throw new Error("BACKEND_NOT_CONFIGURED");
  }

  const form = new FormData();
  form.append("audio", audio, "query.webm");
  form.append("language", language);

  const controller = new AbortController();
  const timeoutId = window.setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  try {
    const response = await fetch(buildApiUrl("/voice/query"), {
      method: "POST",
      body: form,
      signal: controller.signal,
    });

    const payload = (await response.json().catch(() => null)) as
      | BackendVoiceResponse
      | VoiceQueryError
      | null;

    if (!response.ok) {
      throw new Error(extractErrorMessage(payload, "Voice query failed."));
    }

    if (!payload || !("answer" in payload)) {
      throw new Error("Voice query returned an invalid response.");
    }

    return normalizeVoiceResponse(payload);
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new Error("TIMEOUT");
    }
    throw normalizeFetchError(error);
  } finally {
    window.clearTimeout(timeoutId);
  }
}

function buildApiUrl(path: string) {
  return `${getApiBaseUrl().replace(/\/$/, "")}${path}`;
}

function extractErrorMessage(payload: VoiceQueryError | BackendHealthResponse | null, fallback: string) {
  if (payload && "detail" in payload && typeof payload.detail === "string") {
    return payload.detail;
  }
  if (payload && "error" in payload) {
    return typeof payload.error === "string" ? payload.error : fallback;
  }
  return fallback;
}

function normalizeFetchError(error: unknown) {
  if (error instanceof TypeError) {
    return new Error(`FastAPI is unavailable at ${getApiBaseUrl()}. Start the backend and restart the Vite dev server if the API URL changed.`);
  }
  return error;
}

export function decodeAudioBase64(audioBase64: string) {
  const binary = window.atob(audioBase64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i += 1) {
    bytes[i] = binary.charCodeAt(i);
  }
  return URL.createObjectURL(new Blob([bytes], { type: "audio/mpeg" }));
}

function normalizeVoiceResponse(payload: BackendVoiceResponse): VoiceQueryResponse {
  const transcription = payload.transcription ?? payload.transcript ?? "";
  const normalizedLanguage =
    payload.normalized_language ?? normalizeLanguageCode(payload.language ?? payload.language_code);
  const sources = payload.sources ?? mapSources(payload.retrieved_passages);

  return {
    ...payload,
    transcription,
    refusal: payload.refusal ?? payload.refused ?? false,
    language: normalizedLanguage,
    normalized_language: normalizedLanguage,
    sources,
    audio_base64: payload.audio_base64 ?? payload.tts_audio_base64 ?? undefined,
    latency: payload.latency ?? normalizeLatency(payload),
  };
}

function normalizeLanguageCode(code?: string) {
  return (code ?? "").trim().toLowerCase().split("-")[0];
}

function mapSources(passages?: Array<Record<string, unknown>>) {
  if (!Array.isArray(passages)) return undefined;

  return passages.map((source, index) => {
    const queryId = source.query_id ?? source.record_id ?? index + 1;
    const passageIndex = source.passage_index ?? source.rank ?? index;
    const chunkIndex = source.chunk_index ?? 0;
    const language = typeof source.language === "string" ? source.language : undefined;
    const text = typeof source.text === "string" ? source.text : "";
    return {
      id: `${queryId}_${passageIndex}_${chunkIndex}`,
      title: `Source ${index + 1}${language ? ` (${language})` : ""}`,
      reference: String(source.reference ?? source.dataset ?? queryId),
      snippet: text,
    };
  });
}

function normalizeLatency(payload: BackendVoiceResponse) {
  const latency = payload.latency_ms ?? {};
  const queryEmbeddingMs = payload.query_embedding_ms ?? latency.query_embedding_ms;
  const vectorSearchMs = payload.vector_search_ms ?? payload.faiss_search_ms ?? latency.vector_search_ms ?? latency.faiss_search_ms;
  const metadataLookupMs = payload.metadata_lookup_ms ?? latency.metadata_lookup_ms;
  const contextConstructionMs = payload.context_construction_ms ?? latency.context_construction_ms;
  const llmMs = payload.llm_latency_ms ?? latency.llm_request_ms;
  const ragMs = payload.rag_latency_ms ?? latency.total_rag_ms ?? latency.total_ms;
  const retrievalMs =
    payload.retrieval_latency_ms ??
    sumDefined(queryEmbeddingMs, vectorSearchMs, metadataLookupMs);

  const normalized = {
    retrieval_ms: retrievalMs,
    generation_ms: payload.generation_latency_ms ?? llmMs,
    stt_ms: payload.stt_latency_ms,
    rag_ms: ragMs,
    llm_ms: llmMs,
    tts_ms: payload.tts_latency_ms,
    total_ms: payload.total_latency_ms ?? latency.total_ms,
  };

  return Object.values(normalized).some((value) => value !== undefined) ? normalized : undefined;
}

function sumDefined(...values: Array<number | undefined>) {
  const present = values.filter((value): value is number => value !== undefined);
  if (!present.length) return undefined;
  return present.reduce((total, value) => total + value, 0);
}
