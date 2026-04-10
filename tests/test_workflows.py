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


def test_workflows_do_not_use_deprecated_checkout_or_setup_uv_pins() -> None:
    """Workflow definitions avoid the previously warned checkout and setup-uv pins."""
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in Path(".github/workflows").glob("*.yml")
    )

    assert "actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5" not in combined
    assert "astral-sh/setup-uv@d0cc045d04ccac9d8b7881df0226f9e82c39688e" not in combined


def test_workflows_do_not_use_deprecated_codeql_v3_pins() -> None:
    """Workflow definitions avoid the previously warned CodeQL v3 action pins."""
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in Path(".github/workflows").glob("*.yml")
    )

    assert (
        "github/codeql-action/init@5c8a8a642e79153f5d047b10ec1cba1d1cc65699"
        not in combined
    )
    assert (
        "github/codeql-action/analyze@5c8a8a642e79153f5d047b10ec1cba1d1cc65699"
        not in combined
    )
    assert (
        "github/codeql-action/upload-sarif@5c8a8a642e79153f5d047b10ec1cba1d1cc65699"
        not in combined
    )


def test_dependency_review_workflow_probes_graph_before_review() -> None:
    """Dependency review only runs when the repository graph probe succeeds."""
    workflow = _read_workflow(".github/workflows/dependency-review.yml")

    assert "permissions:\n  contents: read\n" in workflow
    assert "pull-requests: read" not in workflow
    assert (
        """  dependency-review:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    permissions:
      contents: read
      pull-requests: write
"""
        in workflow
    )
    assert "id: dependency_graph" in workflow
    assert (
        "dependency-graph/compare/${{ github.event.pull_request.base.sha }}...${{ github.event.pull_request.head.sha }}"
        in workflow
    )
    assert workflow.index("id: dependency_graph") < workflow.index(
        "actions/dependency-review-action@"
    )
    assert "if: steps.dependency_graph.outputs.available == 'true'" in workflow
    assert "if: steps.dependency_graph.outputs.available != 'true'" in workflow
    assert (
        "DEPENDENCY_GRAPH_MESSAGE: ${{ steps.dependency_graph.outputs.message }}"
        in workflow
    )
    assert "printf '%s\\n' \"$DEPENDENCY_GRAPH_MESSAGE\"" in workflow
    assert (
        "Dependency review was skipped because the repository dependency graph is unavailable."
        in workflow
    )
