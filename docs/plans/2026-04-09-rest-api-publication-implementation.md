<!-- markdownlint-disable MD013 MD022 MD032 -->

# Snowflake Cortex Translation REST API Publication Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add RESTful API support and publish this project as a protected public GitHub repository with GHCR releases, OSSF Scorecard automation, and a Korean GitHub Pages manual.

**Architecture:** Keep the current domain/service/gateway layers intact, add a thin FastAPI delivery layer for REST access, then wrap the project with container, documentation, and GitHub governance automation. Use Git Flow with protected `main` and `develop` branches, plus GitHub Actions for CI, Pages, Scorecard, CodeQL, and GHCR release.

**Tech Stack:** Python 3.12+, uv, FastAPI, Uvicorn, pytest, httpx/TestClient, Docker, GitHub Actions, GitHub Pages, GHCR

---

### Task 1: Add failing API tests and dependency expectations

**Files:**
- Modify: `tests/test_cli.py`
- Create: `tests/test_api.py`
- Modify: `pyproject.toml`

**Step 1: Write the failing test**

Define REST API expectations for:
- `GET /healthz`
- `POST /api/v1/translations` success
- validation failures for missing/blank inputs
- gateway/runtime error mapping
- OpenAPI availability

**Step 2: Run tests to verify RED**

Run: `uv run pytest tests/test_api.py -v`
Expected: FAIL because the API module/app does not exist yet.

**Step 3: Add minimal dependency declarations**

Add FastAPI/Uvicorn runtime support and test-time HTTP client support.

**Step 4: Re-run the API tests**

Run: `uv run pytest tests/test_api.py -v`
Expected: FAIL for missing implementation rather than missing test tooling.

### Task 2: Implement the FastAPI REST layer

**Files:**
- Create: `src/cortex_translate_service/api.py`
- Modify: `src/cortex_translate_service/__init__.py`
- Modify: `README.md`
- Modify: `ARCHITECTURE.md`
- Test: `tests/test_api.py`

**Step 1: Run targeted tests to verify RED**

Run: `uv run pytest tests/test_api.py -v`
Expected: FAIL because the FastAPI app and routes are missing.

**Step 2: Write minimal implementation**

Implement:
- app factory / default app
- `GET /healthz`
- `POST /api/v1/translations`
- structured JSON error responses
- OpenAPI metadata for the translation endpoint

**Step 3: Run targeted tests to verify GREEN**

Run: `uv run pytest tests/test_api.py -v`
Expected: PASS.

### Task 3: Add container and local runtime support

**Files:**
- Create: `Dockerfile`
- Create: `.dockerignore`
- Modify: `README.md`
- Modify: `ARCHITECTURE.md`

**Step 1: Define the runtime contract**

Document container environment expectations and the default API server command.

**Step 2: Build a minimal runtime image**

Create a container image that installs the app with `uv`, exposes the API server, and preserves Snowflake env-based configuration.

**Step 3: Verify the container build**

Run: `docker build -t cortex-translate-service:local .`
Expected: PASS.

### Task 4: Add public repository governance and release automation

**Files:**
- Create: `LICENSE`
- Create: `SECURITY.md`
- Create: `CONTRIBUTING.md`
- Create: `CODEOWNERS`
- Create: `CHANGELOG.md`
- Create: `.github/pull_request_template.md`
- Create: `.github/dependabot.yml`
- Create: `.github/workflows/ci.yml`
- Create: `.github/workflows/codeql.yml`
- Create: `.github/workflows/dependency-review.yml`
- Create: `.github/workflows/scorecard.yml`
- Create: `.github/workflows/pages.yml`
- Create: `.github/workflows/release.yml`

**Step 1: Write the workflow and governance files**

Define CI, security, release, and documentation automation appropriate for a public repository.

**Step 2: Verify workflow syntax and file coverage**

Run: `python3 scripts/prompt_checks/validate_agent_packs.py --root .` only if present, otherwise run file-based linting and YAML validation via repository-safe tooling.
Expected: PASS or documented absence of prompt-check scripts.

### Task 5: Add a Korean GitHub Pages manual

**Files:**
- Create: `site/index.html`
- Create: `site/styles.css`
- Create: `site/app.js`
- Modify: `README.md`

**Step 1: Write the manual content**

Publish a Korean web manual covering setup, CLI usage, REST API usage, Docker, release flow, and contribution guidance.

**Step 2: Verify the manual locally**

Serve the site locally and verify major flows with Playwright plus screenshot evidence.

### Task 6: Final verification and publication

**Files:**
- Verify: `src/cortex_translate_service/**`
- Verify: `tests/**`
- Verify: `.github/**`
- Verify: `site/**`
- Verify: `README.md`

**Step 1: Run the full automated suite**

Run: `uv run pytest --cov=src/cortex_translate_service --cov-report=term-missing`
Expected: PASS with 100% coverage.

**Step 2: Run lint/type verification**

Run: `uv run mypy src tests`
Expected: PASS.

**Step 3: Verify local API smoke**

Run the app locally and confirm `GET /healthz` plus one translation request path through tests or local smoke tooling.

**Step 4: Publish and protect the repository**

Create the public GitHub repository, push `main`/`develop`, configure protection rules, open the PR from feature branch to `develop`, and gather PR continuity evidence.

**Step 5: Release the image and docs**

Tag the release, trigger the GHCR workflow, confirm image digests for `linux/amd64` and `linux/arm64`, and verify the GitHub Pages deployment URL.
