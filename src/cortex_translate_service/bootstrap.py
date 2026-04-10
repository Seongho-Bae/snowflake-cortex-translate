"""Composition helpers shared by CLI and API delivery layers."""

from cortex_translate_service.service import TranslationService
from cortex_translate_service.snowflake_gateway import build_gateway_from_env


def build_service_from_env() -> TranslationService:
    """Build the application service from environment-backed infrastructure."""
    return TranslationService(build_gateway_from_env())


__all__ = ["build_service_from_env"]
