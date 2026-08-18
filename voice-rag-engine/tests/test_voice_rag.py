import os
from unittest.mock import MagicMock, patch

import pytest

from rag.llm_client import LLMClient
from voice.stt.base import STTResult
from voice.stt.mock import MockSTT
from voice.tts.base import TTSResult
from voice.tts.mock import MockTTS
from voice.voice_rag import VoiceRAG, VoiceRAGError


class RecordingRAGPipeline:
    def __init__(self, result=None):
        self.result = result or {
            "answer": "Mock answer",
            "grounded": True,
            "refused": False,
            "latency_ms": {"total_ms": 42.0},
        }
        self.calls = []

    def answer(self, query, language="hi", top_k=5, min_score=0.70, query_id=None):
        self.calls.append(
            {
                "query": query,
                "language": language,
                "top_k": top_k,
                "min_score": min_score,
                "query_id": query_id,
            }
        )
        return self.result


class FixedSTT:
    def __init__(self, result=None, exc=None):
        self.result = result
        self.exc = exc

    def transcribe(self, audio_path):
        if self.exc:
            raise self.exc
        return self.result

    def validate_audio(self, audio_path):
        return os.path.exists(audio_path)


@pytest.fixture
def sample_audio(tmp_path):
    audio_path = tmp_path / "sample.wav"
    audio_path.write_bytes(b"fake audio")
    return str(audio_path)


def test_successful_audio_stt_then_rag(sample_audio):
    stt = MockSTT(latency_ms=25)
    pipeline = RecordingRAGPipeline(
        result={
            "answer": "यह उत्तर उपलब्ध है।",
            "grounded": True,
            "refused": False,
            "latency_ms": {"total_ms": 40.0},
        }
    )

    orchestrator = VoiceRAG(rag_pipeline=pipeline)
    result = orchestrator.process_audio(sample_audio, stt=stt)

    assert result["transcript"].startswith("यह एक परीक्षण प्रतिलिपि है")
    assert result["language_code"] == "hi-IN"
    assert result["stt_provider"] == "Mock"
    assert result["stt_model"] == "saaras:v3"
    assert result["answer"] == "यह उत्तर उपलब्ध है।"
    assert result["grounded"] is True
    assert result["refused"] is False
    assert result["stt_latency_ms"] >= 25.0
    assert result["rag_latency_ms"] == 40.0
    assert result["total_latency_ms"] >= max(result["stt_latency_ms"], result["rag_latency_ms"])
    assert result["query_embedding_ms"] == 0.0
    assert result["vector_search_ms"] == 0.0
    assert result["llm_latency_ms"] == 0.0
    assert pipeline.calls[0]["query"] == result["transcript"]


def test_transcript_passed_correctly_to_rag(sample_audio):
    transcript = "मैं विश्वविद्यालय का पता पूछ रहा हूँ।"
    stt = FixedSTT(
        result=STTResult(
            text=transcript,
            language_code="hi-IN",
            provider="Mock",
            model="mock:v1",
            latency_ms=11.5,
        )
    )
    pipeline = RecordingRAGPipeline(
        result={
            "answer": "उत्तर",
            "grounded": True,
            "refused": False,
            "latency_ms": {"total_ms": 12.0},
        }
    )

    result = VoiceRAG(rag_pipeline=pipeline).process_audio(sample_audio, stt=stt)

    assert result["transcript"] == transcript
    assert pipeline.calls[0]["query"] == transcript
    assert pipeline.calls[0]["language"] == "hi"


def test_stt_failure_returns_structured_error_without_rag(sample_audio):
    stt = FixedSTT(exc=RuntimeError("STT API failure"))
    pipeline = RecordingRAGPipeline()

    result = VoiceRAG(rag_pipeline=pipeline).process_audio(sample_audio, stt=stt)

    assert result["error"]["type"] == "STTError"
    assert "STT API failure" in result["error"]["message"]
    assert pipeline.calls == []


