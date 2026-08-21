import type { VoiceQueryResponse } from "../types";
import {
  getPredefinedQueriesForLanguage,
  findPredefinedResponse,
} from "../config/predefinedQueries";

export function buildDemoResponse(language: string = "hi"): VoiceQueryResponse {
  const queries = getPredefinedQueriesForLanguage(language);
  if (queries.length > 0) {
    return queries[0].response;
  }
  return {
    transcription: "What is grounded answer generation in this RAG engine?",
    language: "en",
    normalized_language: "en",
    answer:
      "Grounded answer generation requires that the model's response is strictly supported by the retrieved context. If there is insufficient evidence, the system must refuse to answer.",
    grounded: true,
    refusal: false,
    confidence: 0.95,
    sources: [
      {
        id: 1,
        title: "Grounded Generation Guidelines",
        reference: "Guidelines-Ref-1",
        snippet: "Answers must be strictly generated using the provided context.",
      },
    ],
    latency: {
      stt_ms: 250,
      retrieval_ms: 120,
      generation_ms: 450,
      tts_ms: 300,
      total_ms: 1120,
    },
  };
}

export { findPredefinedResponse };
