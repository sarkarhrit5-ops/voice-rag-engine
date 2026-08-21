export type VoiceState =
  | 'idle'
  | 'listening'
  | 'processing'
  | 'retrieving'
  | 'verifying'
  | 'answer'
  | 'refused'
  | 'error';

export interface LanguageOption {
  code: string;
  label: string;
  nativeLabel: string;
  flag: string;
}

export interface SourceItem {
  id: string | number;
  title: string;
  snippet?: string;
  reference?: string;
}

export interface LatencyMetrics {
  retrieval_ms?: number;
  generation_ms?: number;
  stt_ms?: number;
  tts_ms?: number;
  total_ms?: number;
  rag_ms?: number;
  llm_ms?: number;
}

export interface VoiceQueryResponse {
  transcription: string;
  answer: string;
  grounded: boolean;
  refusal: boolean;
  confidence?: number;
  sources?: SourceItem[];
  latency?: LatencyMetrics;
  audio_url?: string;
  audio_base64?: string;
  language?: string;
  language_code?: string;
  normalized_language?: string;
  selected_index?: string;
  retrieved_result_count?: number;
  top_similarity_score?: number;
  reason?: string;
}

export interface VoiceQueryError {
  error: string;
  detail?: string;
}