def test_empty_transcript_does_not_call_rag(sample_audio):
    stt = FixedSTT(
        result=STTResult(
            text="   ",
            language_code="hi-IN",
            provider="Mock",
            model="mock:v1",
            latency_ms=9.0,
        )
    )
    pipeline = RecordingRAGPipeline()

    result = VoiceRAG(rag_pipeline=pipeline).process_audio(sample_audio, stt=stt)

    assert result["error"]["type"] == "EmptyTranscriptError"
    assert pipeline.calls == []


def test_answerable_query(sample_audio):
    stt = MockSTT(latency_ms=30)
    pipeline = RecordingRAGPipeline(
        result={
            "answer": "यह उत्तर उपलब्ध है।",
            "grounded": True,
            "refused": False,
            "latency_ms": {"total_ms": 50.0},
        }
    )

    result = VoiceRAG(rag_pipeline=pipeline).process_audio(sample_audio, stt=stt)

    assert result["answer"] == "यह उत्तर उपलब्ध है।"
    assert result["grounded"] is True
    assert result["refused"] is False


def test_rag_refusal(sample_audio):
    stt = FixedSTT(
        result=STTResult(
            text="मुझे कोई जवाब नहीं मिल रहा है।",
            language_code="hi-IN",
            provider="Mock",
            model="mock:v1",
            latency_ms=12.0,
        )
    )
    pipeline = RecordingRAGPipeline(
        result={
            "answer": "उपलब्ध जानकारी के आधार पर इस प्रश्न का उत्तर नहीं दिया जा सकता है।",
            "grounded": False,
            "refused": True,
            "latency_ms": {"total_ms": 33.0},
        }
    )

    result = VoiceRAG(rag_pipeline=pipeline).process_audio(sample_audio, stt=stt)

    assert result["refused"] is True
    assert result["grounded"] is False
    assert result["answer"] == "उपलब्ध जानकारी के आधार पर इस प्रश्न का उत्तर नहीं दिया जा सकता है।"


def test_latency_fields(sample_audio):
    stt = MockSTT(latency_ms=14)
    pipeline = RecordingRAGPipeline(
        result={
            "answer": "उत्तर",
            "grounded": True,
            "refused": False,
            "latency_ms": {"total_ms": 21.0},
        }
    )

    result = VoiceRAG(rag_pipeline=pipeline).process_audio(sample_audio, stt=stt)

    assert isinstance(result["stt_latency_ms"], float)
    assert isinstance(result["rag_latency_ms"], float)
    assert isinstance(result["total_latency_ms"], float)
    assert isinstance(result["query_embedding_ms"], float)
    assert isinstance(result["vector_search_ms"], float)
    assert isinstance(result["context_construction_ms"], float)
    assert isinstance(result["llm_latency_ms"], float)
    assert result["total_latency_ms"] >= max(result["stt_latency_ms"], result["rag_latency_ms"])


def test_mock_stt_operation(sample_audio):
    stt = MockSTT(latency_ms=5)
    result = stt.transcribe(sample_audio)

    assert result.provider == "Mock"
    assert result.model == "saaras:v3"
    assert result.language_code == "hi-IN"
    assert "यह एक परीक्षण प्रतिलिपि है" in result.text


@patch("rag.llm_client.requests.post")
def test_groq_gpt_oss_sets_include_reasoning_false(mock_post):
    client = LLMClient(provider="groq", model="openai/gpt-oss-20b")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"role": "assistant", "content": "संदर्भ के अनुसार यह बनता है।"}, "finish_reason": "stop"}],
        "usage": {"completion_tokens": 8},
    }
    mock_post.return_value = mock_response

    answer, _ = client.generate(
        system_prompt="हिंदी में उत्तर दें।",
        user_prompt="Context here",
        max_tokens=25,
        temperature=0,
    )

    payload = mock_post.call_args.kwargs["json"]
    assert payload["include_reasoning"] is False
    assert answer == "संदर्भ के अनुसार यह बनता है।"


