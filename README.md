# Cortex Translate Service

Local Python translation service and REST API that use a Snowflake `dev`
profile and Snowflake Cortex `AI_TRANSLATE`.

## What this project does

- activates a named Snowflake connection profile (default: `dev`)
- sends translation requests to Snowflake Cortex `AI_TRANSLATE`
- exposes the flow through both a CLI and a RESTful API
- documents the grants and SQL verification needed for live Snowflake use

## Project layout

```text
.
├── ARCHITECTURE.md
├── README.md
├── config/
│   └── connections.toml.example
├── docs/plans/
├── pyproject.toml
├── sql/
│   ├── setup.sql
│   └── verify.sql
├── src/cortex_translate_service/
│   ├── __init__.py
│   ├── api.py
│   ├── cli.py
│   ├── domain.py
│   ├── service.py
│   └── snowflake_gateway.py
└── tests/
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
- The CLI and REST API return only translated output or high-level error
  messages.
