import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from voice.tts.base import BaseTTS, TTSResult
from voice.tts.mock import MockTTS
from voice.tts.sarvam import SarvamTTS


class TestTTSResult:
    def test_tts_result_creation(self):
        result = TTSResult(
            audio=b"fake-audio-bytes",
            language_code="hi-IN",
            provider="Sarvam",
            model="bulbul:v2",
            latency_ms=120.5,
        )
        assert result.audio == b"fake-audio-bytes"
        assert result.language_code == "hi-IN"
        assert result.provider == "Sarvam"
        assert result.model == "bulbul:v2"
        assert result.latency_ms == 120.5


class TestAbstractBaseClass:
    def test_base_tts_cannot_instantiate(self):
        with pytest.raises(TypeError):
            BaseTTS()

    def test_base_tts_requires_synthesize(self):
        class IncompleteTTS(BaseTTS):
            def validate_text(self, text):
                return True

        with pytest.raises(TypeError):
            IncompleteTTS()

    def test_base_tts_requires_validate_text(self):
        class IncompleteTTS(BaseTTS):
            def synthesize(self, text):
                return TTSResult(
                    audio=b"test",
                    language_code="hi-IN",
                    provider="Test",
                    model="test:v1",
                    latency_ms=1.0,
                )

        with pytest.raises(TypeError):
            IncompleteTTS()


class TestMockTTS:
    def test_mock_tts_initialization(self):
        tts = MockTTS(model="mock:v1", language_code="en-IN", latency_ms=25.0)
        assert tts.model == "mock:v1"
        assert tts.language_code == "en-IN"
        assert tts.latency_ms == 25.0

    def test_mock_tts_synthesizes_deterministic_audio(self):
        tts = MockTTS()
        result = tts.synthesize("नमस्ते दुनिया")
        assert isinstance(result, TTSResult)
        assert result.provider == "Mock"
        assert result.model == "mock:v1"
        assert result.language_code == "hi-IN"
        assert result.audio == "mock-audio:नमस्ते दुनिया".encode("utf-8")
        assert result.latency_ms >= 0.0

    def test_mock_tts_rejects_invalid_text(self):
        tts = MockTTS()
        with pytest.raises(ValueError, match="Empty or invalid text"):
            tts.synthesize("   ")


class TestSarvamTTS:
    @patch.dict(os.environ, {"SARVAM_API_KEY": "test_key"}, clear=True)
    def test_sarvam_initialization_from_env(self):
        tts = SarvamTTS()
        assert tts.api_key == "test_key"
        assert tts.model == "bulbul:v2"
        assert tts.language_code == "hi-IN"
        assert tts.timeout == 30

    @patch.dict(os.environ, {"SARVAM_API_KEY": "test_key"}, clear=True)
    def test_sarvam_initialization_explicit(self):
        tts = SarvamTTS(api_key="explicit_key", model="voice:v1", language_code="en-IN", timeout=45)
        assert tts.api_key == "explicit_key"
        assert tts.model == "voice:v1"
        assert tts.language_code == "en-IN"
        assert tts.timeout == 45

    @patch.dict(os.environ, {}, clear=True)
    @patch("voice.config.find_env_file", return_value=None)
    def test_sarvam_initialization_missing_api_key(self, mock_find_env):
        with pytest.raises(ValueError, match="SARVAM_API_KEY not provided"):
            SarvamTTS()

    @patch.dict(os.environ, {"SARVAM_API_KEY": "test_key"}, clear=True)
    def test_sarvam_configuration_loading(self):
        with patch.dict(os.environ, {"SARVAM_TTS_MODEL": "voice:test", "SARVAM_TTS_LANGUAGE_CODE": "en-IN"}):
            tts = SarvamTTS()
            assert tts.model == "voice:test"
            assert tts.language_code == "en-IN"

    @patch("voice.tts.sarvam.requests.post")
    @patch.dict(os.environ, {"SARVAM_API_KEY": "test_key"}, clear=True)
    def test_sarvam_synthesizes_success(self, mock_post):
        tts = SarvamTTS()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"fake-audio-bytes"
        mock_post.return_value = mock_response

        result = tts.synthesize("नमस्ते दुनिया")

        assert isinstance(result, TTSResult)
        assert result.audio == b"fake-audio-bytes"
        assert result.language_code == "hi-IN"
        assert result.provider == "Sarvam"
        assert result.model == "bulbul:v2"
        assert result.latency_ms > 0

        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://api.sarvam.ai/text-to-speech"
        assert call_args[1]["headers"]["api-subscription-key"] == "test_key"

    @patch("voice.tts.sarvam.requests.post")
    @patch.dict(os.environ, {"SARVAM_API_KEY": "test_key"}, clear=True)
    def test_sarvam_authentication_failure(self, mock_post):
        tts = SarvamTTS()
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_post.return_value = mock_response

        with pytest.raises(RuntimeError, match="Authentication failed"):
            tts.synthesize("नमस्ते")

    @patch("voice.tts.sarvam.requests.post")
    @patch.dict(os.environ, {"SARVAM_API_KEY": "test_key"}, clear=True)
    def test_sarvam_timeout(self, mock_post):
        import requests

        tts = SarvamTTS(timeout=1)
        mock_post.side_effect = requests.exceptions.Timeout()

        with pytest.raises(TimeoutError, match="timed out"):
            tts.synthesize("नमस्ते")

    @patch("voice.tts.sarvam.requests.post")
    @patch.dict(os.environ, {"SARVAM_API_KEY": "test_key"}, clear=True)
    def test_sarvam_api_failure(self, mock_post):
        tts = SarvamTTS()
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal server error"
        mock_post.return_value = mock_response

        with pytest.raises(RuntimeError, match="Sarvam TTS API error"):
            tts.synthesize("नमस्ते")

    @patch("voice.tts.sarvam.requests.post")
    @patch.dict(os.environ, {"SARVAM_API_KEY": "test_key"}, clear=True)
    def test_sarvam_response_parsing(self, mock_post):
        tts = SarvamTTS()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"parsed-audio"
        mock_post.return_value = mock_response

        result = tts.synthesize("नमस्ते")
        assert result.audio == b"parsed-audio"

    def test_sarvam_rejects_invalid_or_empty_text(self):
        tts = SarvamTTS(api_key="test_key")
        with pytest.raises(ValueError, match="Empty or invalid text"):
            tts.synthesize("   ")
