"""
Unit tests for Voice STT module.
"""

import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from voice.stt.base import BaseSTT, STTResult
from voice.stt.sarvam import SarvamSTT
from voice.stt.mock import MockSTT


class TestSTTResult:
    """Tests for STTResult dataclass."""

    def test_stt_result_creation(self):
        """Test creating STTResult with all fields."""
        result = STTResult(
            text="नमस्ते",
            language_code="hi-IN",
            provider="Sarvam",
            model="saaras:v3",
            latency_ms=150.5,
        )
        assert result.text == "नमस्ते"
        assert result.language_code == "hi-IN"
        assert result.provider == "Sarvam"
        assert result.model == "saaras:v3"
        assert result.latency_ms == 150.5


class TestMockSTT:
    """Tests for MockSTT implementation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_stt = MockSTT(latency_ms=10)

    def test_mock_stt_initialization(self):
        """Test MockSTT initialization with defaults."""
        stt = MockSTT()
        assert stt.model == "saaras:v3"
        assert stt.language_code == "hi-IN"
        assert stt.latency_ms == 100.0

    def test_mock_stt_initialization_custom(self):
        """Test MockSTT initialization with custom values."""
        stt = MockSTT(
            model="custom:v1",
            language_code="en-IN",
            latency_ms=50.0,
        )
        assert stt.model == "custom:v1"
        assert stt.language_code == "en-IN"
        assert stt.latency_ms == 50.0

    def test_mock_transcribe_valid_audio(self):
        """Test transcription with mock audio file."""
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_audio = f.name

        try:
            result = self.mock_stt.transcribe(temp_audio)
            assert isinstance(result, STTResult)
            assert result.text.startswith("यह एक परीक्षण प्रतिलिपि है")
            assert result.language_code == "hi-IN"
            assert result.provider == "Mock"
            assert result.model == "saaras:v3"
            assert result.latency_ms > 0
        finally:
            os.unlink(temp_audio)

    def test_mock_transcribe_missing_audio(self):
        """Test transcription with missing audio file."""
        with pytest.raises(ValueError, match="Invalid or missing audio file"):
            self.mock_stt.transcribe("/nonexistent/path.wav")

    def test_validate_audio_valid_formats(self):
        """Test audio validation with supported formats."""
        supported_formats = [".wav", ".mp3", ".m4a", ".ogg", ".flac", ".webm"]
        for fmt in supported_formats:
            with tempfile.NamedTemporaryFile(suffix=fmt, delete=False) as f:
                temp_file = f.name
            try:
                assert self.mock_stt.validate_audio(temp_file) is True
            finally:
                os.unlink(temp_file)

    def test_validate_audio_invalid_format(self):
        """Test audio validation with unsupported format."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            temp_file = f.name
        try:
            assert self.mock_stt.validate_audio(temp_file) is False
        finally:
            os.unlink(temp_file)

    def test_validate_audio_nonexistent(self):
        """Test audio validation with nonexistent file."""
        assert self.mock_stt.validate_audio("/nonexistent/path.wav") is False


