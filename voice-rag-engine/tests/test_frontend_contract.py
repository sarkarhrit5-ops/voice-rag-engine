from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_frontend_no_longer_contains_generic_demo_answer():
    generic = (
        "It turns a spoken question into text, retrieves relevant multilingual evidence, "
        "checks that the answer is grounded, and responds only when the context supports it."
    )

    source_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (ROOT / "src").rglob("*")
        if path.suffix in {".ts", ".tsx"}
    )

    assert generic not in source_text
    assert "buildDemoResponse" not in source_text
    assert "isDemo" not in source_text


def test_frontend_api_maps_real_backend_fields():
    api_source = (ROOT / "src" / "lib" / "api.ts").read_text(encoding="utf-8")

    assert "payload.transcript" in api_source
    assert "payload.refused" in api_source
    assert "payload.retrieved_passages" in api_source
    assert "payload.tts_audio_base64" in api_source
    assert "payload.latency_ms" in api_source
    assert 'buildApiUrl("/voice/query")' in api_source
    assert 'buildApiUrl("/health")' in api_source


def test_frontend_requires_explicit_api_configuration():
    api_source = (ROOT / "src" / "lib" / "api.ts").read_text(encoding="utf-8")
    route_source = (ROOT / "src" / "routes" / "index.tsx").read_text(encoding="utf-8")

    assert "VITE_VOICE_RAG_API_URL" in api_source
    assert '"http://127.0.0.1:8000"' not in api_source
    assert "BACKEND_NOT_CONFIGURED" in api_source
    assert "The voice API is not configured" in route_source
    assert "FastAPI is unavailable" in api_source
