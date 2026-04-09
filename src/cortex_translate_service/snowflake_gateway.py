"""Snowflake connector adapter for Cortex translation."""

import json
import os
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

import snowflake.connector

from cortex_translate_service.domain import TranslationRequest, TranslationResult
from cortex_translate_service.service import TranslationGatewayError

TRANSLATION_QUERY = """
SELECT AI_TRANSLATE(
    %(text)s,
    %(source_language)s,
    %(target_language)s,
    TRUE
) AS translation_payload
"""

ConnectFunction = Callable[..., Any]


@dataclass(slots=True)
class SnowflakeTranslationGateway:
    """Translate text through Snowflake Cortex using a named connection."""

    connection_name: str = "dev"
    query_tag: str = "cortex-translate-service"
    statement_timeout_seconds: int = 60
    login_timeout: int = 30
    network_timeout: int = 120
    connect_function: ConnectFunction = field(
        default=snowflake.connector.connect, repr=False
    )

    def translate(self, request: TranslationRequest) -> TranslationResult:
        """Execute a Snowflake Cortex translation query for the provided request."""
        try:
            with self.connect_function(
                connection_name=self.connection_name,
                login_timeout=self.login_timeout,
                network_timeout=self.network_timeout,
                session_parameters={
                    "QUERY_TAG": self.query_tag,
                    "STATEMENT_TIMEOUT_IN_SECONDS": self.statement_timeout_seconds,
                },
            ) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        TRANSLATION_QUERY,
                        {
                            "text": request.text,
                            "source_language": request.source_language,
                            "target_language": request.target_language,
                        },
                    )
                    row = cursor.fetchone()
        except TranslationGatewayError:
            raise
        except Exception as exc:  # pragma: no cover - exercised in CLI error path.
            raise TranslationGatewayError(
                f"Snowflake translation request failed: {exc}"
            ) from exc

        return self._build_result(row)

    def _build_result(self, row: tuple[Any, ...] | None) -> TranslationResult:
        """Convert a Snowflake row into a translation result value object."""
        if row is None:
            raise TranslationGatewayError("Snowflake did not return a translation row")

        payload = self._normalize_payload(row[0])
        if isinstance(payload, dict):
            error = payload.get("error")
            if error:
                raise TranslationGatewayError(str(error))
            value = payload.get("value")
        else:
            value = payload

        if value is None:
            raise TranslationGatewayError("Snowflake returned an empty translation")

        return TranslationResult(
            translated_text=str(value),
            connection_name=self.connection_name,
            query_tag=self.query_tag,
        )

    def _normalize_payload(self, payload: Any) -> Any:
        """Normalize Snowflake payloads before result extraction."""
        if not isinstance(payload, str):
            return payload

        try:
            return json.loads(payload)
        except json.JSONDecodeError:
            return payload


def build_gateway_from_env(
    connect_function: ConnectFunction | None = None,
) -> SnowflakeTranslationGateway:
    """Build a Snowflake translation gateway from environment variables."""
    timeout_value = os.getenv("SNOWFLAKE_STATEMENT_TIMEOUT_SECONDS", "60")

    try:
        statement_timeout_seconds = int(timeout_value)
    except ValueError as exc:
        raise TranslationGatewayError(
            "SNOWFLAKE_STATEMENT_TIMEOUT_SECONDS must be an integer"
        ) from exc

    return SnowflakeTranslationGateway(
        connection_name=os.getenv("SNOWFLAKE_CONNECTION_NAME", "dev"),
        query_tag=os.getenv("SNOWFLAKE_QUERY_TAG", "cortex-translate-service"),
        statement_timeout_seconds=statement_timeout_seconds,
        connect_function=connect_function or snowflake.connector.connect,
    )


__all__ = ["SnowflakeTranslationGateway", "build_gateway_from_env"]
