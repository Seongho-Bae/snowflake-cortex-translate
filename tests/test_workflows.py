"""Regression tests for GitHub workflow definitions."""

from pathlib import Path


def _read_workflow(relative_path: str) -> str:
    """Read a GitHub workflow YAML file as UTF-8 text."""
    return Path(relative_path).read_text(encoding="utf-8")


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


def test_codeql_workflow_limits_global_permissions_to_read_only() -> None:
    """The CodeQL workflow keeps write permissions scoped to the analyze job."""
    workflow = _read_workflow(".github/workflows/codeql.yml")

    assert "permissions:\n  contents: read\n  actions: read\n" in workflow
    assert (
        """  analyze:
    name: codeql-python
    runs-on: ubuntu-latest
    timeout-minutes: 30
    permissions:
      contents: read
      actions: read
      security-events: write
"""
        in workflow
    )


def test_scorecard_workflow_limits_global_permissions_to_read_only() -> None:
    """The Scorecard workflow scopes write permissions to the scorecard job."""
    workflow = _read_workflow(".github/workflows/scorecard.yml")

    assert "permissions:\n  contents: read\n  actions: read\n" in workflow
    assert (
        """  scorecard:
    runs-on: ubuntu-latest
    timeout-minutes: 20
    permissions:
      contents: read
      actions: read
      security-events: write
      id-token: write
"""
        in workflow
    )
    assert "id: scorecard\n        continue-on-error: true\n" in workflow
    assert "if: always() && hashFiles('results.sarif') != ''\n" in workflow
    assert "if: always() && hashFiles('results.sarif') == ''\n" in workflow
    assert "GITHUB_STEP_SUMMARY" in workflow


def test_security_policy_links_private_reporting_channel() -> None:
    """The security policy links a concrete private reporting channel."""
    security_policy = Path("SECURITY.md").read_text(encoding="utf-8")

    assert (
        "https://github.com/Seongho-Bae/snowflake-cortex-translate/security/advisories/new"
        in security_policy
    )