@patch("rag.llm_client.requests.post")
def test_groq_gpt_oss_ignores_reasoning_field(mock_post):
    client = LLMClient(provider="groq", model="openai/gpt-oss-20b")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"role": "assistant", "content": "", "reasoning": "hidden reasoning text"}, "finish_reason": "stop"}],
        "usage": {"completion_tokens": 0},
    }
    mock_post.return_value = mock_response

    answer, _ = client.generate(
        system_prompt="हिंदी में उत्तर दें।",
        user_prompt="Context here",
        max_tokens=25,
        temperature=0,
    )

    assert answer == ""
    assert answer != "hidden reasoning text"


@patch("rag.llm_client.requests.post")
def test_groq_gpt_oss_empty_content_keeps_safe_behavior(mock_post):
    client = LLMClient(provider="groq", model="openai/gpt-oss-20b")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"role": "assistant", "content": None}, "finish_reason": "stop"}],
        "usage": {"completion_tokens": 0},
    }
    mock_post.return_value = mock_response

    answer, _ = client.generate(
        system_prompt="हिंदी में उत्तर दें।",
        user_prompt="Context here",
        max_tokens=25,
        temperature=0,
    )

    assert answer == ""


def test_dependency_injection(sample_audio):
    class CustomSTT:
        def transcribe(self, audio_path):
            return STTResult(
                text="इनजेक्शन टेस्ट",
                language_code="en-IN",
                provider="Custom",
                model="custom:v1",
                latency_ms=7.0,
            )

        def validate_audio(self, audio_path):
            return True

    pipeline = RecordingRAGPipeline(
        result={
            "answer": "ok",
            "grounded": True,
            "refused": False,
            "latency_ms": {"total_ms": 10.0},
        }
    )

    result = VoiceRAG(rag_pipeline=pipeline).process_audio(sample_audio, stt=CustomSTT())

    assert result["transcript"] == "इनजेक्शन टेस्ट"
    assert result["language_code"] == "en-IN"
    assert result["stt_provider"] == "Custom"
    assert pipeline.calls[0]["query"] == "इनजेक्शन टेस्ट"


def test_voice_rag_raises_on_error_when_requested(sample_audio):
    stt = FixedSTT(exc=RuntimeError("bad audio"))
    pipeline = RecordingRAGPipeline()

    with pytest.raises(VoiceRAGError, match="STT failed"):
        VoiceRAG(rag_pipeline=pipeline).process_audio(sample_audio, stt=stt, raise_on_error=True)


def test_voice_rag_without_tts_preserves_existing_behavior(sample_audio):
    stt = MockSTT(latency_ms=12)
    pipeline = RecordingRAGPipeline(
        result={
            "answer": "उत्तर उपलब्ध है।",
            "grounded": True,
            "refused": False,
            "latency_ms": {"total_ms": 18.0},
        }
    )

    result = VoiceRAG(rag_pipeline=pipeline).process_audio(sample_audio, stt=stt)

    assert result["answer"] == "उत्तर उपलब्ध है।"
    assert result["tts_audio"] is None
    assert result["tts_provider"] is None
    assert result["tts_model"] is None
    assert result["tts_error"] is None


def test_voice_rag_synthesizes_answer_with_mock_tts(sample_audio):
    stt = MockSTT(latency_ms=8)
    pipeline = RecordingRAGPipeline(
        result={
            "answer": "यह उत्तर उपलब्ध है।",
            "grounded": True,
            "refused": False,
            "latency_ms": {"total_ms": 20.0},
        }
    )
    tts = MockTTS(model="mock:v2", language_code="hi-IN", latency_ms=12.5)

    result = VoiceRAG(rag_pipeline=pipeline, tts=tts).process_audio(sample_audio, stt=stt)

    assert result["answer"] == "यह उत्तर उपलब्ध है।"
    assert result["tts_provider"] == "Mock"
    assert result["tts_model"] == "mock:v2"
    assert result["tts_audio"] == "mock-audio:यह उत्तर उपलब्ध है।".encode("utf-8")
    assert result["tts_latency_ms"] == 12.5


