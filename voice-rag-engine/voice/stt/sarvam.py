"""
Sarvam AI Speech-to-Text implementation.
"""

import os
import time
import requests
from pathlib import Path
from typing import Optional
from voice.stt.base import BaseSTT, STTResult
from voice.config import load_env_config, get_config_value


class SarvamSTT(BaseSTT):
    """Speech-to-Text implementation using Sarvam AI."""

    API_BASE_URL = "https://api.sarvam.ai/speech-to-text"
    DEFAULT_MODEL = "saaras:v3"
    DEFAULT_LANGUAGE = "hi-IN"
    DEFAULT_MODE = "transcribe"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        language_code: Optional[str] = None,
        timeout: int = 30,
    ):
        """
        Initialize Sarvam STT client.

        Args:
            api_key: Sarvam API key. If None, reads from SARVAM_API_KEY env var or .env
            model: Model to use. Defaults to saaras:v3
            language_code: Language code. Defaults to hi-IN
            timeout: Request timeout in seconds

        Raises:
            ValueError: If API key is not provided or found
        """
        # Load environment from .env file
        load_env_config()

        self.api_key = api_key or get_config_value("SARVAM_API_KEY")
        if not self.api_key:
            raise ValueError(
                "SARVAM_API_KEY not provided and SARVAM_API_KEY environment "
                "variable is not set"
            )

        self.model = model or get_config_value("SARVAM_STT_MODEL", self.DEFAULT_MODEL)
        self.language_code = (
            language_code or get_config_value("SARVAM_LANGUAGE_CODE", self.DEFAULT_LANGUAGE)
        )
        self.timeout = timeout

    def transcribe(self, audio_path: str, language_code: Optional[str] = None) -> STTResult:
        """
        Transcribe audio file using Sarvam AI.

        Args:
            audio_path: Path to audio file
            language_code: Optional language code override (e.g. 'hi-IN', 'en-IN', 'ta-IN', 'unknown')

        Returns:
            STTResult: Structured transcription result
        """
        # Validate audio file
        if not self.validate_audio(audio_path):
            raise ValueError(f"Invalid or missing audio file: {audio_path}")

        # Read audio file
        try:
            with open(audio_path, "rb") as f:
                audio_data = f.read()
        except IOError as e:
            raise ValueError(f"Failed to read audio file: {e}")

        # Call Sarvam API
        start_time = time.time()
        effective_lang = language_code or self.language_code
        try:
            # Determine MIME type based on file extension
            audio_path_obj = Path(audio_path)
            mime_type_map = {
                ".wav": "audio/wav",
                ".mp3": "audio/mpeg",
                ".m4a": "audio/mp4",
                ".ogg": "audio/ogg",
                ".flac": "audio/flac",
                ".webm": "audio/webm",
            }
            mime_type = mime_type_map.get(audio_path_obj.suffix.lower(), "audio/wav")

            # Prepare multipart form data
            files = {
                "file": ("audio", audio_data, mime_type),
            }
            data = {
                "model": self.model,
                "mode": self.DEFAULT_MODE,
                "language_code": effective_lang,
            }
            headers = {
                "api-subscription-key": self.api_key,
            }

            response = requests.post(
                self.API_BASE_URL,
                files=files,
                data=data,
                headers=headers,
                timeout=self.timeout,
            )
        except requests.exceptions.Timeout:
            raise TimeoutError(
                f"Sarvam API request timed out after {self.timeout} seconds"
            )
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Sarvam API request failed: {e}")

        latency_ms = (time.time() - start_time) * 1000

        # Handle API response
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
                f"Sarvam API error ({response.status_code}): {error_detail}"
            )

        # Parse response
        try:
            result = response.json()
        except ValueError as e:
            raise RuntimeError(f"Failed to parse Sarvam API response: {e}")

        # Extract transcript
        text = result.get("transcript", "").strip()
        if not text:
            raise ValueError("Empty transcript returned from Sarvam API")

        return STTResult(
            text=text,
            language_code=self.language_code,
            provider="Sarvam",
            model=self.model,
            latency_ms=latency_ms,
        )

    def validate_audio(self, audio_path: str) -> bool:
        """
        Validate audio file exists and has valid extension.

        Args:
            audio_path: Path to audio file

        Returns:
            bool: True if audio file is valid
        """
        path = Path(audio_path)
        if not path.exists():
            return False

        # Check for supported audio formats
        supported_formats = {".wav", ".mp3", ".m4a", ".ogg", ".flac", ".webm"}
        return path.suffix.lower() in supported_formats
