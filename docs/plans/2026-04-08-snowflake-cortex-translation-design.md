<!-- markdownlint-disable MD013 MD022 MD032 -->

# Snowflake Cortex Translation Service Design

**Goal:** Build a local Python translation service that activates a Snowflake `dev` connection profile and translates text through Snowflake Cortex `AI_TRANSLATE`.

## Project context

- The workspace started empty, so the service needs full scaffolding.
- The user explicitly wants a Snowflake dev profile and Cortex AI translation flow.
- Snowflake documentation confirms `AI_TRANSLATE(text, source_language, target_language[, return_error_details])` is the preferred function and requires the `SNOWFLAKE.CORTEX_USER` database role.
- Snowflake Python Connector documentation confirms named connections in `connections.toml`, `SNOWFLAKE_HOME`, and `SNOWFLAKE_DEFAULT_CONNECTION_NAME` support a safe local dev profile workflow.

## Constraints

- Do not commit credentials or `.snowflake/` runtime state.
- Prefer a named `dev` profile over hardcoded connection settings.
- Keep the implementation small enough to verify mechanically without live Snowflake credentials.
- Make the runtime path explicit: local CLI -> domain service -> Snowflake connector -> `AI_TRANSLATE` query.
- Preserve a safe default authentication path by documenting `externalbrowser` and allowing profile-based overrides.

## Approaches considered

### 1. Streamlit in Snowflake app
- **Pros:** Native UX inside Snowflake, easy demo surface.
- **Cons:** Requires Snowsight app scaffolding, browser/runtime verification, and more deployment assumptions than the request needs.

### 2. Local Python CLI service backed by Snowflake connector (**recommended**)
- **Pros:** Smallest working service, clean dev-profile activation, easy unit testing, clear separation between domain logic and Snowflake I/O.
- **Cons:** Live translation still needs real Snowflake credentials.

### 3. SQL-only worksheet / stored procedure demo
- **Pros:** Minimal moving parts.
- **Cons:** Weak developer ergonomics, poor reuse, and no service abstraction.

## Recommended design

Build a `src/`-layout Python project using `uv`, with a small domain model and a Snowflake adapter.

### Components

1. **Domain layer**
   - `TranslationRequest`: immutable value object validating input text and language values.
   - `TranslationResult`: immutable value object carrying translated text and execution metadata.
   - `TranslationService`: application-facing service that delegates translation to a gateway.

2. **Infrastructure layer**
   - `SnowflakeTranslationGateway`: connects with `connection_name="dev"` by default, sets session parameters (`QUERY_TAG`, statement timeout), and executes parameterized `AI_TRANSLATE` SQL.
   - `build_gateway_from_env()`: uses `SNOWFLAKE_CONNECTION_NAME`, `SNOWFLAKE_QUERY_TAG`, and `SNOWFLAKE_STATEMENT_TIMEOUT_SECONDS` for local control.

3. **Delivery surface**
   - CLI entry point for `uv run cortex-translate --text ... --source ... --target ...`.
   - SQL setup/verification files to grant `SNOWFLAKE.CORTEX_USER` and smoke-test translation directly in Snowflake.
   - README and example profile template documenting how to activate the `dev` profile safely.

## Data flow

1. Developer configures local Snowflake profile in `connections.toml`.
2. CLI collects text/language parameters.
3. Domain layer validates and normalizes the request.
4. Gateway opens a Snowflake connection using the named profile.
5. Gateway executes `SELECT AI_TRANSLATE(%(text)s, %(source_language)s, %(target_language)s, TRUE)`.
6. On success, the CLI prints the translated text. On SQL/provider errors, it prints a clear non-secret error message.

## Error handling

- Reject blank source text or missing language inputs before any Snowflake call.
- Treat missing query results and Snowflake connector failures as `TranslationGatewayError`.
- Use `return_error_details = TRUE` so the adapter can surface Cortex-side errors deterministically.
- Avoid logging secrets, account identifiers beyond the configured connection name, or profile file contents.

## Testing strategy

- Unit-test domain validation and normalization.
- Unit-test service delegation and result shaping.
- Unit-test Snowflake gateway SQL execution with a fake connector/cursor.
- Unit-test CLI success and error paths with a fake service.
- Mechanical verification uses `uv run pytest --cov=src/cortex_translate_service --cov-report=term-missing`.
- Live Snowflake verification is documented in `sql/verify.sql` and `README.md`, but depends on real credentials.

## Decisions and assumptions

- Choose a CLI service instead of a web app to minimize unnecessary runtime/deployment complexity.
- Default to the `dev` named profile because the user asked for a Snowflake dev profile.
- Document `externalbrowser` as the safest default local auth mode.
- Keep source language explicit but allow auto-detect via an empty string because `AI_TRANSLATE` supports it.
- Treat missing Snowflake credentials as a live-verification blocker, not as a reason to skip implementation.
