"""API configuration helpers."""

from dataclasses import dataclass, field
import os
from pathlib import Path
from typing import Optional

from voice.config import load_env_config


SUPPORTED_AUDIO_EXTENSIONS = frozenset({".wav", ".mp3", ".m4a", ".ogg", ".flac", ".webm"})
SUPPORTED_AUDIO_MIME_TYPES = frozenset(
    {
        "audio/wav",
        "audio/x-wav",
        "audio/mpeg",
        "audio/mp3",
        "audio/mp4",
        "audio/ogg",
        "audio/flac",
        "audio/webm",
    }
)


def _get_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _get_any_bool(names: tuple[str, ...], default: bool = False) -> bool:
    values = [os.getenv(name) for name in names]
    if any(value is not None and value.strip().lower() in {"1", "true", "yes", "on"} for value in values):
        return True
    if any(value is not None for value in values):
        return False
    return default


def _get_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _get_csv(name: str, default: tuple[str, ...]) -> tuple[str, ...]:
    value = os.getenv(name)
    if value is None:
        return default
    items = tuple(item.strip() for item in value.split(",") if item.strip())
    return items or default


@dataclass
class APISettings:
    """Runtime settings for the production API layer."""

    app_name: str = "Voice RAG Engine"
    app_version: str = "0.1.0"
    host: str = "127.0.0.1"
    port: int = 8000
    allowed_cors_origins: tuple[str, ...] = (
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    )
    max_upload_bytes: int = 10 * 1024 * 1024
    request_timeout_seconds: float = 60.0
    stt_timeout_seconds: int = 30
    llm_timeout_seconds: float = 10.0
    tts_timeout_seconds: int = 30
    llm_provider: Optional[str] = None
    llm_model: Optional[str] = None
    enable_tts: bool = False
    temp_dir: Optional[Path] = None
    supported_extensions: frozenset[str] = field(default_factory=lambda: SUPPORTED_AUDIO_EXTENSIONS)
    supported_mime_types: frozenset[str] = field(default_factory=lambda: SUPPORTED_AUDIO_MIME_TYPES)


def load_api_settings() -> APISettings:
    """Load API settings from the existing environment configuration path."""
    load_env_config()
    max_upload_mb = _get_float("VOICE_RAG_MAX_UPLOAD_MB", 10.0)
    temp_dir_value = os.getenv("VOICE_RAG_TEMP_DIR")

    return APISettings(
        host=os.getenv("VOICE_RAG_API_HOST", "127.0.0.1"),
        port=max(1, _get_int("VOICE_RAG_API_PORT", 8000)),
        allowed_cors_origins=_get_csv(
            "VOICE_RAG_ALLOWED_ORIGINS",
            (
                "http://localhost:3000",
                "http://127.0.0.1:3000",
                "http://localhost:5173",
                "http://127.0.0.1:5173",
            ),
        ),
        max_upload_bytes=max(1, int(max_upload_mb * 1024 * 1024)),
        request_timeout_seconds=max(1.0, _get_float("VOICE_RAG_REQUEST_TIMEOUT_SECONDS", 60.0)),
        stt_timeout_seconds=max(1, _get_int("SARVAM_STT_TIMEOUT_SECONDS", 30)),
        llm_timeout_seconds=max(1.0, _get_float("LLM_TIMEOUT_SECONDS", 10.0)),
        tts_timeout_seconds=max(1, _get_int("SARVAM_TTS_TIMEOUT_SECONDS", 30)),
        llm_provider=os.getenv("LLM_PROVIDER"),
        llm_model=os.getenv("LLM_MODEL"),
        enable_tts=_get_any_bool(("VOICE_RAG_ENABLE_TTS", "TTS_ENABLED"), False),
        temp_dir=Path(temp_dir_value) if temp_dir_value else None,
    )
