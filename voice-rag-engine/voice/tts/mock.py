"""
Mock Text-to-Speech implementation for testing without API key.
"""

import time

from voice.tts.base import BaseTTS, TTSResult


class MockTTS(BaseTTS):
    """Mock Text-to-Speech implementation for testing."""

    def __init__(
        self,
        model: str = "mock:v1",
        language_code: str = "hi-IN",
        latency_ms: float = 25.0,
    ):
        self.model = model
        self.language_code = language_code
        self.latency_ms = latency_ms

    def validate_text(self, text: str) -> bool:
        if not isinstance(text, str):
            return False
        return bool(text.strip())

    def synthesize(self, text: str) -> TTSResult:
        if not self.validate_text(text):
            raise ValueError("Empty or invalid text provided for TTS synthesis")

        time.sleep(self.latency_ms / 1000.0)
        audio = f"mock-audio:{text.strip()}".encode("utf-8")

        return TTSResult(
            audio=audio,
            language_code=self.language_code,
            provider="Mock",
            model=self.model,
            latency_ms=self.latency_ms,
        )
