# Cortex Translate Service

Local Python translation service and REST API that use a Snowflake `dev`
profile and Snowflake Cortex `AI_TRANSLATE`.

한국어 GitHub Pages 소스는 [`site/index.html`](site/index.html)에서 바로 확인할 수 있으며,
배포된 페이지도 같은 정적 자산을 사용합니다.

## What this project does

- activates a named Snowflake connection profile (default: `dev`)
- sends translation requests to Snowflake Cortex `AI_TRANSLATE`
- exposes the flow through both a CLI and a RESTful API
- documents the grants and SQL verification needed for live Snowflake use

## Project layout

```text
.
├── .github/workflows/
├── ARCHITECTURE.md
├── CHANGELOG.md
├── README.md
├── config/
│   └── connections.toml.example
├── docs/
│   ├── plans/
│   └── release-publishing.md
├── pyproject.toml
├── site/
│   ├── favicon.ico
│   ├── favicon.svg
│   ├── index.html
│   └── styles.css
├── sql/
│   ├── setup.sql
│   └── verify.sql
├── src/cortex_translate_service/
│   ├── __init__.py
│   ├── api.py
│   ├── bootstrap.py
│   ├── cli.py
│   ├── domain.py
│   ├── service.py
│   └── snowflake_gateway.py
└── tests/
    └── test_*.py
```

## Prerequisites

- Python 3.12+
- `uv`
- a Snowflake role with `SNOWFLAKE.CORTEX_USER`
- a reachable Snowflake warehouse, database, and schema

## Activate the Snowflake dev profile

1. Copy the example connection profile:

   ```bash
   mkdir -p .snowflake
   cp config/connections.toml.example .snowflake/connections.toml
   ```

2. Update the placeholder values in `.snowflake/connections.toml`.

3. Export the local Snowflake profile environment:

   ```bash
   export SNOWFLAKE_HOME="$PWD/.snowflake"
   export SNOWFLAKE_DEFAULT_CONNECTION_NAME=dev
   export SNOWFLAKE_CONNECTION_NAME=dev
   ```

`externalbrowser` is the safest default for local development because it
avoids storing a password in the repository.

## Install dependencies

```bash
uv sync --dev
```

## Run the translation service

Translate a sentence from English to Korean:

```bash
uv run cortex-translate --text "Hello world" --source en --target ko
```

Auto-detect the source language:

```bash
uv run cortex-translate --text "Voy a likear tus fotos en Insta." --target en
```

Override the query tag for tracing:

```bash
SNOWFLAKE_QUERY_TAG=cortex-translate-demo \
uv run cortex-translate --text "Good morning" --source en --target de
```

## Run the REST API

Start the FastAPI server locally:

```bash
export TRANSLATION_API_KEY=change-me-before-exposing-the-api
uv run uvicorn cortex_translate_service.api:app --host 127.0.0.1 --port 8000
```

Check health:

```bash
curl http://127.0.0.1:8000/healthz
```

Translate text through the REST endpoint:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/translations \
  -H "Content-Type: application/json" \
  -H "x-api-key: $TRANSLATION_API_KEY" \
  -d '{
    "text": "Hello world",
    "source_language": "en",
    "target_language": "ko"
  }'
```

OpenAPI is available at:

```text
http://127.0.0.1:8000/openapi.json
```

## Run tests

```bash
uv run pytest --cov=src/cortex_translate_service --cov-report=term-missing
```

Type-check the service and tests:

```bash
uv run mypy src tests
```

Verify docstring coverage:

```bash
uv run interrogate src tests
```

## Build and run the API container

Build the image:

```bash
docker build -t cortex-translate-service:local .
```

Run the API server container:

```bash
docker run --rm -p 8000:8000 \
  -v "$PWD/.snowflake:/run/secrets/snowflake:ro" \
  -e SNOWFLAKE_HOME=/run/secrets/snowflake \
  -e SNOWFLAKE_DEFAULT_CONNECTION_NAME=dev \
  -e SNOWFLAKE_CONNECTION_NAME=dev \
  -e TRANSLATION_API_KEY="$TRANSLATION_API_KEY" \
  cortex-translate-service:local
```

Mount Snowflake connection material read-only or inject workload identity at
runtime. Do not bake credentials into the image.
The runtime image drops privileges to a dedicated non-root user before starting
Uvicorn.
OCI-first local builders such as Podman may ignore Docker `HEALTHCHECK`
metadata even though GitHub Actions still publishes the image.

## Repository governance and automation

This repository includes public-repo governance and GitHub automation for:

- Apache-2.0 licensing
- contribution and security disclosure policies
- CODEOWNERS and PR checklist guidance
- Git Flow-aligned branch governance for protected `main` and `develop`
- CI with pytest coverage and mypy gates
- dependency review and CodeQL security scanning
- scheduled OSSF Scorecard analysis
- GitHub Pages deployment from `site/`
- GHCR multi-architecture image releases with SBOM and provenance

See `docs/release-publishing.md` for the repository admin checklist and release
process.

## Live Snowflake verification

1. Run `sql/setup.sql` with a sufficiently privileged role after replacing
   the placeholder identifiers.
2. Switch to the `dev` profile context.
3. Run `sql/verify.sql` in Snowflake, or execute the CLI locally:

   ```bash
   SNOWFLAKE_HOME="$PWD/.snowflake" \
   SNOWFLAKE_DEFAULT_CONNECTION_NAME=dev \
   SNOWFLAKE_CONNECTION_NAME=dev \
   uv run cortex-translate --text "Hello world" --source en --target ko
   ```

## Security notes

- `.snowflake/` is ignored so local profiles are not committed.
- Keep credentials outside the repository.
- Prefer `externalbrowser`, key-pair auth, OAuth, PAT, or workload
  identity over plaintext passwords.
- Set `TRANSLATION_API_KEY` before enabling the REST API; the endpoint rejects
  requests until a key is configured.
- Keep the API behind network controls and rate limiting when exposing it
  outside localhost.
- Translation text is capped at 5,000 characters per request to limit abuse and
  unexpected Snowflake spend.
- The CLI returns translated output or operator-facing failure context.
- The REST API returns translated output or stable high-level error messages
  without exposing backend runtime details.
