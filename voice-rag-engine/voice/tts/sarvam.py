"""
Sarvam AI Text-to-Speech implementation.
"""

import base64
import time
from typing import Optional

import requests

from voice.config import get_config_value, load_env_config
from voice.tts.base import BaseTTS, TTSResult


class SarvamTTS(BaseTTS):
    """Text-to-Speech implementation using Sarvam AI."""

    API_BASE_URL = "https://api.sarvam.ai/text-to-speech"
    DEFAULT_MODEL = "bulbul:v2"
    DEFAULT_LANGUAGE = "hi-IN"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        language_code: Optional[str] = None,
        timeout: int = 30,
    ):
        load_env_config()

        self.api_key = api_key or get_config_value("SARVAM_API_KEY")
        if not self.api_key:
            raise ValueError(
                "SARVAM_API_KEY not provided and SARVAM_API_KEY environment "
                "variable is not set"
            )

        self.model = model or get_config_value("SARVAM_TTS_MODEL", self.DEFAULT_MODEL)
        self.language_code = (
            language_code or get_config_value("SARVAM_TTS_LANGUAGE_CODE", self.DEFAULT_LANGUAGE)
        )
        self.timeout = timeout

    def validate_text(self, text: str) -> bool:
        if not isinstance(text, str):
            return False
        return bool(text.strip())

    def synthesize(self, text: str, language_code: Optional[str] = None) -> TTSResult:
        if not self.validate_text(text):
            raise ValueError("Empty or invalid text provided for TTS synthesis")

        start_time = time.time()
        effective_lang = language_code or self.language_code
        tts_text = text.strip()

        # Map regional languages to optimal TTS acoustic voice models
        if effective_lang in ["as", "as-IN"]:
            effective_lang = "bn-IN"
        elif effective_lang in ["ne", "ne-IN", "sa", "sa-IN"]:
            effective_lang = "hi-IN"
        elif effective_lang in ["od", "or"]:
            effective_lang = "od-IN"

        # If language is Urdu (ur / ur-IN), convert script to Hindi phonetics for audio synthesis
        if effective_lang in ["ur", "ur-IN"] or any('\u0600' <= char <= '\u06FF' for char in tts_text):
            try:
                tr_resp = requests.post(
                    "https://api.sarvam.ai/translate",
                    headers={
                        "api-subscription-key": self.api_key,
                        "Content-Type": "application/json",
                    },
                    json={
                        "input": tts_text,
                        "source_language_code": "ur-IN",
                        "target_language_code": "hi-IN",
                        "model": "sarvam-translate:v1",
                    },
                    timeout=self.timeout,
                )
                if tr_resp.status_code == 200:
                    tts_text = tr_resp.json().get("translated_text", tts_text)
                    effective_lang = "hi-IN"
            except Exception:
                effective_lang = "hi-IN"

        try:
            response = requests.post(
                self.API_BASE_URL,
                headers={
                    "api-subscription-key": self.api_key,
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "text": tts_text,
                    "language_code": effective_lang,
                },
                timeout=self.timeout,
            )
        except requests.exceptions.Timeout:
            raise TimeoutError(
                f"Sarvam TTS API request timed out after {self.timeout} seconds"
            )
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Sarvam TTS API request failed: {e}")

        latency_ms = (time.time() - start_time) * 1000

        if response.status_code == 401:
            raise RuntimeError("Authentication failed: Invalid or expired API key")
        elif response.status_code == 429:
            raise RuntimeError("Rate limit exceeded. Please try again later.")
        elif response.status_code != 200:
            try:
                error_detail = response.json().get("message", response.text)
            except Exception:
                error_detail = response.text
            raise RuntimeError(
                f"Sarvam TTS API error ({response.status_code}): {error_detail}"
            )

        try:
            data = response.json()
            if isinstance(data, dict) and "audios" in data and data["audios"]:
                audio = b"".join(base64.b64decode(item) for item in data["audios"] if item)
            else:
                audio = response.content
        except Exception:
            audio = response.content

        if not audio:
            raise RuntimeError("Sarvam TTS API returned empty audio data")

        return TTSResult(
            audio=audio,
            language_code=self.language_code,
            provider="Sarvam",
            model=self.model,
            latency_ms=latency_ms,
        )
