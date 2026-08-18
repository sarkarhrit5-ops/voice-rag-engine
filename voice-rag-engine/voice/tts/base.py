"""
Base class for Text-to-Speech (TTS) implementations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class TTSResult:
    """Structured result from TTS processing."""

    audio: bytes
    language_code: str
    provider: str
    model: str
    latency_ms: float


class BaseTTS(ABC):
    """Abstract base class for Text-to-Speech implementations."""

    @abstractmethod
    def synthesize(self, text: str) -> TTSResult:
        """
        Convert text to spoken audio.

        Args:
            text: Input text to synthesize

        Returns:
            TTSResult: Structured TTS output

        Raises:
            ValueError: If text is empty or invalid
            TimeoutError: If API request times out
            RuntimeError: For authentication or API errors
        """
        pass

    @abstractmethod
    def validate_text(self, text: str) -> bool:
        """
        Validate text before synthesis.

        Args:
            text: Text to validate

        Returns:
            bool: True if text is valid for synthesis
        """
        pass
