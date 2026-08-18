"""
Mock Speech-to-Text implementation for testing without API key.
"""

import time
from pathlib import Path
from voice.stt.base import BaseSTT, STTResult


class MockSTT(BaseSTT):
    """Mock Speech-to-Text implementation for testing."""

    def __init__(
        self,
        model: str = "saaras:v3",
        language_code: str = "hi-IN",
        latency_ms: float = 100.0,
    ):
        """
        Initialize Mock STT client.

        Args:
            model: Model identifier
            language_code: Language code
            latency_ms: Simulated latency in milliseconds
        """
        self.model = model
        self.language_code = language_code
        self.latency_ms = latency_ms

    def transcribe(self, audio_path: str) -> STTResult:
        """
        Return mock transcription result.

        Args:
            audio_path: Path to audio file

        Returns:
            STTResult: Mock transcription result
        """
        if not self.validate_audio(audio_path):
            raise ValueError(f"Invalid or missing audio file: {audio_path}")

        # Simulate API latency
        time.sleep(self.latency_ms / 1000.0)

        # Return mock transcript
        filename = Path(audio_path).stem
        mock_text = f"यह एक परीक्षण प्रतिलिपि है {filename} के लिए"

        return STTResult(
            text=mock_text,
            language_code=self.language_code,
            provider="Mock",
            model=self.model,
            latency_ms=self.latency_ms,
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
