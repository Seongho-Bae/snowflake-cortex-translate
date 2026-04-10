"""CLI entry point for the Snowflake Cortex translation service."""

import argparse
import sys
from collections.abc import Sequence

from cortex_translate_service.bootstrap import build_service_from_env
from cortex_translate_service.domain import (
    TranslationRequest,
    TranslationValidationError,
)
from cortex_translate_service.service import TranslationGatewayError


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="Translate text with Snowflake Cortex AI using a named profile.",
    )
    parser.add_argument("--text", required=True, help="Text to translate.")
    parser.add_argument(
        "--source",
        default="",
        help="Source language code. Leave empty to auto-detect.",
    )
    parser.add_argument("--target", required=True, help="Target language code.")
    return parser


def run(argv: Sequence[str] | None = None) -> int:
    """Run the CLI command and return a process exit code."""
    args = build_parser().parse_args(argv)

    try:
        service = build_service_from_env()
        result = service.translate(
            TranslationRequest(
                text=args.text,
                source_language=args.source,
                target_language=args.target,
            )
        )
    except (TranslationValidationError, TranslationGatewayError) as exc:
        print(f"Translation failed: {exc}", file=sys.stderr)
        return 1

    print(result.translated_text)
    return 0


def main() -> int:
    """Run the CLI using process arguments."""
    return run()


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