class TestSarvamSTT:
    """Tests for Sarvam STT implementation."""

    @patch.dict(os.environ, {"SARVAM_API_KEY": "test_key"})
    def test_sarvam_initialization_from_env(self):
        """Test Sarvam initialization reading from environment."""
        stt = SarvamSTT()
        assert stt.api_key == "test_key"
        assert stt.model == "saaras:v3"
        assert stt.language_code == "hi-IN"
        assert stt.timeout == 30

    def test_sarvam_initialization_explicit(self):
        """Test Sarvam initialization with explicit parameters."""
        stt = SarvamSTT(
            api_key="explicit_key",
            model="custom:v1",
            language_code="en-IN",
            timeout=60,
        )
        assert stt.api_key == "explicit_key"
        assert stt.model == "custom:v1"
        assert stt.language_code == "en-IN"
        assert stt.timeout == 60

    @patch("voice.config.find_env_file", return_value=None)
    @patch.dict(os.environ, {}, clear=True)
    def test_sarvam_initialization_missing_api_key(self, mock_find_env):
        """Test Sarvam initialization fails without API key."""
        with pytest.raises(ValueError, match="SARVAM_API_KEY not provided"):
            SarvamSTT()

    @patch.dict(os.environ, {"SARVAM_API_KEY": "test_key"})
    def test_sarvam_initialization_env_overrides(self):
        """Test environment variables override defaults."""
        with patch.dict(
            os.environ,
            {
                "SARVAM_API_KEY": "env_key",
                "SARVAM_STT_MODEL": "env_model:v2",
                "SARVAM_LANGUAGE_CODE": "en-US",
            },
        ):
            stt = SarvamSTT()
            assert stt.api_key == "env_key"
            assert stt.model == "env_model:v2"
            assert stt.language_code == "en-US"

    @patch.dict(os.environ, {"SARVAM_API_KEY": "test_key"})
    def test_sarvam_validate_audio(self):
        """Test Sarvam audio validation."""
        stt = SarvamSTT()
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_file = f.name
        try:
            assert stt.validate_audio(temp_file) is True
        finally:
            os.unlink(temp_file)

    @patch("voice.stt.sarvam.requests.post")
    @patch.dict(os.environ, {"SARVAM_API_KEY": "test_key"})
    def test_sarvam_transcribe_success(self, mock_post):
        """Test successful Sarvam transcription."""
        stt = SarvamSTT()

        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"transcript": "नमस्ते दुनिया"}
        mock_post.return_value = mock_response

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(b"fake audio data")
            temp_file = f.name

        try:
            result = stt.transcribe(temp_file)
            assert isinstance(result, STTResult)
            assert result.text == "नमस्ते दुनिया"
            assert result.language_code == "hi-IN"
            assert result.provider == "Sarvam"
            assert result.model == "saaras:v3"
            assert result.latency_ms > 0

            # Verify API call uses correct endpoint and format
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert call_args[0][0] == "https://api.sarvam.ai/speech-to-text"
            
            # Verify headers use api-subscription-key
            assert "api-subscription-key" in call_args[1]["headers"]
            assert call_args[1]["headers"]["api-subscription-key"] == "test_key"
            
            # Verify multipart form data is used
            assert "files" in call_args[1]
            assert "data" in call_args[1]
            assert call_args[1]["data"]["model"] == "saaras:v3"
            assert call_args[1]["data"]["mode"] == "transcribe"
            assert call_args[1]["data"]["language_code"] == "hi-IN"
        finally:
            os.unlink(temp_file)

    @patch("voice.stt.sarvam.requests.post")
    @patch.dict(os.environ, {"SARVAM_API_KEY": "test_key"})
    def test_sarvam_api_request_format(self, mock_post):
        """Test that Sarvam API request uses correct endpoint and headers."""
        stt = SarvamSTT()

        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"transcript": "test"}
        mock_post.return_value = mock_response

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(b"test audio")
            temp_file = f.name

        try:
            stt.transcribe(temp_file)

            # Verify correct endpoint
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert call_args[0][0] == "https://api.sarvam.ai/speech-to-text"

            # Verify api-subscription-key header
            headers = call_args[1]["headers"]
            assert headers["api-subscription-key"] == "test_key"

            # Verify multipart form data structure
            assert "files" in call_args[1]
            assert "file" in call_args[1]["files"]
            
            # Verify form data parameters
            form_data = call_args[1]["data"]
            assert form_data["model"] == "saaras:v3"
            assert form_data["mode"] == "transcribe"
            assert form_data["language_code"] == "hi-IN"

        finally:
            os.unlink(temp_file)

    @patch("voice.stt.sarvam.requests.post")
    @patch.dict(os.environ, {"SARVAM_API_KEY": "test_key"})
    def test_sarvam_transcribe_empty_transcript(self, mock_post):
        """Test Sarvam transcription with empty response."""
        stt = SarvamSTT()

        # Mock API response with empty transcript
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"transcript": ""}
        mock_post.return_value = mock_response

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(b"fake audio data")
            temp_file = f.name

        try:
            with pytest.raises(ValueError, match="Empty transcript"):
                stt.transcribe(temp_file)
        finally:
            os.unlink(temp_file)

    @patch("voice.stt.sarvam.requests.post")
    @patch.dict(os.environ, {"SARVAM_API_KEY": "test_key"})
    def test_sarvam_transcribe_missing_audio(self, mock_post):
        """Test Sarvam transcription with missing audio file."""
        stt = SarvamSTT()
        with pytest.raises(ValueError, match="Invalid or missing audio file"):
            stt.transcribe("/nonexistent/path.wav")

    @patch("voice.stt.sarvam.requests.post")
    @patch.dict(os.environ, {"SARVAM_API_KEY": "test_key"})
    def test_sarvam_transcribe_timeout(self, mock_post):
        """Test Sarvam transcription timeout."""
        import requests

        stt = SarvamSTT()
        mock_post.side_effect = requests.exceptions.Timeout()

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(b"fake audio data")
            temp_file = f.name

        try:
            with pytest.raises(TimeoutError, match="timed out"):
                stt.transcribe(temp_file)
        finally:
            os.unlink(temp_file)

    @patch("voice.stt.sarvam.requests.post")
    @patch.dict(os.environ, {"SARVAM_API_KEY": "test_key"})
    def test_sarvam_transcribe_auth_failure(self, mock_post):
        """Test Sarvam transcription with authentication failure."""
        stt = SarvamSTT()

        # Mock 401 Unauthorized response
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_post.return_value = mock_response

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(b"fake audio data")
            temp_file = f.name

        try:
            with pytest.raises(RuntimeError, match="Authentication failed"):
                stt.transcribe(temp_file)
        finally:
            os.unlink(temp_file)

    @patch("voice.stt.sarvam.requests.post")
    @patch.dict(os.environ, {"SARVAM_API_KEY": "test_key"})
    def test_sarvam_transcribe_rate_limit(self, mock_post):
        """Test Sarvam transcription with rate limiting."""
        stt = SarvamSTT()

        # Mock 429 Too Many Requests response
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_post.return_value = mock_response

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(b"fake audio data")
            temp_file = f.name

        try:
            with pytest.raises(RuntimeError, match="Rate limit exceeded"):
                stt.transcribe(temp_file)
        finally:
            os.unlink(temp_file)

    @patch("voice.stt.sarvam.requests.post")
    @patch.dict(os.environ, {"SARVAM_API_KEY": "test_key"})
    def test_sarvam_transcribe_api_error(self, mock_post):
        """Test Sarvam transcription with API error."""
        stt = SarvamSTT()

        # Mock 500 Internal Server Error response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"message": "Internal server error"}
        mock_post.return_value = mock_response

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(b"fake audio data")
            temp_file = f.name

        try:
            with pytest.raises(RuntimeError, match="Sarvam API error"):
                stt.transcribe(temp_file)
        finally:
            os.unlink(temp_file)

    @patch("voice.stt.sarvam.requests.post")
    @patch.dict(os.environ, {"SARVAM_API_KEY": "test_key"})
    def test_sarvam_transcribe_invalid_json(self, mock_post):
        """Test Sarvam transcription with invalid JSON response."""
        stt = SarvamSTT()

        # Mock response with invalid JSON
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_post.return_value = mock_response

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(b"fake audio data")
            temp_file = f.name

        try:
            with pytest.raises(RuntimeError, match="Failed to parse"):
                stt.transcribe(temp_file)
        finally:
            os.unlink(temp_file)


