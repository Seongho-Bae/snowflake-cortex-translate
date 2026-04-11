<!-- markdownlint-disable MD024 -->

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.4] - 2026-04-11

### Added

- a public OpenSSF Scorecard badge plus documented API and viewer endpoints for
  repository governance checks

### Fixed

- kept the OSSF Scorecard analysis job compatible with `api.scorecard.dev`
  publication rules by isolating shell reporting in a follow-up job
- preserved the generated Scorecard SARIF as an Actions artifact so failed
  publication attempts still leave inspectable evidence for operators

## [0.1.3] - 2026-04-10

### Fixed

- aligned the FastAPI OpenAPI version with packaged release metadata so the
  published API contract no longer reports a stale historical version
- replaced stale hard-coded release tag examples in public docs with generic
  semantic placeholders and locked the contract with regression coverage

## [0.1.2] - 2026-04-10

### Added

- workflow regression coverage for Pages fallback bootstrapping, dependency-review
  graph probing, security policy links, and GitHub Actions pin hygiene

### Changed

- refreshed the develop branch to the released mainline before merging follow-up
  dependency updates
- updated GitHub Actions checkout, setup-uv, and CodeQL pins to current
  Node24-compatible immutable revisions
- adjusted dependency review to summarize the missing dependency-graph blocker
  instead of leaving pull requests red when GitHub has the feature disabled
- upgraded `snowflake-connector-python` to 4.4.0, `pytest` to 9.0.3, and
  `pytest-cov` to 7.1.0 with regenerated `uv.lock`
- removed CodeQL unnecessary-lambda findings from REST API tests without
  changing test behavior

### Fixed

- repaired the GitHub Pages fallback heredoc so the Pages workflow can publish
  even when `site/` assets are absent at build time

### Security

- scoped CodeQL and Scorecard write permissions to job level and preserved
  explicit fallback reporting when Scorecard cannot publish SARIF
- linked `SECURITY.md` to the private advisory endpoint and maintainer contact
  address for direct vulnerability disclosure

## [0.1.1] - 2026-04-10

### Added

- public repository governance files for licensing, contribution guidance,
  ownership, and security disclosure
- GitHub Actions workflows for CI, dependency review, CodeQL, OSSF Scorecard,
  GitHub Pages publishing, and GHCR multi-architecture image releases
- a docstring coverage gate that enforces 100% documented Python and test
  symbols in CI and local verification
- a container build for the FastAPI server with production-oriented dependency
  installation and health checking
- release and publishing notes for protected branches, Pages, and GHCR
- a bundled GitHub Pages favicon for the Korean service page

### Changed

- aligned README, architecture notes, contribution guidance, and Korean service page
  content with the shared bootstrap wiring and Git Flow publication model
- corrected CODEOWNERS to the authenticated maintainer account
- hardened the container image to run the API as a dedicated non-root user
- tightened release guidance so semantic tags are cut only from reviewed
  `main` history
- documented the required read-only Snowflake profile mount for container runs
- required API-key configuration and a 5,000-character limit for the REST API

### Security

- required automation for dependency review and CodeQL scanning
- SBOM and build provenance publication for GHCR image releases
- release automation now rejects tags that are not already reachable from
  protected `main`
- local Playwright and `.env` artifacts are excluded from git and Docker build
  contexts
- REST API 502 responses now return a stable public message instead of backend
  exception text
- public REST API guidance now requires `TRANSLATION_API_KEY`, upstream rate
  limiting, and network controls before exposure beyond localhost

## [0.1.0] - 2026-04-09

### Added

- initial Snowflake Cortex translation CLI and REST API service
- Snowflake profile configuration examples and SQL verification scripts
