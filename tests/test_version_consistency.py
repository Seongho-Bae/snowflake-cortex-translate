"""Regression tests for package/API/public version consistency."""

from importlib.metadata import version
from pathlib import Path

from fastapi.testclient import TestClient

REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_NAME = "cortex-translate-service"
SEMVER_PLACEHOLDER = "vX.Y.Z"


def test_openapi_version_matches_installed_package_metadata() -> None:
    """The FastAPI contract version matches the installed package metadata."""
    from cortex_translate_service.api import build_app

    client = TestClient(build_app(required_api_key="test-api-key"))

    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert response.json()["info"]["version"] == version(PACKAGE_NAME)


def test_public_release_examples_use_semantic_version_placeholders() -> None:
    """Public docs avoid pinning release commands to a stale historical tag."""
    examples = {
        "site/index.html": SEMVER_PLACEHOLDER,
        "docs/release-publishing.md": SEMVER_PLACEHOLDER,
        "CONTRIBUTING.md": SEMVER_PLACEHOLDER,
    }

    for relative_path, placeholder in examples.items():
        content = (REPO_ROOT / relative_path).read_text(encoding="utf-8")

        assert placeholder in content, relative_path
        assert "v0.1.1" not in content, relative_path


def test_readme_project_layout_uses_generic_test_glob() -> None:
    """The README layout stays current by describing tests with a glob."""
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    assert "test_*.py" in readme
