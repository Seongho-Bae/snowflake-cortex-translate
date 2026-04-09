"""Application service interfaces for translation operations."""

from dataclasses import dataclass
from typing import Protocol

from cortex_translate_service.domain import TranslationRequest, TranslationResult


class TranslationGatewayError(RuntimeError):
    """Raised when the translation gateway cannot complete a request."""


class TranslationGateway(Protocol):
    """Protocol for infrastructure adapters that can translate text."""

    def translate(self, request: TranslationRequest) -> TranslationResult:
        """Translate the provided request and return the result."""


@dataclass(slots=True)
class TranslationService:
    """Application service that coordinates translation requests."""

    gateway: TranslationGateway

    def translate(self, request: TranslationRequest) -> TranslationResult:
        """Delegate translation to the configured gateway."""
        return self.gateway.translate(request)


__all__ = [
    "TranslationGateway",
    "TranslationGatewayError",
    "TranslationService",
]
