"""Base AI Provider interface and exception definitions."""

from abc import ABC, abstractmethod
from typing import Optional, Tuple
from src.schemas import MeetingAnalysis


class AIProviderError(Exception):
    """Base exception for all AI provider communication failures."""
    def __init__(self, message: str, provider_name: str = "Unknown", status_code: Optional[int] = None):
        super().__init__(message)
        self.message = message
        self.provider_name = provider_name
        self.status_code = status_code


class AuthenticationError(AIProviderError):
    """Raised when API credentials are missing, expired, or invalid (401/403)."""
    pass


class QuotaExceededError(AIProviderError):
    """Raised when rate limits or account credit budgets ($3 hackathon credits) are exhausted (429)."""
    pass


class ProviderTimeoutError(AIProviderError):
    """Raised when a request exceeds the configured network timeout threshold."""
    pass


class MalformedResponseError(AIProviderError):
    """Raised when the LLM returns invalid JSON or content violating the structured schema."""
    pass


class ProviderConnectionError(AIProviderError):
    """Raised when network connectivity fails or the host is unreachable."""
    pass


class BaseAIProvider(ABC):
    """Abstract interface decoupling the UI application from concrete LLM backends."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the provider (e.g. 'Qualcomm AI Playground')."""
        pass

    @abstractmethod
    def is_configured(self) -> Tuple[bool, str]:
        """Checks if necessary credentials and endpoints are present in the environment."""
        pass

    @abstractmethod
    def extract_meeting_action_items(
        self,
        transcript: str,
        meeting_title: Optional[str] = None,
        meeting_date: Optional[str] = None,
    ) -> MeetingAnalysis:
        """Sends meeting notes to the provider and returns validated MeetingAnalysis."""
        pass

    @abstractmethod
    def test_connection(self) -> Tuple[bool, str]:
        """Performs a lightweight ping or diagnostic check against the provider endpoint."""
        pass
