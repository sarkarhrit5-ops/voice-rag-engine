"""
Base class for Speech-to-Text (STT) implementations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class STTResult:
    """Structured result from STT processing."""
    text: str
    language_code: str
    provider: str
    model: str
    latency_ms: float


class BaseSTT(ABC):
    """Abstract base class for Speech-to-Text implementations."""

    @abstractmethod
    def transcribe(self, audio_path: str) -> STTResult:
        """
        Transcribe audio file to text.

        Args:
            audio_path: Path to audio file

        Returns:
            STTResult: Structured transcription result

        Raises:
            ValueError: If audio is invalid or transcript is empty
            TimeoutError: If API request times out
            RuntimeError: For authentication or API errors
        """
        pass

    @abstractmethod
    def validate_audio(self, audio_path: str) -> bool:
        """
        Validate audio file before transcription.

        Args:
            audio_path: Path to audio file

        Returns:
            bool: True if audio is valid
        """
        pass
