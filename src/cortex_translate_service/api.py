"""FastAPI delivery layer for the Snowflake Cortex translation service."""

from collections.abc import Callable

from fastapi import Depends, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict

from cortex_translate_service.cli import build_service_from_env
from cortex_translate_service.domain import (
    TranslationRequest,
    TranslationValidationError,
)
from cortex_translate_service.service import TranslationGatewayError, TranslationService

ServiceFactory = Callable[[], TranslationService]


class TranslationRequestBody(BaseModel):
    """API request model for translation requests."""

    model_config = ConfigDict(extra="forbid")

    text: str
    source_language: str = ""
    target_language: str


class TranslationResponseBody(BaseModel):
    """API response model for successful translations."""

    translated_text: str
    connection_name: str
    query_tag: str


class ErrorResponse(BaseModel):
    """API response model for controlled failures."""

    code: str
    message: str


def build_app(service_factory: ServiceFactory = build_service_from_env) -> FastAPI:
    """Build and configure the FastAPI application."""
    app = FastAPI(
        title="Cortex Translate Service",
        version="0.1.0",
        description=(
            "REST API for translating text with Snowflake Cortex AI_TRANSLATE "
            "using a named Snowflake connection profile."
        ),
    )

    def get_service() -> TranslationService:
        """Provide the translation service dependency."""
        return service_factory()

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
                message=str(exc),
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
            422: {"model": ErrorResponse},
            502: {"model": ErrorResponse},
        },
        tags=["translations"],
        summary="Translate text with Snowflake Cortex",
    )
    def create_translation(
        payload: TranslationRequestBody,
        service: TranslationService = Depends(get_service),
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
            connection_name=result.connection_name,
            query_tag=result.query_tag,
        )

    return app


app = build_app()


__all__ = [
    "ErrorResponse",
    "TranslationRequestBody",
    "TranslationResponseBody",
    "app",
    "build_app",
]
