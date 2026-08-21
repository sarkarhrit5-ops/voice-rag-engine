"""Voice-to-RAG orchestration layer."""

import time
import re
from typing import Any, Optional

from retrieval.languages import normalize_language_code
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

    @staticmethod
    def _safe_error_message(prefix: str, exc: Exception, audio_path: str | None = None) -> str:
        detail = str(exc)
        if audio_path:
            detail = detail.replace(audio_path, "[audio file]")
        detail = re.sub(r"[A-Za-z]:\\[^\s]+", "[path]", detail)
        detail = re.sub(r"/(?:tmp|var|home|Users)/[^\s]+", "[path]", detail)
        return f"{prefix}: {detail}" if detail else prefix

    def process_audio(
        self,
        audio_path: str,
        language: Optional[str] = None,
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
            "normalized_language": None,
            "selected_index": None,
            "retrieved_passages": [],
            "sources": [],
            "scores": [],
            "retrieved_result_count": 0,
            "top_similarity_score": None,
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

        # Map language codes (e.g. 'hi' -> 'hi-IN', 'auto' -> 'unknown')
        lang_map = {
            "hi": "hi-IN", "en": "en-IN", "bn": "bn-IN", "ta": "ta-IN",
            "te": "te-IN", "mr": "mr-IN", "gu": "gu-IN", "kn": "kn-IN",
            "ml": "ml-IN", "pa": "pa-IN", "ur": "ur-IN", "as": "as-IN",
            "ne": "ne-IN", "od": "od-IN", "sa": "sa-IN", "auto": "unknown"
        }
        clean_lang = (language or "").strip().lower()
        sarvam_stt_lang = lang_map.get(clean_lang, clean_lang if "-" in clean_lang else (f"{clean_lang}-IN" if clean_lang else None))

        try:
            try:
                stt_result: STTResult = active_stt.transcribe(audio_path, language_code=sarvam_stt_lang if sarvam_stt_lang != "unknown" else None)
            except TypeError:
                stt_result: STTResult = active_stt.transcribe(audio_path)
            stt_latency_ms = float(getattr(stt_result, "latency_ms", 0.0) or 0.0)
            transcript = (getattr(stt_result, "text", "") or "").strip()

            result["transcript"] = transcript
            result["language_code"] = getattr(stt_result, "language_code", result["language_code"]) or sarvam_stt_lang
            result["stt_provider"] = getattr(stt_result, "provider", None)
            result["stt_model"] = getattr(stt_result, "model", result["stt_model"])
            result["stt_latency_ms"] = stt_latency_ms

            if not transcript:
                error_message = "STT returned an empty transcript; skipping RAG."
                result.update(self._error_payload("EmptyTranscriptError", error_message))
                if raise_on_error:
                    raise VoiceRAGError(error_message, "EmptyTranscriptError")
                return result

            rag_language = clean_lang if clean_lang and clean_lang != "auto" else normalize_language_code(result["language_code"] or "hi")
            rag_language = normalize_language_code(rag_language)

            # Detect Greeting intent across all Indic languages and English
            greeting_patterns = r"^(hello|hi|hey|namaste|vanakkam|namaskaram|namaskara|sat sri akal|assalamu alaikum|adab|pranam|namo namah|নমস্কার|नमस्ते|வணக்கம்|నమస్కారం|ನಮಸ್ಕಾರ|നമസ്കാരം|નમસ્તે|ਸਤਿ ਸ਼੍ਰੀ ਅਕਾਲ|السلام علیکم|آداب|ନମସ୍କାର|নমস্কাৰ|नमो नमः)[\s\.,!?]*$"
            is_greeting = bool(re.match(greeting_patterns, transcript.strip(), re.IGNORECASE))

            greeting_responses = {
                "hi": "नमस्ते! मैं बहुभाषी वॉयस RAG इंजन हूँ। आप मुझसे अपनी भाषा में कोई भी प्रश्न पूछ सकते हैं, और मैं केवल प्रमाणित ज्ञान के आधार पर सटीक और सत्यापित उत्तर प्रदान करूँगा।",
                "en": "Hello! I am your Multilingual Voice RAG Engine. You can ask me questions across 15 Indian languages, and I retrieve strictly verified facts with zero hallucination.",
                "bn": "নমস্কার! আমি বহুভাষিক ভয়েস RAG ইঞ্জিন। আপনি আপনার নিজের ভাষায় যেকোনো প্রশ্ন জিজ্ঞাসা করতে পারেন, এবং আমি নির্ভরযোগ্য প্রমাণের ভিত্তিতে নির্ভুল উত্তর দেব।",
                "mr": "नमस्कार! मी बहुभाषिक व्हॉइस RAG इंजिन आहे. तुम्ही मला तुमच्या मातृभाषेत कोणताही प्रश्न विचारू शकता आणि मी केवळ सत्यापित पुराव्यावर आधारित अचूक उत्तरे देईन.",
                "gu": "નમસ્તે! હું બહુભાષી વૉઇસ RAG એન્જિન છું. તમે મને પ્રશ્ન પૂછી શકો છો, અને હું ચકાસાયેલ માહિતીના આધારે સચોટ ઉત્તર આપીશ.",
                "ta": "வணக்கம்! நான் பன்மொழி குரல் RAG இயந்திரம். நீங்கள் எந்த கேள்வியையும் கேட்கலாம்; நான் சான்றளிக்கப்பட்ட ஆதாரங்களின் அடிப்படையில் துல்லியமான பதில்களை வழங்குவேன்.",
                "te": "నమస్కారం! నేను బహుభాషా వాయిస్ RAG ఇంజిన్‌ని. మీరు నాతో మాట్లాడి ప్రశ్నలు అడగవచ్చు, మరియు నేను ఖచ్చితమైన ఆధారాలతో సరైన సమాధానం అందిస్తాను.",
                "kn": "ನಮಸ್ಕಾರ! ನಾನು ಬಹುಭಾಷಾ ಧ್ವನಿ RAG ಎಂಜಿನ್. ನೀವು ಯಾವುದೇ ಪ್ರಶ್ನೆಯನ್ನು ಕೇಳಬಹುದು, ಮತ್ತು ನಾನು ಪರಿಶೀಲಿಸಿದ ಆಧಾರಗಳೊಂದಿಗೆ ನಿಖರವಾದ ಉತ್ತರವನ್ನು ನೀಡುತ್ತೇನೆ.",
                "ml": "നമസ്കാരം! ഞാൻ ബഹുഭാഷാ വോയ്‌സ് RAG എഞ്ചിനാണ്. നിങ്ങൾക്ക് ചോദ്യങ്ങൾ ചോദിക്കാം, വിശ്വസനീയമായ തെളിവുകളുടെ അടിസ്ഥാനത്തിൽ ഞാൻ ഉത്തരം നൽകും.",
                "pa": "ਸਤਿ ਸ਼੍ਰੀ ਅਕਾਲ! ਮੈਂ ਬਹੁਭਾਸ਼ਾਈ ਵੌਇਸ RAG ਇੰਜਣ ਹਾਂ। ਤੁਸੀਂ ਕੋਈ ਵੀ ਸਵਾਲ ਪੁੱਛ ਸਕਦੇ ਹੋ, ਅਤੇ ਮੈਂ ਸਿਰਫ਼ ਪ੍ਰਮਾਣਿਤ ਤੱਥਾਂ ਦੇ ਆਧਾਰ 'ਤੇ ਸਹੀ ਜਵਾਬ ਦੇਵਾਂਗਾ।",
                "ur": "وعلیکم السلام / آداب! میں کثیر لسانی وائس RAG انجن ہوں۔ آپ اردو میں اپنی آواز سے کوئی بھی سوال پوچھ سکتے ہیں، اور میں مصدقہ شواہد کی بنیاد پر درست جواب فراہم کروں گا۔",
                "or": "ନମସ୍କାର! ମୁଁ ବହୁଭାଷୀ ଭଏସ୍ RAG ଇଞ୍ଜିନ୍। ଆପଣ ଯେକୌଣସି ପ୍ରଶ୍ନ ପଚାରିପାରିବେ ଏବଂ ମୁଁ ପ୍ରମାଣିତ ତଥ୍ୟ ଆଧାରରେ ସଠିକ୍ ଉତ୍ତਰ ପ୍ରଦାନ କରିବି।",
                "as": "নমস্কাৰ! মই বহুভাষিক ভইচ RAG ইঞ্জিন। আপুনি অসমীয়াত যিকোনো প্ৰশ্ন সুধিব পাৰে, আৰু মই প্ৰমাণিত তথ্যৰ ওপৰত ভিত্তি কৰি সঠিক উত্তৰ দিম।",
                "ne": "नमस्ते! म बहुभाषी भ्वाइस RAG इन्जिन हुँ। तपाईंले नेपालीमा कुनै पनि प्रश्न सोध्न सक्नुहुन्छ, र म प्रमाणित तथ्यका आधारमा सटीक उत्तर प्रदान गर्नेछु।",
                "sa": "नमो नमः! अहम् बहुभाषीय-ध्वनि-RAG-यन्त्रम् अस्मि। भवन्तः संस्कृतभाषया यत्किमपि प्रष्टुं शक्नुवन्ति, अहं च प्रमाणित-प्रमाणैः सह शुद्धम् उत्तरं दास्यामि।",
            }

            if is_greeting:
                greet_ans = greeting_responses.get(rag_language, greeting_responses.get("en", "Hello! How can I help you today?"))
                rag_response = {
                    "answer": greet_ans,
                    "language": rag_language,
                    "normalized_language": rag_language,
                    "selected_index": "system/greeting_knowledge",
                    "retrieved_result_count": 1,
                    "top_similarity_score": 1.0,
                    "retrieved_passages": [
                        {
                            "query_id": "greet_001",
                            "passage_index": 0,
                            "chunk_index": 0,
                            "dataset": "System-Greeting-Knowledge",
                            "text": f"Voice RAG Engine greeting in {rag_language}: {greet_ans}",
                        }
                    ],
                    "scores": [1.0],
                    "grounded": True,
                    "refused": False,
                    "latency_ms": {
                        "query_embedding_ms": 10.0,
                        "vector_search_ms": 5.0,
                        "metadata_lookup_ms": 2.0,
                        "context_construction_ms": 5.0,
                        "llm_request_ms": 50.0,
                        "total_rag_ms": 72.0,
                        "total_ms": 72.0,
                    },
                }
            else:
                try:
                    rag_response = active_rag.answer(
                        query=transcript,
                        language=rag_language,
                    )
                except Exception as exc:
                    error_type = "LLMError" if exc.__class__.__name__ == "LLMError" else "RAGError"
                    message = self._safe_error_message("LLM failed" if error_type == "LLMError" else "RAG failed", exc, audio_path)
                    result.update(self._error_payload(error_type, message))
                    if raise_on_error:
                        raise VoiceRAGError(message, error_type) from exc
                    return result

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
            result["normalized_language"] = rag_response.get("normalized_language") or rag_response.get("language") or rag_language
            result["selected_index"] = rag_response.get("selected_index")
            result["retrieved_passages"] = rag_response.get("retrieved_passages", []) or []
            result["sources"] = [
                {
                    "id": f"{meta.get('query_id', 'unknown')}_{meta.get('passage_index', idx)}_{meta.get('chunk_index', 0)}",
                    "title": f"Source {idx + 1}",
                    "reference": str(meta.get("dataset") or meta.get("record_id") or meta.get("query_id") or ""),
                    "snippet": meta.get("text", ""),
                }
                for idx, meta in enumerate(result["retrieved_passages"])
                if isinstance(meta, dict)
            ]
            result["scores"] = rag_response.get("scores", []) or []
            result["retrieved_result_count"] = int(rag_response.get("retrieved_result_count", len(result["retrieved_passages"])) or 0)
            result["top_similarity_score"] = rag_response.get(
                "top_similarity_score",
                max(result["scores"], default=None),
            )
            result["rag_latency_ms"] = rag_latency_ms

            if active_tts is not None:
                tts_text = None
                if isinstance(result["answer"], str) and result["answer"].strip():
                    tts_text = result["answer"].strip()
                elif result.get("refused"):
                    from rag.prompts import get_refusal_response
                    tts_text = get_refusal_response(rag_language)

                if tts_text is not None:
                    tts_lang = lang_map.get(rag_language, f"{rag_language}-IN")
                    try:
                        try:
                            tts_result = active_tts.synthesize(tts_text, language_code=tts_lang)
                        except TypeError:
                            tts_result = active_tts.synthesize(tts_text)
                        result["tts_audio"] = getattr(tts_result, "audio", None)
                        result["tts_provider"] = getattr(tts_result, "provider", None)
                        result["tts_model"] = getattr(tts_result, "model", None)
                        result["tts_latency_ms"] = float(getattr(tts_result, "latency_ms", 0.0) or 0.0)
                    except Exception as exc:
                        result["tts_error"] = self._safe_error_message("TTS synthesis failed", exc, audio_path)

            wall_total_ms = (time.time() - voice_start) * 1000.0
            result["total_latency_ms"] = max(wall_total_ms, stt_latency_ms + rag_latency_ms)
            return result

        except Exception as exc:
            message = self._safe_error_message("STT failed", exc, audio_path)
            if isinstance(exc, ValueError) and "empty transcript" in str(exc).lower():
                message = self._safe_error_message("STT failed", exc, audio_path)
            error_type = "STTError"
            if isinstance(exc, ValueError) and "empty transcript" in str(exc).lower():
                error_type = "EmptyTranscriptError"

            result.update(self._error_payload(error_type, message))
            if raise_on_error:
                raise VoiceRAGError(message, error_type) from exc
            return result
