# Contributing

Thanks for contributing to Cortex Translate Service.

## Development Setup

```bash
uv sync --dev
```

Optional local Snowflake setup:

```bash
mkdir -p .snowflake
cp config/connections.toml.example .snowflake/connections.toml
export SNOWFLAKE_HOME="$PWD/.snowflake"
export SNOWFLAKE_DEFAULT_CONNECTION_NAME=dev
export SNOWFLAKE_CONNECTION_NAME=dev
```

## Required Local Checks

Run these before opening a pull request:

```bash
uv run pytest --cov=src/cortex_translate_service --cov-report=term-missing
uv run mypy src tests
uv run interrogate src tests
docker build -t cortex-translate-service:local .
```

The test suite enforces **100% coverage**, and docstring coverage is also gated at
**100%**.

If your change touches the REST API, also verify that authenticated requests use
`x-api-key`, unauthenticated requests fail safely, and any public deployment
plan keeps upstream rate limiting / network controls in place.

## Branch and PR Expectations

- follow the Git Flow baseline: `develop` is the integration branch, `main` is
  the release branch, and short-lived `feature/*`, `release/*`, and
  `hotfix/*` branches promote change between them
- keep docs-only work on focused `docs/*` branches when that isolates review
- open pull requests instead of pushing directly to protected `develop` or
  `main`
- keep changes focused and document operational impact in the PR description
- include updates to governance, documentation, or release notes when the user
  or operator experience changes

## Commit Style

Conventional commit prefixes are recommended:

- `feat:` for user-facing additions
- `fix:` for bug fixes
- `docs:` for documentation changes
- `ci:` for workflow or automation changes
- `security:` for hardening and governance changes

## Security and Secrets

- never commit secrets, credentials, or copied production data
- do not paste tokens into issues, pull requests, or workflow logs
- use `.env.example` and `config/connections.toml.example` only as templates

## Release Notes

- keep `CHANGELOG.md` in Keep a Changelog format
- cut container releases from semantic tags like `vX.Y.Z` on reviewed `main`
  history only
- use `docs/release-publishing.md` as the operator checklist for GitHub Pages,
  GHCR publishing, and required branch rules
