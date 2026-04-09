"""Public package interface for the Cortex translation service."""

from cortex_translate_service.domain import (
    TranslationRequest,
    TranslationResult,
    TranslationValidationError,
)
from cortex_translate_service.service import (
    TranslationGateway,
    TranslationGatewayError,
    TranslationService,
)

__all__ = [
    "TranslationGateway",
    "TranslationGatewayError",
    "TranslationRequest",
    "TranslationResult",
    "TranslationService",
    "TranslationValidationError",
]
