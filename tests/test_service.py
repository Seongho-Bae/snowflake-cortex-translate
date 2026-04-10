"""Tests for the application service."""

from cortex_translate_service.domain import TranslationRequest, TranslationResult
from cortex_translate_service.service import TranslationGateway, TranslationService


class RecordingGateway(TranslationGateway):
    """Test double that records incoming requests."""

    def __init__(self) -> None:
        """Initialize the recorded request list for service assertions."""
        self.requests: list[TranslationRequest] = []

    def translate(self, request: TranslationRequest) -> TranslationResult:
        """Return a canned translation result."""
        self.requests.append(request)
        return TranslationResult(
            translated_text="안녕하세요",
            connection_name="dev",
            query_tag="test-query-tag",
        )


def test_translation_service_delegates_to_gateway() -> None:
    """The application service passes the request through unchanged."""
    gateway = RecordingGateway()
    service = TranslationService(gateway)
    request = TranslationRequest(
        text="Hello", source_language="en", target_language="ko"
    )

    result = service.translate(request)

    assert gateway.requests == [request]
    assert result.translated_text == "안녕하세요"
    assert result.connection_name == "dev"
    assert result.query_tag == "test-query-tag"
