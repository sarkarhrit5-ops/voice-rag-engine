"""Voice-to-RAG orchestration layer."""

import time
from typing import Any, Optional

from voice.stt.base import BaseSTT, STTResult
from voice.stt.sarvam import SarvamSTT
from voice.tts.base import BaseTTS


class VoiceRAGError(RuntimeError):
    """Raised when the voice-to-RAG workflow fails."""

    def __init__(self, message: str, error_type: str = "VoiceRAGError"):
        super().__init__(message)
        self.message = message
        self.error_type = error_type


class VoiceRAG:
    """Orchestrates STT and the existing text-based RAG pipeline."""

    def __init__(
        self,
        stt: Optional[BaseSTT] = None,
        rag_pipeline: Optional[Any] = None,
        tts: Optional[BaseTTS] = None,
    ):
        self.stt = stt
        self.tts = tts
        if rag_pipeline is None:
            try:
                from rag.pipeline import TextRAGPipeline

                self.rag_pipeline = TextRAGPipeline()
            except Exception:
                self.rag_pipeline = None
        else:
            self.rag_pipeline = rag_pipeline

    @staticmethod
    def _error_payload(error_type: str, message: str) -> dict:
        return {
            "error": {
                "type": error_type,
                "message": message,
            }
        }

    def process_audio(
        self,
        audio_path: str,
        stt: Optional[BaseSTT] = None,
        rag_pipeline: Optional[Any] = None,
        tts: Optional[BaseTTS] = None,
        raise_on_error: bool = False,
    ) -> dict:
        """Transcribe an audio file then answer using the existing RAG pipeline."""
        active_stt = stt or self.stt
        if active_stt is None:
            active_stt = SarvamSTT()
        active_rag = rag_pipeline or self.rag_pipeline
        active_tts = tts or self.tts

        if active_stt is None:
            raise ValueError("An STT implementation is required.")
        if active_rag is None or not hasattr(active_rag, "answer"):
            raise ValueError("A RAG pipeline with an answer() method is required.")

        result = {
            "transcript": "",
            "language_code": getattr(active_stt, "language_code", None),
            "stt_provider": None,
            "stt_model": getattr(active_stt, "model", None),
            "answer": None,
            "refused": None,
            "grounded": None,
            "stt_latency_ms": 0.0,
            "query_embedding_ms": 0.0,
            "vector_search_ms": 0.0,
            "metadata_lookup_ms": 0.0,
            "context_construction_ms": 0.0,
            "llm_latency_ms": 0.0,
            "rag_latency_ms": 0.0,
            "total_latency_ms": 0.0,
            "tts_audio": None,
            "tts_provider": None,
            "tts_model": None,
            "tts_latency_ms": 0.0,
            "tts_error": None,
        }

        voice_start = time.time()

        try:
            stt_start = time.time()
            stt_result: STTResult = active_stt.transcribe(audio_path)
            stt_latency_ms = float(getattr(stt_result, "latency_ms", 0.0) or 0.0)
            transcript = (getattr(stt_result, "text", "") or "").strip()

            result["transcript"] = transcript
            result["language_code"] = getattr(stt_result, "language_code", result["language_code"])
            result["stt_provider"] = getattr(stt_result, "provider", None)
            result["stt_model"] = getattr(stt_result, "model", result["stt_model"])
            result["stt_latency_ms"] = stt_latency_ms

            if not transcript:
                error_message = "STT returned an empty transcript; skipping RAG."
                result.update(self._error_payload("EmptyTranscriptError", error_message))
                if raise_on_error:
                    raise VoiceRAGError(error_message, "EmptyTranscriptError")
                return result

            rag_language = (result["language_code"] or "hi").split("-")[0]
            rag_response = active_rag.answer(
                query=transcript,
                language=rag_language,
            )
            rag_latency_ms = float(
                rag_response.get("latency_ms", {}).get("total_rag_ms", rag_response.get("latency_ms", {}).get("total_ms", 0.0))
                if isinstance(rag_response, dict)
                else 0.0
            )
            rag_latency_details = rag_response.get("latency_ms", {}) if isinstance(rag_response, dict) else {}

            result["query_embedding_ms"] = float(rag_latency_details.get("query_embedding_ms", 0.0) or 0.0)
            result["vector_search_ms"] = float(rag_latency_details.get("vector_search_ms", rag_latency_details.get("faiss_search_ms", 0.0)) or 0.0)
            result["metadata_lookup_ms"] = float(rag_latency_details.get("metadata_lookup_ms", 0.0) or 0.0)
            result["context_construction_ms"] = float(rag_latency_details.get("context_construction_ms", 0.0) or 0.0)
            result["llm_latency_ms"] = float(rag_latency_details.get("llm_request_ms", 0.0) or 0.0)

            result["answer"] = rag_response.get("answer")
            result["refused"] = bool(rag_response.get("refused", False))
            result["grounded"] = bool(rag_response.get("grounded", False))
            result["rag_latency_ms"] = rag_latency_ms

            if active_tts is not None:
                tts_text = None
                if isinstance(result["answer"], str) and result["answer"].strip():
                    tts_text = result["answer"].strip()
                elif result.get("refused"):
                    tts_text = "उपलब्ध जानकारी के आधार पर इस प्रश्न का उत्तर नहीं दिया जा सकता है।"

                if tts_text is not None:
                    try:
                        tts_start = time.time()
                        tts_result = active_tts.synthesize(tts_text)
                        result["tts_audio"] = getattr(tts_result, "audio", None)
                        result["tts_provider"] = getattr(tts_result, "provider", None)
                        result["tts_model"] = getattr(tts_result, "model", None)
                        result["tts_latency_ms"] = float(getattr(tts_result, "latency_ms", 0.0) or 0.0)
                    except Exception as exc:
                        result["tts_error"] = f"TTS synthesis failed: {exc}"

            wall_total_ms = (time.time() - voice_start) * 1000.0
            result["total_latency_ms"] = max(wall_total_ms, stt_latency_ms + rag_latency_ms)
            return result

        except Exception as exc:
            message = f"STT failed: {exc}"
            if isinstance(exc, ValueError) and "empty transcript" in str(exc).lower():
                message = f"STT failed: {exc}"
            error_type = "STTError"
            if isinstance(exc, ValueError) and "empty transcript" in str(exc).lower():
                error_type = "EmptyTranscriptError"

            result.update(self._error_payload(error_type, message))
            if raise_on_error:
                raise VoiceRAGError(message, error_type) from exc
            return result
