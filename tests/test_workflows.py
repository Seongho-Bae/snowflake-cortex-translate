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
        "  scorecard:\n    runs-on: ubuntu-latest\n    timeout-minutes: 20\n"
        in workflow
    )
    assert "scorecard-step-outcome: ${{ steps.scorecard.outcome }}" in workflow
    assert "sarif-artifact-outcome: ${{ steps.scorecard_artifact.outcome }}" in workflow
    assert (
        """    permissions:
      contents: read
      actions: read
      security-events: write
      id-token: write
"""
        in workflow
    )
    assert "id: scorecard\n        continue-on-error: true\n" in workflow
    assert "if: always() && hashFiles('results.sarif') != ''\n" in workflow
    assert (
        "actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a" in workflow
    )
    assert "GITHUB_STEP_SUMMARY" in workflow


def test_scorecard_workflow_keeps_publishable_job_separate_from_reporting() -> None:
    """The Scorecard publish job keeps API-safe steps isolated from shell reporting."""
    workflow = _read_workflow(".github/workflows/scorecard.yml")
    scorecard_job = workflow.split("  scorecard:\n", maxsplit=1)[1].split(
        "\n  scorecard-report:\n", maxsplit=1
    )[0]

    assert "scorecard-step-outcome: ${{ steps.scorecard.outcome }}" in scorecard_job
    assert (
        "sarif-artifact-outcome: ${{ steps.scorecard_artifact.outcome }}"
        in scorecard_job
    )
    assert "publish_results: true" in scorecard_job
    assert (
        "actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a"
        in scorecard_job
    )
    assert "id: scorecard_artifact" in scorecard_job
    assert "run:" not in scorecard_job

    report_job = workflow.split("\n  scorecard-report:\n", maxsplit=1)[1]
    assert "needs: scorecard" in report_job
    assert "run: |" in report_job


def test_readme_exposes_scorecard_badge_and_viewer_link() -> None:
    """The README surfaces the public Scorecard badge and viewer URL."""
    readme = Path("README.md").read_text(encoding="utf-8")

    assert (
        "[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/"
        "Seongho-Bae/snowflake-cortex-translate/badge)]"
        "(https://scorecard.dev/viewer/?uri=github.com/"
        "Seongho-Bae/snowflake-cortex-translate)"
    ) in readme


def test_release_notes_document_scorecard_api_and_viewer_urls() -> None:
    """The release notes document the live Scorecard API and viewer endpoints."""
    release_notes = Path("docs/release-publishing.md").read_text(encoding="utf-8")

    assert (
        "https://api.scorecard.dev/projects/github.com/Seongho-Bae/"
        "snowflake-cortex-translate"
    ) in release_notes
    assert (
        "https://scorecard.dev/viewer/?uri=github.com/Seongho-Bae/"
        "snowflake-cortex-translate"
    ) in release_notes


def test_dockerfile_pins_runtime_base_image_by_digest() -> None:
    """The runtime Docker base image stays pinned by digest for Scorecard."""
    dockerfile = Path("Dockerfile").read_text(encoding="utf-8")

    assert (
        "FROM python:3.12-slim-bookworm@sha256:"
        "d97792894a6a4162cae14da44542a83c75e56c77a27b92d58f3f83b7bc961292 AS runtime"
    ) in dockerfile


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
