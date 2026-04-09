# Architecture

Last updated: 2026-04-08

## Overview

This project provides a minimal translation service for Snowflake Cortex.
A local CLI and a small REST API receive translation input, validate it in
a small domain layer, and delegate execution to a Snowflake connector
adapter that calls `AI_TRANSLATE` through a named connection profile.

## Components

### Domain (`src/cortex_translate_service/domain.py`)

- `TranslationRequest`: immutable input value object
- `TranslationResult`: immutable output value object
- `TranslationValidationError`: validation exception

### Application (`src/cortex_translate_service/service.py`)

- `TranslationGateway`: infrastructure boundary
- `TranslationService`: orchestrates translation requests
- `TranslationGatewayError`: gateway/runtime exception

### Infrastructure (`src/cortex_translate_service/snowflake_gateway.py`)

- `SnowflakeTranslationGateway`: uses `snowflake.connector.connect(connection_name=...)`
- applies `QUERY_TAG` and statement timeout session parameters
- executes parameterized `AI_TRANSLATE(..., TRUE)` SQL

### Delivery (`src/cortex_translate_service/cli.py`)

- parses CLI arguments
- builds the environment-backed service
- prints translated text or a safe failure message

### API Delivery (`src/cortex_translate_service/api.py`)

- exposes `GET /healthz`
- exposes `POST /api/v1/translations`
- maps request, domain, and gateway failures to controlled JSON responses
- publishes OpenAPI for the REST interface

## Runtime flow

1. The operator activates a local Snowflake profile under `SNOWFLAKE_HOME`.
2. The CLI or REST API builds a `TranslationRequest`.
3. `TranslationService` delegates to `SnowflakeTranslationGateway`.
4. The gateway opens the named connection and executes `AI_TRANSLATE`.
5. The translated value is returned as `TranslationResult` and surfaced
   either as CLI stdout or JSON API output.

## Operational artifacts

- `config/connections.toml.example`: dev-profile template
- `sql/setup.sql`: required grants and warehouse/database usage setup
- `sql/verify.sql`: direct SQL verification for the Cortex translation path
- `docs/plans/`: design and implementation records
