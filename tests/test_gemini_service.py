"""Unit tests for GeminiService configuration and behavior."""

import pytest
from unittest.mock import MagicMock, patch
from core.gemini_service import GeminiService


def test_gemini_service_initialization_no_key():
    service = GeminiService(api_key=None)
    # Should report not configured if env var empty
    with patch.dict("os.environ", {}, clear=True):
        svc = GeminiService(api_key=None)
        assert svc.is_configured() is False


def test_gemini_service_initialization_with_key():
    service = GeminiService(api_key="test-key-123")
    assert service.is_configured() is True
    assert service.api_key == "test-key-123"


def test_gemini_service_generate_without_key_raises():
    with patch.dict("os.environ", {}, clear=True):
        service = GeminiService(api_key=None)
        with pytest.raises(ValueError, match="GEMINI_API_KEY is required"):
            service.generate(prompt="Hello")


@patch("core.gemini_service.genai.Client")
def test_gemini_service_successful_generation(mock_client_cls):
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client

    mock_response = MagicMock()
    mock_response.text = "All tests passed"
    mock_client.models.generate_content.return_value = mock_response

    service = GeminiService(api_key="fake-test-key")
    result = service.generate(prompt="Test prompt")
    assert result == "All tests passed"
