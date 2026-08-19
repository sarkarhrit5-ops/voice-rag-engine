from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.config import APISettings
from api.main import create_app, get_voice_rag
from rag.llm_client import LLMClient
from voice.stt.base import STTResult
from voice.stt.mock import MockSTT
from voice.tts.mock import MockTTS
from voice.voice_rag import VoiceRAG


class RecordingRAGPipeline:
    def __init__(self, result=None, exc=None):
        self.result = result or {
            "answer": "Mock answer",
            "grounded": True,
            "refused": False,
            "latency_ms": {"total_ms": 10.0},
        }
        self.exc = exc
        self.calls = []

    def answer(self, query, language="hi", top_k=5, min_score=0.70, query_id=None):
        self.calls.append({"query": query, "language": language})
        if self.exc:
            raise self.exc
        return self.result


class FailingSTT:
    model = "failing:stt"
    language_code = "hi-IN"

    def transcribe(self, audio_path):
        raise RuntimeError("STT provider down")

    def validate_audio(self, audio_path):
        return True


class FailingTTS:
    def synthesize(self, text):
        raise RuntimeError("TTS provider down")

    def validate_text(self, text):
        return True


class TrackingVoiceRAG:
    def __init__(self):
        self.paths = []

    def process_audio(self, audio_path):
        path = Path(audio_path)
        assert path.exists()
        self.paths.append(path)
        return {
            "transcript": "tracked transcript",
            "language_code": "hi-IN",
            "stt_provider": "Mock",
            "stt_model": "mock",
            "answer": "tracked answer",
            "refused": False,
            "grounded": True,
            "stt_latency_ms": 1.0,
            "query_embedding_ms": 0.0,
            "vector_search_ms": 0.0,
            "metadata_lookup_ms": 0.0,
            "context_construction_ms": 0.0,
            "llm_latency_ms": 0.0,
            "rag_latency_ms": 1.0,
            "total_latency_ms": 2.0,
            "tts_audio": None,
            "tts_provider": None,
            "tts_model": None,
            "tts_latency_ms": 0.0,
            "tts_error": None,
        }


@pytest.fixture
def api_client(tmp_path):
    app = create_app()
    app.state.api_settings = APISettings(max_upload_bytes=1024 * 1024, temp_dir=tmp_path)
    yield TestClient(app), app
    app.dependency_overrides.clear()


def make_voice_rag(rag_result=None, rag_exc=None, stt=None, tts=None):
    return VoiceRAG(
        stt=stt or MockSTT(latency_ms=0.0),
        rag_pipeline=RecordingRAGPipeline(result=rag_result, exc=rag_exc),
        tts=tts,
    )


def post_audio(client, data=b"fake audio", filename="query.wav", content_type="audio/wav", headers=None):
    return client.post(
        "/voice/query",
        files={"audio": (filename, data, content_type)},
        headers=headers or {},
    )


def test_health_endpoint(api_client):
    client, _ = api_client

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["request_id"]
    assert response.headers["X-Request-ID"] == response.json()["request_id"]


def test_valid_voice_request_using_mocks(api_client):
    client, app = api_client
    app.dependency_overrides[get_voice_rag] = lambda: make_voice_rag(
        rag_result={
            "answer": "mock API answer",
            "grounded": True,
            "refused": False,
            "latency_ms": {"total_ms": 5.0},
        },
        tts=MockTTS(latency_ms=0.0),
    )

    response = post_audio(client)
    payload = response.json()

    assert response.status_code == 200
    assert payload["transcript"]
    assert payload["answer"] == "mock API answer"
    assert payload["grounded"] is True
    assert payload["refused"] is False
    assert payload["tts_provider"] == "Mock"
    assert payload["tts_audio_base64"]
    assert payload["tts_audio_bytes"] > 0
    assert payload["request_id"] == response.headers["X-Request-ID"]


def test_missing_audio_returns_validation_error(api_client):
    client, _ = api_client

    response = client.post("/voice/query")

    assert response.status_code == 422
    assert response.json()["error"]["type"] == "ValidationError"


