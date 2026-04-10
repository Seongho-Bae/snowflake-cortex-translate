"""Tests for translation domain value objects."""

import pytest

from cortex_translate_service.domain import (
    MAX_TEXT_LENGTH,
    TranslationRequest,
    TranslationResult,
    TranslationValidationError,
)


def test_translation_request_strips_whitespace() -> None:
    """Translation requests normalize whitespace around fields."""
    request = TranslationRequest(
        text="  Hello world  ",
        source_language=" en ",
        target_language=" ko ",
    )

    assert request.text == "Hello world"
    assert request.source_language == "en"
    assert request.target_language == "ko"


def test_translation_request_allows_auto_detect_source_language() -> None:
    """Translation requests preserve the empty-string auto-detect mode."""
    request = TranslationRequest(
        text="Hola",
        source_language="  ",
        target_language="en",
    )

    assert request.source_language == ""


def test_translation_request_rejects_blank_text() -> None:
    """Translation requests require source text."""
    with pytest.raises(TranslationValidationError, match="text is required"):
        TranslationRequest(text="   ", source_language="en", target_language="ko")


def test_translation_request_rejects_text_over_max_length() -> None:
    """Translation requests reject text that exceeds the cost-control limit."""
    with pytest.raises(
        TranslationValidationError,
        match=f"text must be at most {MAX_TEXT_LENGTH} characters",
    ):
        TranslationRequest(
            text="a" * (MAX_TEXT_LENGTH + 1),
            source_language="en",
            target_language="ko",
        )


def test_translation_result_rejects_blank_translated_text() -> None:
    """Translation results require translated content."""
    with pytest.raises(TranslationValidationError, match="translated_text is required"):
        TranslationResult(translated_text="   ", connection_name="dev", query_tag="tag")


def test_translation_request_rejects_blank_target_language() -> None:
    """Translation requests require a target language."""
    with pytest.raises(TranslationValidationError, match="target_language is required"):
        TranslationRequest(text="Hello", source_language="en", target_language="   ")


def test_translation_result_rejects_blank_connection_name() -> None:
    """Translation results require the named Snowflake connection."""
    with pytest.raises(TranslationValidationError, match="connection_name is required"):
        TranslationResult(
            translated_text="안녕하세요", connection_name="   ", query_tag="tag"
        )


def test_translation_result_rejects_blank_query_tag() -> None:
    """Translation results require a query tag for observability."""
    with pytest.raises(TranslationValidationError, match="query_tag is required"):
        TranslationResult(
            translated_text="안녕하세요",
            connection_name="dev",
            query_tag="   ",
        )