def test_voice_rag_synthesizes_refusal_when_answer_is_empty(sample_audio):
    stt = FixedSTT(
        result=STTResult(
            text="उत्पादन की जानकारी नहीं है।",
            language_code="hi-IN",
            provider="Mock",
            model="mock:v1",
            latency_ms=10.0,
        )
    )
    pipeline = RecordingRAGPipeline(
        result={
            "answer": "",
            "grounded": False,
            "refused": True,
            "latency_ms": {"total_ms": 25.0},
        }
    )
    tts = MockTTS(model="mock:refusal", latency_ms=5.0)

    result = VoiceRAG(rag_pipeline=pipeline, tts=tts).process_audio(sample_audio, stt=stt)

    assert result["refused"] is True
    assert result["tts_audio"] == "mock-audio:उपलब्ध जानकारी के आधार पर इस प्रश्न का उत्तर नहीं दिया जा सकता है।".encode("utf-8")


def test_voice_rag_tts_failure_does_not_break_pipeline(sample_audio):
    stt = MockSTT(latency_ms=9)
    pipeline = RecordingRAGPipeline(
        result={
            "answer": "उत्तर दिया गया।",
            "grounded": True,
            "refused": False,
            "latency_ms": {"total_ms": 15.0},
        }
    )

    class FailingTTS:
        def synthesize(self, text):
            raise RuntimeError("TTS backend down")

    result = VoiceRAG(rag_pipeline=pipeline, tts=FailingTTS()).process_audio(sample_audio, stt=stt)

    assert result["answer"] == "उत्तर दिया गया।"
    assert result["tts_audio"] is None
    assert "TTS synthesis failed" in result["tts_error"]


def test_voice_rag_does_not_call_tts_on_stt_failure(sample_audio):
    class TrackingTTS:
        def __init__(self):
            self.calls = []

        def synthesize(self, text):
            self.calls.append(text)
            return TTSResult(
                audio=b"audio",
                language_code="hi-IN",
                provider="Mock",
                model="mock:test",
                latency_ms=3.0,
            )

    stt = FixedSTT(exc=RuntimeError("STT API failure"))
    pipeline = RecordingRAGPipeline()
    tts = TrackingTTS()

    result = VoiceRAG(rag_pipeline=pipeline, tts=tts).process_audio(sample_audio, stt=stt)

    assert result["error"]["type"] == "STTError"
    assert tts.calls == []


@patch.dict(os.environ, {"GROQ_API_KEY": "test_key", "GROQ_MODEL": "openai/gpt-oss-20b"}, clear=False)
def test_llm_client_uses_configured_groq_model():
    client = LLMClient(provider="groq")
    assert client.provider == "groq"
    assert client.model == "openai/gpt-oss-20b"


def test_rag_pipeline_uses_shorter_output_and_context():
    class FakeLLM:
        last_generation_metrics = {
            "provider": "mock",
            "model": "mock-low-latency",
            "request_latency_ms": 7.5,
            "time_to_first_token_ms": None,
            "total_generation_ms": 7.5,
            "output_token_count": 8,
        }

        def generate(self, **kwargs):
            return "पता है", 7.5

    pipeline = __import__("rag.pipeline", fromlist=["TextRAGPipeline"]).TextRAGPipeline(llm_provider="mock", llm_model="mock-low-latency")
    pipeline.llm_client = FakeLLM()

    result = pipeline.answer("भूमि आकृतियाँ कैसे बनती हैं?", language="hi", top_k=5, min_score=0.70)

    assert result["answer"] == "पता है"
    assert result["latency_ms"]["llm_request_ms"] == 7.5
