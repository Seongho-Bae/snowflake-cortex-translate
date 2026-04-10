"""FastAPI delivery layer for the Snowflake Cortex translation service."""

import os
from collections.abc import Callable
from importlib.metadata import PackageNotFoundError, version as package_version
from typing import Protocol

from fastapi import Depends, FastAPI, Security
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, ConfigDict, Field

from cortex_translate_service.bootstrap import build_service_from_env
from cortex_translate_service.domain import (
    MAX_TEXT_LENGTH,
    TranslationRequest,
    TranslationResult,
    TranslationValidationError,
)
from cortex_translate_service.service import TranslationGatewayError


class SupportsTranslate(Protocol):
    """Protocol for any component that can process translation requests."""

    def translate(self, request: TranslationRequest) -> TranslationResult:
        """Translate the request and return a result-like object."""


ServiceFactory = Callable[[], SupportsTranslate]
AUTHORIZATION_ERROR_MESSAGE = "Invalid API key"
API_NOT_CONFIGURED_MESSAGE = "Translation API unavailable"
TRANSLATION_GATEWAY_PUBLIC_MESSAGE = "Translation backend unavailable"
PACKAGE_NAME = "cortex-translate-service"
LOCAL_VERSION_FALLBACK = "0.0.0+local"


def resolve_api_version() -> str:
    """Return package metadata version or a safe local fallback."""
    try:
        return package_version(PACKAGE_NAME)
    except PackageNotFoundError:
        return LOCAL_VERSION_FALLBACK


class TranslationRequestBody(BaseModel):
    """API request model for translation requests."""

    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1, max_length=MAX_TEXT_LENGTH)
    source_language: str = ""
    target_language: str


class TranslationResponseBody(BaseModel):
    """API response model for successful translations."""

    translated_text: str


class ErrorResponse(BaseModel):
    """API response model for controlled failures."""

    code: str
    message: str


class AuthorizationError(RuntimeError):
    """Raised when API authorization requirements are not satisfied."""


class ApiNotConfiguredError(RuntimeError):
    """Raised when the API has not been configured for authenticated use."""


def build_app(
    service_factory: ServiceFactory = build_service_from_env,
    required_api_key: str | None = None,
) -> FastAPI:
    """Build and configure the FastAPI application."""
    configured_api_key = (
        os.getenv("TRANSLATION_API_KEY", "")
        if required_api_key is None
        else required_api_key
    ).strip()

    app = FastAPI(
        title="Cortex Translate Service",
        version=resolve_api_version(),
        description=(
            "REST API for translating text with Snowflake Cortex AI_TRANSLATE "
            "using a named Snowflake connection profile."
        ),
    )
    api_key_header = APIKeyHeader(
        name="x-api-key",
        auto_error=False,
        scheme_name="APIKeyHeader",
    )

    def get_service() -> SupportsTranslate:
        """Provide the translation service dependency."""
        return service_factory()

    def require_api_key(
        x_api_key: str | None = Security(api_key_header),
    ) -> None:
        """Require a configured API key before cost-bearing translation calls."""
        if not configured_api_key:
            raise ApiNotConfiguredError(API_NOT_CONFIGURED_MESSAGE)
        if x_api_key != configured_api_key:
            raise AuthorizationError(AUTHORIZATION_ERROR_MESSAGE)

    @app.exception_handler(RequestValidationError)
    async def handle_request_validation_error(  # type: ignore[override]
        _,
        exc: RequestValidationError,
    ) -> JSONResponse:
        """Return a stable JSON response for request schema failures."""
        return JSONResponse(
            status_code=422,
            content=ErrorResponse(
                code="request_validation_error",
                message="Request validation failed",
            ).model_dump(),
        )

    @app.exception_handler(AuthorizationError)
    async def handle_authorization_error(  # type: ignore[override]
        _,
        exc: AuthorizationError,
    ) -> JSONResponse:
        """Return a stable JSON response for missing or invalid API keys."""
        return JSONResponse(
            status_code=401,
            content=ErrorResponse(
                code="authorization_error",
                message=str(exc),
            ).model_dump(),
        )

    @app.exception_handler(ApiNotConfiguredError)
    async def handle_api_not_configured_error(  # type: ignore[override]
        _,
        exc: ApiNotConfiguredError,
    ) -> JSONResponse:
        """Return a stable JSON response when the API key is not configured."""
        return JSONResponse(
            status_code=503,
            content=ErrorResponse(
                code="api_not_configured",
                message=str(exc),
            ).model_dump(),
        )

    @app.exception_handler(TranslationValidationError)
    async def handle_translation_validation_error(  # type: ignore[override]
        _,
        exc: TranslationValidationError,
    ) -> JSONResponse:
        """Return a stable JSON response for translation validation failures."""
        return JSONResponse(
            status_code=422,
            content=ErrorResponse(
                code="translation_validation_error",
                message=str(exc),
            ).model_dump(),
        )

    @app.exception_handler(TranslationGatewayError)
    async def handle_translation_gateway_error(  # type: ignore[override]
        _,
        exc: TranslationGatewayError,
    ) -> JSONResponse:
        """Return a stable JSON response for gateway/runtime failures."""
        return JSONResponse(
            status_code=502,
            content=ErrorResponse(
                code="translation_gateway_error",
                message=TRANSLATION_GATEWAY_PUBLIC_MESSAGE,
            ).model_dump(),
        )

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        """Report application health."""
        return {"status": "ok"}

    @app.post(
        "/api/v1/translations",
        response_model=TranslationResponseBody,
        responses={
            401: {"model": ErrorResponse},
            422: {"model": ErrorResponse},
            502: {"model": ErrorResponse},
            503: {"model": ErrorResponse},
        },
        tags=["translations"],
        summary="Translate text with Snowflake Cortex",
    )
    def create_translation(
        payload: TranslationRequestBody,
        _: None = Depends(require_api_key),
        service: SupportsTranslate = Depends(get_service),
    ) -> TranslationResponseBody:
        """Translate the provided text through Snowflake Cortex."""
        result = service.translate(
            TranslationRequest(
                text=payload.text,
                source_language=payload.source_language,
                target_language=payload.target_language,
            )
        )
        return TranslationResponseBody(
            translated_text=result.translated_text,
        )

    return app


app = build_app()


__all__ = [
    "ErrorResponse",
    "AUTHORIZATION_ERROR_MESSAGE",
    "API_NOT_CONFIGURED_MESSAGE",
    "SupportsTranslate",
    "TranslationRequestBody",
    "TranslationResponseBody",
    "app",
    "build_app",
]
