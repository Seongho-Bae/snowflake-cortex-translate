<!-- markdownlint-disable MD001 MD013 MD022 MD032 MD036 -->

# Snowflake Cortex Translation Service Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a local Python service that uses a Snowflake `dev` profile and Snowflake Cortex `AI_TRANSLATE` to translate text safely.

**Architecture:** Use a small DDD-style Python package with immutable request/result value objects, an application service, and a Snowflake connector gateway. Expose the flow through a CLI and support it with SQL setup/verification files plus usage documentation.

**Tech Stack:** Python 3.12, uv, pytest, snowflake-connector-python, argparse, SQL

---

### Task 1: Scaffold project and write failing tests

**Files:**
- Create: `pyproject.toml`
- Create: `.gitignore`
- Create: `tests/test_domain.py`
- Create: `tests/test_service.py`
- Create: `tests/test_snowflake_gateway.py`
- Create: `tests/test_cli.py`

**Step 1: Write the failing tests**

Create tests that define:
- request validation and normalization,
- service delegation to a translation gateway,
- Snowflake gateway query execution and error handling,
- CLI success and failure output.

**Step 2: Run test to verify it fails**

Run: `uv run pytest`
Expected: FAIL because `cortex_translate_service` modules do not exist yet.

**Step 3: Write minimal implementation support files**

Add `pyproject.toml` with runtime dependency `snowflake-connector-python` and dev dependencies for `pytest` and `pytest-cov`. Add `.gitignore` entries for `.venv`, `.snowflake`, caches, and coverage artifacts.

**Step 4: Run test to verify failure is still about missing production modules**

Run: `uv run pytest`
Expected: FAIL with import errors for missing package modules.

### Task 2: Implement domain and application service

**Files:**
- Create: `src/cortex_translate_service/__init__.py`
- Create: `src/cortex_translate_service/domain.py`
- Create: `src/cortex_translate_service/service.py`
- Test: `tests/test_domain.py`
- Test: `tests/test_service.py`

**Step 1: Write the failing test**

Use the tests from Task 1 to drive domain behavior first.

**Step 2: Run targeted tests to verify RED**

Run: `uv run pytest tests/test_domain.py tests/test_service.py -v`
Expected: FAIL for missing classes/functions.

**Step 3: Write minimal implementation**

Implement immutable request/result value objects, protocol/ABC for a translation gateway, and a `TranslationService.translate()` method.

**Step 4: Run targeted tests to verify GREEN**

Run: `uv run pytest tests/test_domain.py tests/test_service.py -v`
Expected: PASS.

### Task 3: Implement Snowflake gateway and CLI

**Files:**
- Create: `src/cortex_translate_service/snowflake_gateway.py`
- Create: `src/cortex_translate_service/cli.py`
- Test: `tests/test_snowflake_gateway.py`
- Test: `tests/test_cli.py`

**Step 1: Run targeted tests to verify RED**

Run: `uv run pytest tests/test_snowflake_gateway.py tests/test_cli.py -v`
Expected: FAIL for missing gateway and CLI implementations.

**Step 2: Write minimal implementation**

Implement the Snowflake adapter with parameterized `AI_TRANSLATE(..., TRUE)` SQL, `connection_name` support, session parameters, timeout handling, and error wrapping. Add a CLI that builds the gateway from env, runs the service, prints the translated text, and exits non-zero on failure.

**Step 3: Run targeted tests to verify GREEN**

Run: `uv run pytest tests/test_snowflake_gateway.py tests/test_cli.py -v`
Expected: PASS.

### Task 4: Add operational docs and SQL artifacts

**Files:**
- Create: `README.md`
- Create: `.env.example`
- Create: `config/connections.toml.example`
- Create: `sql/setup.sql`
- Create: `sql/verify.sql`

**Step 1: Write the documentation/spec artifacts**

Document how to activate the `dev` profile with `SNOWFLAKE_HOME` and `SNOWFLAKE_DEFAULT_CONNECTION_NAME`, how to run the CLI, what grants are required, and how to verify the Cortex translation path in SQL.

**Step 2: Verify docs align with implementation**

Run: `uv run python -m cortex_translate_service.cli --help`
Expected: CLI help matches the documented interface.

### Task 5: Full verification

**Files:**
- Verify: `src/cortex_translate_service/**`
- Verify: `tests/**`
- Verify: `README.md`
- Verify: `sql/**`

**Step 1: Run the full automated suite**

Run: `uv run pytest --cov=src/cortex_translate_service --cov-report=term-missing`
Expected: PASS with 100% coverage.

**Step 2: Run a local CLI smoke without Snowflake credentials**

Run: `uv run python -m cortex_translate_service.cli --text "Hello" --source en --target ko`
Expected: controlled failure if no dev profile exists, without leaking secrets.

**Step 3: Record live verification command for real credentials**

Run when credentials exist: `SNOWFLAKE_HOME="$PWD/.snowflake" SNOWFLAKE_DEFAULT_CONNECTION_NAME=dev uv run python -m cortex_translate_service.cli --text "Hello" --source en --target ko`
Expected: translated output from Snowflake Cortex.
