"""Regression tests for public-facing documentation copy."""

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
PUBLIC_COPY_RULES = {
    "site/index.html": (
        "매뉴얼",
        "Manual",
        "안내서",
        "GitHub Pages",
        "이 페이지에서는",
        "README.md",
        "CONTRIBUTING.md",
        "ARCHITECTURE.md",
        "docs/release-publishing.md",
    ),
    "README.md": ("매뉴얼", "Manual", "안내서"),
    "ARCHITECTURE.md": ("매뉴얼", "Manual", "안내서"),
}


@pytest.mark.parametrize(
    ("relative_path", "term"),
    [
        (relative_path, term)
        for relative_path, terms in PUBLIC_COPY_RULES.items()
        for term in terms
    ],
    ids=lambda case: "-".join(str(part) for part in case),
)
def test_public_facing_copy_avoids_manual_framing(
    relative_path: str, term: str
) -> None:
    """Public-facing docs avoid manual-style wording banned by the user."""
    content = (REPO_ROOT / relative_path).read_text(encoding="utf-8")

    assert term not in content