def test_invalid_audio_type_is_rejected(api_client):
    client, app = api_client
    app.dependency_overrides[get_voice_rag] = lambda: make_voice_rag()

    response = post_audio(client, data=b"not audio", filename="query.txt", content_type="text/plain")

    assert response.status_code == 415
    assert response.json()["error"]["type"] == "InvalidAudioError"


def test_empty_audio_is_rejected(api_client):
    client, app = api_client
    app.dependency_overrides[get_voice_rag] = lambda: make_voice_rag()

    response = post_audio(client, data=b"")

    assert response.status_code == 400
    assert response.json()["error"]["type"] == "EmptyUploadError"


def test_stt_failure_returns_structured_error(api_client):
    client, app = api_client
    app.dependency_overrides[get_voice_rag] = lambda: make_voice_rag(stt=FailingSTT())

    response = post_audio(client)

    assert response.status_code == 502
    assert response.json()["error"]["type"] == "STTError"
    assert "voice-rag-" not in response.json()["error"]["message"]


def test_rag_failure_returns_structured_error(api_client):
    client, app = api_client
    app.dependency_overrides[get_voice_rag] = lambda: make_voice_rag(rag_exc=RuntimeError("RAG failed hard"))

    response = post_audio(client)

    assert response.status_code == 502
    assert response.json()["error"]["type"] == "RAGError"


def test_tts_failure_does_not_fail_voice_response(api_client):
    client, app = api_client
    app.dependency_overrides[get_voice_rag] = lambda: make_voice_rag(
        rag_result={
            "answer": "answer with failed speech",
            "grounded": True,
            "refused": False,
            "latency_ms": {"total_ms": 5.0},
        },
        tts=FailingTTS(),
    )

    response = post_audio(client)
    payload = response.json()

    assert response.status_code == 200
    assert payload["answer"] == "answer with failed speech"
    assert "TTS synthesis failed" in payload["tts_error"]
    assert payload["tts_audio_base64"] is None


def test_refusal_response_is_preserved(api_client):
    client, app = api_client
    app.dependency_overrides[get_voice_rag] = lambda: make_voice_rag(
        rag_result={
            "answer": "",
            "grounded": False,
            "refused": True,
            "latency_ms": {"total_ms": 5.0},
        },
        tts=MockTTS(latency_ms=0.0),
    )

    response = post_audio(client)
    payload = response.json()

    assert response.status_code == 200
    assert payload["refused"] is True
    assert payload["grounded"] is False
    assert payload["tts_audio_base64"]


def test_request_id_is_reused_from_header(api_client):
    client, app = api_client
    app.dependency_overrides[get_voice_rag] = lambda: make_voice_rag()

    response = post_audio(client, headers={"X-Request-ID": "req-test-123"})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "req-test-123"
    assert response.json()["request_id"] == "req-test-123"


def test_invalid_request_id_is_replaced(api_client):
    client, app = api_client
    app.dependency_overrides[get_voice_rag] = lambda: make_voice_rag()

    response = post_audio(client, headers={"X-Request-ID": "bad id with spaces and /slashes"})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] != "bad id with spaces and /slashes"
    assert response.json()["request_id"] == response.headers["X-Request-ID"]


def test_temporary_file_is_cleaned_up(api_client):
    client, app = api_client
    tracking_voice_rag = TrackingVoiceRAG()
    app.dependency_overrides[get_voice_rag] = lambda: tracking_voice_rag

    response = post_audio(client)

    assert response.status_code == 200
    assert len(tracking_voice_rag.paths) == 1
    assert not tracking_voice_rag.paths[0].exists()
    assert not tracking_voice_rag.paths[0].parent.exists()


def test_temporary_file_is_cleaned_up_after_failure(api_client):
    client, app = api_client
    app.dependency_overrides[get_voice_rag] = lambda: make_voice_rag(stt=FailingSTT())

    response = post_audio(client)

    assert response.status_code == 502
    assert list(app.state.api_settings.temp_dir.iterdir()) == []


