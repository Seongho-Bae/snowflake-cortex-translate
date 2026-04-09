"""Tests for the Snowflake Cortex gateway."""

import pytest

from cortex_translate_service.domain import TranslationRequest
from cortex_translate_service.snowflake_gateway import (
    SnowflakeTranslationGateway,
    build_gateway_from_env,
)
from cortex_translate_service.service import TranslationGatewayError


class FakeCursor:
    """Cursor test double for Snowflake query execution."""

    def __init__(self, row: tuple[object, ...] | None) -> None:
        self.row = row
        self.calls: list[tuple[str, dict[str, str]]] = []

    def __enter__(self) -> "FakeCursor":
        """Enter the cursor context."""
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        """Exit the cursor context."""
        return None

    def execute(self, query: str, params: dict[str, str]) -> "FakeCursor":
        """Record the executed query and parameters."""
        self.calls.append((query, params))
        return self

    def fetchone(self) -> tuple[object, ...] | None:
        """Return the preconfigured row."""
        return self.row


class FakeConnection:
    """Connection test double for Snowflake connector usage."""

    def __init__(self, cursor: FakeCursor) -> None:
        self._cursor = cursor

    def __enter__(self) -> "FakeConnection":
        """Enter the connection context."""
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        """Exit the connection context."""
        return None

    def cursor(self) -> FakeCursor:
        """Return the configured fake cursor."""
        return self._cursor


def test_snowflake_gateway_executes_ai_translate_query() -> None:
    """The Snowflake gateway uses a named connection and parameterized SQL."""
    request = TranslationRequest(
        text="Hello", source_language="en", target_language="ko"
    )
    cursor = FakeCursor(({"value": "안녕하세요", "error": None},))
    captured: dict[str, object] = {}

    def connect(**kwargs):
        captured.update(kwargs)
        return FakeConnection(cursor)

    gateway = SnowflakeTranslationGateway(connect_function=connect)

    result = gateway.translate(request)

    assert result.translated_text == "안녕하세요"
    assert result.connection_name == "dev"
    assert result.query_tag == "cortex-translate-service"
    assert captured["connection_name"] == "dev"
    assert captured["login_timeout"] == 30
    assert captured["network_timeout"] == 120
    assert captured["session_parameters"] == {
        "QUERY_TAG": "cortex-translate-service",
        "STATEMENT_TIMEOUT_IN_SECONDS": 60,
    }
    query, params = cursor.calls[0]
    assert "AI_TRANSLATE" in query
    assert params == {
        "text": "Hello",
        "source_language": "en",
        "target_language": "ko",
    }


def test_snowflake_gateway_raises_for_cortex_error_payload() -> None:
    """The gateway surfaces Cortex-side errors cleanly."""
    request = TranslationRequest(
        text="Hello", source_language="en", target_language="ko"
    )

    gateway = SnowflakeTranslationGateway(
        connect_function=lambda **_: FakeConnection(
            FakeCursor(({"value": None, "error": "unsupported language"},))
        )
    )

    with pytest.raises(TranslationGatewayError, match="unsupported language"):
        gateway.translate(request)


def test_snowflake_gateway_re_raises_gateway_errors() -> None:
    """Gateway-specific errors are not wrapped a second time."""
    request = TranslationRequest(
        text="Hello", source_language="en", target_language="ko"
    )
    gateway = SnowflakeTranslationGateway(
        connect_function=lambda **_: (_ for _ in ()).throw(
            TranslationGatewayError("configured failure")
        )
    )

    with pytest.raises(TranslationGatewayError, match="configured failure"):
        gateway.translate(request)


def test_snowflake_gateway_raises_when_no_row_is_returned() -> None:
    """A missing Snowflake row is treated as an error."""
    request = TranslationRequest(
        text="Hello", source_language="en", target_language="ko"
    )
    gateway = SnowflakeTranslationGateway(
        connect_function=lambda **_: FakeConnection(FakeCursor(None))
    )

    with pytest.raises(
        TranslationGatewayError, match="did not return a translation row"
    ):
        gateway.translate(request)


def test_snowflake_gateway_supports_scalar_translation_payloads() -> None:
    """Scalar Snowflake payloads are converted directly to translation results."""
    request = TranslationRequest(
        text="Hello", source_language="en", target_language="fr"
    )
    gateway = SnowflakeTranslationGateway(
        connection_name="analytics-dev",
        query_tag="scalar-payload",
        connect_function=lambda **_: FakeConnection(FakeCursor(("bonjour",))),
    )

    result = gateway.translate(request)

    assert result.translated_text == "bonjour"
    assert result.connection_name == "analytics-dev"
    assert result.query_tag == "scalar-payload"


def test_snowflake_gateway_parses_json_object_string_payloads() -> None:
    """Stringified Snowflake OBJECT payloads are parsed before extraction."""
    request = TranslationRequest(
        text="Hello", source_language="en", target_language="ko"
    )
    gateway = SnowflakeTranslationGateway(
        connect_function=lambda **_: FakeConnection(
            FakeCursor(('{\n  "value": "안녕하세요",\n  "error": null\n}',))
        )
    )

    result = gateway.translate(request)

    assert result.translated_text == "안녕하세요"


def test_snowflake_gateway_raises_for_empty_translation_payload() -> None:
    """A translation payload without a value is rejected."""
    request = TranslationRequest(
        text="Hello", source_language="en", target_language="ko"
    )
    gateway = SnowflakeTranslationGateway(
        connect_function=lambda **_: FakeConnection(
            FakeCursor(({"value": None, "error": None},))
        )
    )

    with pytest.raises(TranslationGatewayError, match="empty translation"):
        gateway.translate(request)


def test_build_gateway_from_env_reads_overrides(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Environment variables customize the gateway defaults."""
    monkeypatch.setenv("SNOWFLAKE_CONNECTION_NAME", "qa")
    monkeypatch.setenv("SNOWFLAKE_QUERY_TAG", "custom-query-tag")
    monkeypatch.setenv("SNOWFLAKE_STATEMENT_TIMEOUT_SECONDS", "90")

    gateway = build_gateway_from_env(connect_function=lambda **_: None)

    assert gateway.connection_name == "qa"
    assert gateway.query_tag == "custom-query-tag"
    assert gateway.statement_timeout_seconds == 90


def test_build_gateway_from_env_rejects_invalid_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Invalid timeout configuration raises a gateway error."""
    monkeypatch.setenv("SNOWFLAKE_STATEMENT_TIMEOUT_SECONDS", "abc")

    with pytest.raises(
        TranslationGatewayError,
        match="SNOWFLAKE_STATEMENT_TIMEOUT_SECONDS must be an integer",
    ):
        build_gateway_from_env(connect_function=lambda **_: None)
