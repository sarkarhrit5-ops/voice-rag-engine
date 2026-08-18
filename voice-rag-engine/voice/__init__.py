"""
Voice Processing Module

Handles speech-to-text (STT) and related voice processing tasks.
"""

from voice.stt.base import BaseSTT
from voice.stt.sarvam import SarvamSTT
from voice.stt.mock import MockSTT

__all__ = ["BaseSTT", "SarvamSTT", "MockSTT"]
