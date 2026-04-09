"""Tests for the CLI entry point."""

from cortex_translate_service import cli
from cortex_translate_service.bootstrap import build_service_from_env
from cortex_translate_service.domain import TranslationRequest, TranslationResult
from cortex_translate_service.service import TranslationGatewayError


class FakeService:
    """Service test double for CLI behavior."""

    def __init__(
        self, *, result: TranslationResult | None = None, error: Exception | None = None
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


def test_run_prints_translation_to_stdout(monkeypatch, capsys) -> None:
    """The CLI prints translated text on success."""
    service = FakeService(
        result=TranslationResult(
            translated_text="안녕하세요",
            connection_name="dev",
            query_tag="test-query-tag",
        )
    )
    monkeypatch.setattr(cli, "build_service_from_env", lambda: service)

    exit_code = cli.run(["--text", "Hello", "--source", "en", "--target", "ko"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out == "안녕하세요\n"
    assert captured.err == ""
    assert service.requests == [
        TranslationRequest(text="Hello", source_language="en", target_language="ko")
    ]


def test_run_prints_gateway_errors_to_stderr(monkeypatch, capsys) -> None:
    """The CLI returns a non-zero exit code for translation errors."""
    service = FakeService(error=TranslationGatewayError("profile missing"))
    monkeypatch.setattr(cli, "build_service_from_env", lambda: service)

    exit_code = cli.run(["--text", "Hello", "--source", "en", "--target", "ko"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == ""
    assert captured.err == "Translation failed: profile missing\n"


def test_build_service_from_env_wraps_the_gateway(monkeypatch) -> None:
    """The CLI service builder wraps the environment-backed gateway."""
    gateway = object()
    monkeypatch.setattr(
        "cortex_translate_service.bootstrap.build_gateway_from_env",
        lambda: gateway,
    )

    service = build_service_from_env()

    assert service.gateway is gateway


def test_run_prints_environment_configuration_errors_to_stderr(
    monkeypatch, capsys
) -> None:
    """Invalid env configuration is surfaced as a controlled CLI failure."""
    monkeypatch.setenv("SNOWFLAKE_STATEMENT_TIMEOUT_SECONDS", "abc")

    exit_code = cli.run(["--text", "Hello", "--target", "ko"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == ""
    assert (
        captured.err
        == "Translation failed: SNOWFLAKE_STATEMENT_TIMEOUT_SECONDS must be an integer\n"
    )


def test_main_delegates_to_run(monkeypatch) -> None:
    """The module-level main function delegates to run."""
    monkeypatch.setattr(cli, "run", lambda: 7)

    assert cli.main() == 7
