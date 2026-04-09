"""Tests for the REST API entry point."""

from fastapi.testclient import TestClient

from cortex_translate_service.domain import TranslationRequest, TranslationResult
from cortex_translate_service.service import TranslationGatewayError


class FakeService:
    """Service test double for API behavior."""

    def __init__(
        self,
        *,
        result: TranslationResult | None = None,
        error: Exception | None = None,
    ) -> None:
        self.result = result
        self.error = error
        self.requests: list[TranslationRequest] = []

    def translate(self, request: TranslationRequest) -> TranslationResult:
        """Return the configured result or raise the configured error."""
        self.requests.append(request)
        if self.error is not None:
            raise self.error
        assert self.result is not None
        return self.result


def test_healthz_returns_ok() -> None:
    """The API exposes a simple health check endpoint."""
    from cortex_translate_service.api import build_app

    client = TestClient(build_app(service_factory=lambda: FakeService()))

    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_translation_returns_translation_payload() -> None:
    """The translation endpoint returns structured JSON on success."""
    from cortex_translate_service.api import build_app

    service = FakeService(
        result=TranslationResult(
            translated_text="안녕하세요",
            connection_name="dev",
            query_tag="api-test-query-tag",
        )
    )
    client = TestClient(build_app(service_factory=lambda: service))

    response = client.post(
        "/api/v1/translations",
        json={
            "text": "Hello",
            "source_language": "en",
            "target_language": "ko",
        },
    )

    assert response.status_code == 200
    assert response.json() == {"translated_text": "안녕하세요"}
    assert service.requests == [
        TranslationRequest(text="Hello", source_language="en", target_language="ko")
    ]


def test_create_translation_returns_request_validation_error() -> None:
    """Missing required request fields return a structured 422 response."""
    from cortex_translate_service.api import build_app

    client = TestClient(build_app(service_factory=lambda: FakeService()))

    response = client.post(
        "/api/v1/translations",
        json={
            "text": "Hello",
            "source_language": "en",
        },
    )

    assert response.status_code == 422
    assert response.json()["code"] == "request_validation_error"
    assert response.json()["message"] == "Request validation failed"


def test_create_translation_returns_domain_validation_error() -> None:
    """Whitespace-only text is rejected with a controlled validation response."""
    from cortex_translate_service.api import build_app

    client = TestClient(build_app(service_factory=lambda: FakeService()))

    response = client.post(
        "/api/v1/translations",
        json={
            "text": "   ",
            "source_language": "en",
            "target_language": "ko",
        },
    )

    assert response.status_code == 422
    assert response.json() == {
        "code": "translation_validation_error",
        "message": "text is required",
    }


def test_create_translation_returns_gateway_error() -> None:
    """Snowflake gateway failures are mapped to a 502 JSON response."""
    from cortex_translate_service.api import build_app

    service = FakeService(error=TranslationGatewayError("profile missing"))
    client = TestClient(build_app(service_factory=lambda: service))

    response = client.post(
        "/api/v1/translations",
        json={
            "text": "Hello",
            "source_language": "en",
            "target_language": "ko",
        },
    )

    assert response.status_code == 502
    assert response.json() == {
        "code": "translation_gateway_error",
        "message": "profile missing",
    }


def test_openapi_exposes_translation_endpoint() -> None:
    """The generated OpenAPI document includes the translation route."""
    from cortex_translate_service.api import build_app

    client = TestClient(build_app(service_factory=lambda: FakeService()))

    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert "/api/v1/translations" in response.json()["paths"]