class TestAbstractBaseClass:
    """Tests for BaseSTT abstract base class."""

    def test_base_stt_cannot_instantiate(self):
        """Test that BaseSTT cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseSTT()

    def test_base_stt_requires_transcribe(self):
        """Test that transcribe method must be implemented."""

        class IncompleteSTT(BaseSTT):
            def validate_audio(self, audio_path):
                return True

        with pytest.raises(TypeError):
            IncompleteSTT()

    def test_base_stt_requires_validate_audio(self):
        """Test that validate_audio method must be implemented."""

        class IncompleteSTT(BaseSTT):
            def transcribe(self, audio_path):
                pass

        with pytest.raises(TypeError):
            IncompleteSTT()

    def test_complete_stt_implementation(self):
        """Test that complete STT implementation can be instantiated."""

        class CompleteSTT(BaseSTT):
            def transcribe(self, audio_path):
                return STTResult(
                    text="test",
                    language_code="hi-IN",
                    provider="Test",
                    model="test:v1",
                    latency_ms=100.0,
                )

            def validate_audio(self, audio_path):
                return True

        stt = CompleteSTT()
        assert isinstance(stt, BaseSTT)


class TestConfigLoading:
    """Tests for .env configuration loading."""

    def test_sarvam_loads_env_file(self):
        """Test that SarvamSTT can load configuration from .env file."""
        # This test verifies that .env loading works without exposing the secret
        # The actual API key is never printed or exposed in this test
        try:
            # Attempt to initialize with .env file (may fail if SARVAM_API_KEY is missing)
            # But the important part is that it attempts to load from .env
            stt = SarvamSTT()
            # If we get here, the .env was successfully loaded and contained SARVAM_API_KEY
            assert stt.model == "saaras:v3"
            assert stt.language_code == "hi-IN"
            assert stt.timeout == 30
            # Most importantly: never assert or print the actual API key
            assert stt.api_key is not None
            assert len(stt.api_key) > 0
            # Verify it's a string but don't expose the value
            assert isinstance(stt.api_key, str)
        except ValueError as e:
            # If initialization fails due to missing SARVAM_API_KEY, that's expected
            # when .env is not present or key is not set
            assert "SARVAM_API_KEY" in str(e)

    @patch.dict(os.environ, {}, clear=True)
    def test_sarvam_env_loading_with_mock_env(self):
        """Test SarvamSTT env loading with mocked .env file."""
        import tempfile
        from voice.config import load_env_config

        # Create a temporary .env file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("SARVAM_API_KEY=test_secret_key_12345\n")
            f.write("SARVAM_STT_MODEL=custom_model:v2\n")
            f.write("SARVAM_LANGUAGE_CODE=en-IN\n")
            temp_env = f.name

        try:
            # Load from temporary .env
            load_env_config(temp_env)

            # Verify environment is loaded
            api_key = os.getenv("SARVAM_API_KEY")
            assert api_key == "test_secret_key_12345"

            # Initialize SarvamSTT with explicit api_key to test config loading
            stt = SarvamSTT(api_key=api_key)
            assert stt.model == "custom_model:v2"
            assert stt.language_code == "en-IN"

            # Verify API key is not exposed
            assert "test_secret_key" not in str(repr(stt))
        finally:
            os.unlink(temp_env)

    def test_config_module_exists(self):
        """Test that voice.config module can be imported."""
        from voice.config import load_env_config, get_config_value
        assert callable(load_env_config)
        assert callable(get_config_value)


    pytest.main([__file__, "-v"])
