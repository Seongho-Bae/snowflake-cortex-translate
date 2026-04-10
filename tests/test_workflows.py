"""Regression tests for GitHub workflow definitions."""

from pathlib import Path


def test_pages_workflow_writes_product_facing_fallback_after_early_exit() -> None:
    """The Pages fallback script exits early and keeps fallback copy service-facing."""
    workflow = Path(".github/workflows/pages.yml").read_text(encoding="utf-8")

    assert (
        """run: |
          if [ -d site ]; then
            exit 0
          fi

          mkdir -p site
          cat > site/index.html <<'EOF'
"""
        in workflow
    )
    assert "번역 서비스의 핵심" in workflow
    assert "매뉴얼" not in workflow
