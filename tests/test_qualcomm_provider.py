"""Unit tests for QualcommAIProvider with mocked HTTP requests."""

import json
import pytest
from unittest.mock import patch, MagicMock
import requests

from src.providers.qualcomm import QualcommAIProvider
from src.providers.base import (
    AuthenticationError,
    QuotaExceededError,
    ProviderTimeoutError,
    ProviderConnectionError,
    MalformedResponseError,
)


@pytest.fixture
def mock_qualcomm_provider():
    return QualcommAIProvider(
        api_key="mock_test_key_12345",
        base_url="https://api.qualcomm.com/ai/v2",
        model_name="Llama-3.1-8B",
        timeout=10,
    )


def test_provider_is_configured_true(mock_qualcomm_provider):
    is_ready, _ = mock_qualcomm_provider.is_configured()
    assert is_ready is True


def test_provider_is_configured_false():
    p = QualcommAIProvider(api_key="", base_url="")
    is_ready, msg = p.is_configured()
    assert is_ready is False
    assert "not set" in msg


def test_successful_extraction(mock_qualcomm_provider):
    mock_llm_json = {
        "meeting_title": "Sprint Sync",
        "summary": "Team aligned on release dates.",
        "key_topics": ["Release"],
        "decisions": [
            {"description": "Interface review tomorrow", "status": "confirmed", "evidence": "agreed"}
        ],
        "action_items": [
            {
                "task": "Finish API integration",
                "owner": "Rahul",
                "deadline_text": "Friday",
                "priority": "high",
                "status": "not_started",
                "confidence": 0.95,
                "evidence": "Rahul will finish the API integration by Friday."
            }
        ],
        "risks": [],
        "open_questions": []
    }

    mock_resp = MagicMock()
    mock_resp.ok = True
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [
            {"message": {"content": json.dumps(mock_llm_json)}}
        ]
    }

    with patch("requests.post", return_value=mock_resp):
        analysis = mock_qualcomm_provider.extract_meeting_action_items(
            transcript="Rahul will finish the API integration by Friday."
        )

    assert analysis.summary == "Team aligned on release dates."
    assert len(analysis.action_items) == 1
    assert analysis.action_items[0].owner == "Rahul"
    assert analysis.action_items[0].deadline_text == "Friday"
    assert analysis.source_provider == "qualcomm_live"
    assert analysis.is_sample_data is False


def test_authentication_failure_401(mock_qualcomm_provider):
    mock_resp = MagicMock()
    mock_resp.ok = False
    mock_resp.status_code = 401
    mock_resp.text = "Unauthorized: Invalid API Key"

    with patch("requests.post", return_value=mock_resp):
        with pytest.raises(AuthenticationError, match="Authentication failed"):
            mock_qualcomm_provider.extract_meeting_action_items(transcript="Meeting text")


def test_quota_exceeded_429(mock_qualcomm_provider):
    mock_resp = MagicMock()
    mock_resp.ok = False
    mock_resp.status_code = 429
    mock_resp.text = "Rate limit reached or credits exhausted."

    with patch("requests.post", return_value=mock_resp):
        with pytest.raises(QuotaExceededError, match="credit budget exhausted"):
            mock_qualcomm_provider.extract_meeting_action_items(transcript="Meeting text")


def test_timeout_error(mock_qualcomm_provider):
    with patch("requests.post", side_effect=requests.exceptions.Timeout("Timed out")):
        with pytest.raises(ProviderTimeoutError, match="timed out"):
            mock_qualcomm_provider.extract_meeting_action_items(transcript="Meeting text")


def test_connection_error(mock_qualcomm_provider):
    with patch("requests.post", side_effect=requests.exceptions.ConnectionError("Failed to connect")):
        with pytest.raises(ProviderConnectionError, match="Could not connect"):
            mock_qualcomm_provider.extract_meeting_action_items(transcript="Meeting text")


def test_malformed_response_json(mock_qualcomm_provider):
    mock_resp = MagicMock()
    mock_resp.ok = True
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [
            {"message": {"content": "This is plain text with no JSON."}}
        ]
    }

    with patch("requests.post", return_value=mock_resp):
        with pytest.raises(MalformedResponseError, match="Failed to validate"):
            mock_qualcomm_provider.extract_meeting_action_items(transcript="Meeting text")


def test_test_connection_diagnostics(mock_qualcomm_provider):
    mock_resp = MagicMock()
    mock_resp.ok = True
    mock_resp.status_code = 200

    with patch("requests.post", return_value=mock_resp):
        ok, msg = mock_qualcomm_provider.test_connection()
        assert ok is True
        assert "Successfully connected" in msg
