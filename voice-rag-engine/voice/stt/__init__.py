"""
Speech-to-Text (STT) Module

Provides interface and implementations for converting speech to text.
"""

from voice.stt.base import BaseSTT
from voice.stt.sarvam import SarvamSTT
from voice.stt.mock import MockSTT

__all__ = ["BaseSTT", "SarvamSTT", "MockSTT"]