def test_upload_size_limit_is_enforced(api_client):
    client, app = api_client
    app.state.api_settings = APISettings(max_upload_bytes=4)
    app.dependency_overrides[get_voice_rag] = lambda: make_voice_rag()

    response = post_audio(client, data=b"too large")

    assert response.status_code == 413
    assert response.json()["error"]["type"] == "InvalidAudioError"


def test_configured_cors_origin_is_allowed(monkeypatch):
    monkeypatch.setenv("VOICE_RAG_ALLOWED_ORIGINS", "https://frontend.example.com")
    app = create_app()
    client = TestClient(app)

    response = client.options(
        "/voice/query",
        headers={
            "Origin": "https://frontend.example.com",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "https://frontend.example.com"


def configure_api_construction_mocks(monkeypatch, api_main, tts_cls):
    class EnvSTT:
        model = "mock-stt"
        language_code = "hi-IN"

        def __init__(self, timeout=30):
            self.timeout = timeout

        def transcribe(self, audio_path):
            return STTResult(
                text="mock transcript",
                language_code="hi-IN",
                provider="Mock",
                model=self.model,
                latency_ms=1.0,
            )

        def validate_audio(self, audio_path):
            return True

    class EnvRAGPipeline:
        def __init__(self, llm_provider=None, llm_model=None, llm_timeout_seconds=None):
            self.llm_provider = llm_provider
            self.llm_model = llm_model
            self.llm_timeout_seconds = llm_timeout_seconds

        def answer(self, query, language="hi"):
            return {
                "answer": "mock API answer",
                "grounded": True,
                "refused": False,
                "latency_ms": {"total_ms": 5.0, "llm_request_ms": 1.0},
            }

    monkeypatch.setattr(api_main, "SarvamSTT", EnvSTT)
    monkeypatch.setattr(api_main, "SarvamTTS", tts_cls)
    monkeypatch.setattr(api_main, "TextRAGPipeline", EnvRAGPipeline)


def test_tts_enabled_false_does_not_inject_tts(monkeypatch, tmp_path):
    import api.main as api_main

    calls = []

    class RecordingTTS(MockTTS):
        def __init__(self, timeout=30):
            super().__init__(model="mock:api", latency_ms=0.0)
            self.timeout = timeout

        def synthesize(self, text):
            calls.append(text)
            return super().synthesize(text)

    monkeypatch.setenv("VOICE_RAG_ENABLE_TTS", "false")
    monkeypatch.setenv("TTS_ENABLED", "false")
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    monkeypatch.setenv("LLM_MODEL", "mock-low-latency")
    configure_api_construction_mocks(monkeypatch, api_main, RecordingTTS)

    app = create_app()
    app.state.api_settings.temp_dir = tmp_path
    client = TestClient(app)

    response = post_audio(client)
    payload = response.json()

    assert response.status_code == 200
    assert payload["answer"] == "mock API answer"
    assert payload["tts_provider"] is None
    assert payload["tts_model"] is None
    assert payload["tts_latency_ms"] == 0.0
    assert payload["tts_audio_base64"] is None
    assert calls == []


def test_tts_enabled_true_injects_tts_and_returns_audio(monkeypatch, tmp_path):
    import api.main as api_main

    calls = []

    class RecordingTTS(MockTTS):
        def __init__(self, timeout=30):
            super().__init__(model="mock:api", latency_ms=0.0)
            self.timeout = timeout

        def synthesize(self, text):
            calls.append(text)
            return super().synthesize(text)

    monkeypatch.setenv("VOICE_RAG_ENABLE_TTS", "false")
    monkeypatch.setenv("TTS_ENABLED", "true")
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    monkeypatch.setenv("LLM_MODEL", "mock-low-latency")
    configure_api_construction_mocks(monkeypatch, api_main, RecordingTTS)

    app = create_app()
    app.state.api_settings.temp_dir = tmp_path
    client = TestClient(app)

    response = post_audio(client)
    payload = response.json()

    assert response.status_code == 200
    assert calls == ["mock API answer"]
    assert payload["tts_provider"] == "Mock"
    assert payload["tts_model"] == "mock:api"
    assert payload["tts_latency_ms"] == 0.0
    assert payload["tts_audio_base64"]
    assert payload["tts_audio_bytes"] > 0


def test_injected_tts_errors_are_captured(monkeypatch, tmp_path):
    import api.main as api_main

    class FailingInjectedTTS:
        def __init__(self, timeout=30):
            self.timeout = timeout

        def synthesize(self, text):
            raise RuntimeError("TTS provider down")

        def validate_text(self, text):
            return True

    monkeypatch.setenv("VOICE_RAG_ENABLE_TTS", "false")
    monkeypatch.setenv("TTS_ENABLED", "true")
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    monkeypatch.setenv("LLM_MODEL", "mock-low-latency")
    configure_api_construction_mocks(monkeypatch, api_main, FailingInjectedTTS)

    app = create_app()
    app.state.api_settings.temp_dir = tmp_path
    client = TestClient(app)

    response = post_audio(client)
    payload = response.json()

    assert response.status_code == 200
    assert payload["answer"] == "mock API answer"
    assert payload["tts_provider"] is None
    assert payload["tts_audio_base64"] is None
    assert "TTS synthesis failed" in payload["tts_error"]


def test_api_constructs_mock_llm_from_generic_env(monkeypatch, tmp_path):
    import api.main as api_main

    constructed = {}

    class EnvSTT:
        model = "mock-stt"
        language_code = "hi-IN"

        def __init__(self, timeout=30):
            self.timeout = timeout

        def transcribe(self, audio_path):
            return STTResult(
                text="mock transcript",
                language_code="hi-IN",
                provider="Mock",
                model=self.model,
                latency_ms=1.0,
            )

        def validate_audio(self, audio_path):
            return True

    class EnvRAGPipeline:
        def __init__(self, llm_provider=None, llm_model=None, llm_timeout_seconds=None):
            self.llm_client = LLMClient(provider=llm_provider, model=llm_model, timeout=llm_timeout_seconds)
            constructed["provider_arg"] = llm_provider
            constructed["model_arg"] = llm_model
            constructed["timeout_arg"] = llm_timeout_seconds
            constructed["llm_provider"] = self.llm_client.provider
            constructed["llm_model"] = self.llm_client.model

        def answer(self, query, language="hi"):
            answer, latency_ms = self.llm_client.generate(
                system_prompt="Answer in English.",
                user_prompt="Context here",
                max_tokens=20,
                temperature=0,
            )
            return {
                "answer": answer,
                "grounded": True,
                "refused": False,
                "latency_ms": {"total_ms": latency_ms, "llm_request_ms": latency_ms},
            }

    def fail_if_network_called(*args, **kwargs):
        raise AssertionError("Groq or another live LLM provider was called")

    monkeypatch.setenv("LLM_PROVIDER", "mock")
    monkeypatch.setenv("LLM_MODEL", "mock-low-latency")
    monkeypatch.setenv("GROQ_API_KEY", "test_key_that_must_not_be_used")
    monkeypatch.setattr(api_main, "SarvamSTT", EnvSTT)
    monkeypatch.setattr(api_main, "TextRAGPipeline", EnvRAGPipeline)
    monkeypatch.setattr("rag.llm_client.requests.post", fail_if_network_called)

    app = create_app()
    app.state.api_settings.temp_dir = tmp_path
    client = TestClient(app)

    response = post_audio(client)
    payload = response.json()

    assert response.status_code == 200
    assert constructed["provider_arg"] == "mock"
    assert constructed["model_arg"] == "mock-low-latency"
    assert constructed["timeout_arg"] == app.state.api_settings.llm_timeout_seconds
    assert constructed["llm_provider"] == "mock"
    assert constructed["llm_model"] == "mock-low-latency"
    assert payload["llm_latency_ms"] < 100.0
