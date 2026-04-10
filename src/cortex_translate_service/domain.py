"""Domain models for the Snowflake Cortex translation service."""

from dataclasses import dataclass

MAX_TEXT_LENGTH = 5_000


class TranslationValidationError(ValueError):
    """Raised when translation request or result values are invalid."""


@dataclass(frozen=True, slots=True)
class TranslationRequest:
    """Immutable translation request value object."""

    text: str
    source_language: str
    target_language: str

    def __post_init__(self) -> None:
        """Normalize and validate the translation request fields."""
        normalized_text = self.text.strip()
        normalized_source_language = self.source_language.strip()
        normalized_target_language = self.target_language.strip()

        if not normalized_text:
            raise TranslationValidationError("text is required")
        if len(normalized_text) > MAX_TEXT_LENGTH:
            raise TranslationValidationError(
                f"text must be at most {MAX_TEXT_LENGTH} characters"
            )
        if not normalized_target_language:
            raise TranslationValidationError("target_language is required")

        object.__setattr__(self, "text", normalized_text)
        object.__setattr__(self, "source_language", normalized_source_language)
        object.__setattr__(self, "target_language", normalized_target_language)


@dataclass(frozen=True, slots=True)
class TranslationResult:
    """Immutable translation result value object."""

    translated_text: str
    connection_name: str
    query_tag: str

    def __post_init__(self) -> None:
        """Normalize and validate the translation result fields."""
        normalized_translation = self.translated_text.strip()
        normalized_connection_name = self.connection_name.strip()
        normalized_query_tag = self.query_tag.strip()

        if not normalized_translation:
            raise TranslationValidationError("translated_text is required")
        if not normalized_connection_name:
            raise TranslationValidationError("connection_name is required")
        if not normalized_query_tag:
            raise TranslationValidationError("query_tag is required")

        object.__setattr__(self, "translated_text", normalized_translation)
        object.__setattr__(self, "connection_name", normalized_connection_name)
        object.__setattr__(self, "query_tag", normalized_query_tag)


__all__ = [
    "MAX_TEXT_LENGTH",
    "TranslationRequest",
    "TranslationResult",
    "TranslationValidationError",
]
