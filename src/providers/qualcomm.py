"""Qualcomm AI Playground / Inference Suite integration adapter.

This module provides a production-grade adapter for the Qualcomm AI Playground,
Qualcomm AI Inference Suite, and compatible cloud or on-prem endpoints.
All configuration is loaded via environment variables without hardcoded secrets.
"""

import os
import json
import logging
from typing import Optional, Tuple, Dict, Any
import requests
from dotenv import load_dotenv

from src.schemas import MeetingAnalysis
from src.extraction import build_extraction_prompt, extract_structured_analysis
from src.providers.base import (
    BaseAIProvider,
    AIProviderError,
    AuthenticationError,
    QuotaExceededError,
    ProviderTimeoutError,
    MalformedResponseError,
    ProviderConnectionError,
)

# Load environment variables from .env
load_dotenv()

logger = logging.getLogger(__name__)


class QualcommAIProvider(BaseAIProvider):
    """Client for Qualcomm AI Playground / AI Inference Suite."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model_name: Optional[str] = None,
        timeout: Optional[int] = None,
    ):
        # Support Cirrascale INFERENCE_CLOUD_*, QUALCOMM_*, and IMAGINE_* conventions
        if api_key is not None:
            self.api_key = api_key.strip()
        else:
            self.api_key = (
                os.getenv("INFERENCE_CLOUD_API_KEY")
                or os.getenv("QUALCOMM_API_KEY")
                or os.getenv("IMAGINE_API_KEY")
                or ""
            ).strip()

        if base_url is not None:
            raw_base_url = base_url.strip()
        else:
            raw_base_url = (
                os.getenv("INFERENCE_CLOUD_ENDPOINT")
                or os.getenv("QUALCOMM_API_BASE_URL")
                or os.getenv("IMAGINE_ENDPOINT_URL")
                or "https://aisuite.cirrascale.com/apis/v2"
            ).strip()

        # Normalize endpoint URL
        self.base_url = raw_base_url.rstrip("/")
        if not self.base_url.endswith("/chat/completions"):
            self.endpoint_url = f"{self.base_url}/chat/completions"
        else:
            self.endpoint_url = self.base_url

        self.model_name = (
            model_name
            or os.getenv("QUALCOMM_MODEL_NAME")
            or "llama-3.1-8B"
        ).strip()

        env_timeout = os.getenv("QUALCOMM_TIMEOUT_SECONDS", "45")
        try:
            self.timeout = int(timeout or env_timeout)
        except ValueError:
            self.timeout = 45

    @property
    def provider_name(self) -> str:
        return "Qualcomm AI Playground"

    def is_configured(self) -> Tuple[bool, str]:
        """Validates whether minimum required configuration is present."""
        if not self.api_key:
            return (
                False,
                "INFERENCE_CLOUD_API_KEY (or QUALCOMM_API_KEY) is not set in environment or .env.",
            )
        if not self.base_url:
            return (
                False,
                "INFERENCE_CLOUD_ENDPOINT (or QUALCOMM_API_BASE_URL) is not set.",
            )
        return True, "Configured"

    def _prepare_headers(self) -> Dict[str, str]:
        """Builds HTTP headers including authorization and API key headers."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "MeetingMindAI-QualcommClient/1.0",
        }

    def extract_meeting_action_items(
        self,
        transcript: str,
        meeting_title: Optional[str] = None,
        meeting_date: Optional[str] = None,
    ) -> MeetingAnalysis:
        """Sends meeting notes to the Qualcomm AI endpoint and parses the structured response.
        
        Optimized for hackathon usage: single extraction request, zero redundant calls.
        """
        is_ready, reason = self.is_configured()
        if not is_ready:
            raise AuthenticationError(
                f"Cannot invoke Live AI: {reason}. Please configure .env or use Sample Mode.",
                provider_name=self.provider_name,
            )

        if not transcript or not transcript.strip():
            raise AIProviderError(
                "Cannot analyze empty meeting notes. Please provide text input.",
                provider_name=self.provider_name,
            )

        system_prompt, user_prompt = build_extraction_prompt(
            transcript=transcript,
            meeting_title=meeting_title,
            meeting_date=meeting_date,
        )

        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.1,
            "max_tokens": 2500,
            "stream": False,
        }

        headers = self._prepare_headers()

        logger.info(
            f"Dispatching single inference request to Qualcomm AI Playground ({self.endpoint_url}) "
            f"using model '{self.model_name}'..."
        )

        try:
            response = requests.post(
                self.endpoint_url,
                headers=headers,
                json=payload,
                timeout=self.timeout,
            )
        except requests.exceptions.Timeout as exc:
            raise ProviderTimeoutError(
                f"Qualcomm AI request timed out after {self.timeout} seconds. "
                "Check server load or increase QUALCOMM_TIMEOUT_SECONDS in .env.",
                provider_name=self.provider_name,
            ) from exc
        except requests.exceptions.ConnectionError as exc:
            raise ProviderConnectionError(
                f"Could not connect to Qualcomm AI endpoint at {self.endpoint_url}. "
                "Check network connectivity or endpoint URL.",
                provider_name=self.provider_name,
            ) from exc
        except requests.exceptions.RequestException as exc:
            raise AIProviderError(
                f"Network request to Qualcomm AI failed: {str(exc)}",
                provider_name=self.provider_name,
            ) from exc

        # Handle HTTP status codes
        if response.status_code in (401, 403):
            raise AuthenticationError(
                f"Authentication failed (HTTP {response.status_code}). "
                "The provided QUALCOMM_API_KEY is invalid or lacks access to this model.",
                provider_name=self.provider_name,
                status_code=response.status_code,
            )

        if response.status_code == 429:
            raise QuotaExceededError(
                f"Rate limit reached or credit budget exhausted (HTTP 429). "
                "Please verify your Qualcomm AI Playground credit allocation ($3 budget).",
                provider_name=self.provider_name,
                status_code=response.status_code,
            )

        if response.status_code >= 500:
            raise AIProviderError(
                f"Qualcomm AI Playground server error (HTTP {response.status_code}). "
                f"Details: {response.text[:300]}",
                provider_name=self.provider_name,
                status_code=response.status_code,
            )

        if not response.ok:
            raise AIProviderError(
                f"Qualcomm API responded with HTTP {response.status_code}: {response.text[:300]}",
                provider_name=self.provider_name,
                status_code=response.status_code,
            )

        # Extract message content from response
        try:
            resp_data = response.json()
        except ValueError as exc:
            raise MalformedResponseError(
                f"Qualcomm endpoint returned invalid non-JSON HTTP body: {response.text[:200]}",
                provider_name=self.provider_name,
            ) from exc

        raw_content = ""
        # Check standard OpenAI chat completion format
        if "choices" in resp_data and len(resp_data["choices"]) > 0:
            choice = resp_data["choices"][0]
            if "message" in choice and "content" in choice["message"]:
                raw_content = choice["message"]["content"]
            elif "text" in choice:
                raw_content = choice["text"]
        elif "content" in resp_data:
            raw_content = resp_data["content"]
        elif "response" in resp_data:
            raw_content = resp_data["response"]
        else:
            raise MalformedResponseError(
                f"Unexpected response format from Qualcomm API: {json.dumps(resp_data)[:250]}",
                provider_name=self.provider_name,
            )

        try:
            analysis = extract_structured_analysis(
                raw_json_str=raw_content,
                source_transcript=transcript,
                meeting_title=meeting_title,
                meeting_date=meeting_date,
                source_provider="qualcomm_live",
            )
            analysis.is_sample_data = False
            return analysis
        except Exception as exc:
            raise MalformedResponseError(
                f"Failed to validate structured AI output from Qualcomm model: {str(exc)}",
                provider_name=self.provider_name,
            ) from exc

    def test_connection(self) -> Tuple[bool, str]:
        """Tests connectivity and authentication against Qualcomm endpoint with minimal token consumption."""
        is_ready, reason = self.is_configured()
        if not is_ready:
            return False, reason

        test_payload = {
            "model": self.model_name,
            "messages": [
                {"role": "user", "content": "ping"}
            ],
            "max_tokens": 2,
            "temperature": 0.0,
        }

        try:
            resp = requests.post(
                self.endpoint_url,
                headers=self._prepare_headers(),
                json=test_payload,
                timeout=min(self.timeout, 10),
            )
            if resp.status_code in (401, 403):
                return False, f"Authentication failed (HTTP {resp.status_code}). Invalid QUALCOMM_API_KEY."
            if resp.status_code == 429:
                return False, "Rate limit reached or credits exhausted (HTTP 429)."
            if resp.ok:
                return True, f"Successfully connected to Qualcomm AI Playground ({self.model_name})."
            return False, f"Endpoint responded with HTTP {resp.status_code}: {resp.text[:150]}"
        except requests.exceptions.Timeout:
            return False, f"Connection timed out after 10s connecting to {self.endpoint_url}."
        except requests.exceptions.ConnectionError:
            return False, f"Cannot reach host at {self.endpoint_url}."
        except Exception as exc:
            return False, f"Connection diagnostic error: {str(exc)}"
