<!-- markdownlint-disable MD013 MD022 MD032 -->

# Snowflake Cortex Translation REST API & Public Publication Design

**Goal:** Evolve the local Snowflake Cortex translation CLI into a public repository that also ships a RESTful API, protected GitHub delivery flow, GHCR container release, OSSF Scorecard automation, and a Korean GitHub Pages manual.

## Project context

- The current codebase is a tested Python CLI package that calls Snowflake Cortex `AI_TRANSLATE` through a named Snowflake connection profile.
- The repository is currently local-only: no commits, no remote, no CI/CD, no container image, no Pages site, and no GitHub governance files.
- The user now requires RESTful API support in addition to the existing CLI.
- The user also requires public publication under the `https://github.com/seongho-bae` namespace when no origin exists.

## Constraints

- Preserve the existing CLI workflow and Snowflake named-profile behavior.
- Do not commit credentials or runtime Snowflake connection state.
- Keep the public repo usable as a self-hosted service, not a hosted SaaS assumption.
- Publish the repository as public, release a GHCR image, and publish a Korean web manual on GitHub Pages.
- Apply branch protection/rulesets and an explicit Git Flow-style branching model.
- Keep the API surface small, documented, and mechanically verifiable.

## Approaches considered

### 1. Publish the current CLI-only project as-is
- **Pros:** Smallest change set.
- **Cons:** Fails the new RESTful API requirement, leaves no container/runtime API surface, and under-delivers on public repo expectations.

### 2. Add a minimal ASGI REST API alongside the CLI and automate public delivery (**recommended**)
- **Pros:** Reuses the current domain/service/gateway layers, keeps the CLI intact, exposes a standard REST surface, enables OpenAPI, Docker, Pages docs, and GitHub Actions with manageable scope.
- **Cons:** Requires new dependencies, API tests, and deployment automation.

### 3. Replace the CLI with a full hosted-style API platform
- **Pros:** Maximizes API-first posture.
- **Cons:** Unnecessary scope expansion, breaks current CLI consumers, and adds avoidable operational complexity.

## Recommended design

Retain the current DDD-style translation core and add a thin FastAPI delivery layer that exposes a versioned REST API while preserving the CLI entry point.

### Runtime architecture

1. **Domain layer**
   - Keep `TranslationRequest`, `TranslationResult`, and validation behavior.
   - Continue to treat blank text / blank target language as validation failures.

2. **Application layer**
   - Keep `TranslationService` as the orchestration boundary.
   - Reuse the existing `TranslationGateway` protocol for both CLI and API flows.

3. **Infrastructure layer**
   - Keep the Snowflake connector adapter using named connections and `AI_TRANSLATE(..., TRUE)`.
   - Continue to source connection name, query tag, and statement timeout from environment variables.

4. **Delivery surfaces**
   - Preserve the CLI command for local operator use.
   - Add a FastAPI app with:
     - `GET /healthz`
     - `POST /api/v1/translations`
     - generated `openapi.json`
   - Return structured JSON responses and controlled error payloads without secret leakage.

### Repository publication design

1. **Repository name**
   - Use `snowflake-cortex-translate` as the GitHub repository slug.
   - This keeps the repo concise while still matching the current package name and the service/API direction.

2. **Git Flow model**
   - `main`: protected production/release branch.
   - `develop`: protected integration branch.
   - `feature/*`: short-lived working branches.
   - `release/*`: release promotion branches from `develop` to `main`.
   - `hotfix/*`: production repair branches from `main`.

3. **GitHub governance**
   - Add `LICENSE`, `SECURITY.md`, `CONTRIBUTING.md`, `CODEOWNERS`, PR template, Dependabot, and changelog automation.
   - Apply GitHub rulesets to `main` and `develop` that require pull requests, passing checks, conversation resolution, linear history, and disallow force-push / deletion.

4. **Automation**
   - CI: install with `uv`, run tests, coverage, and type checks.
   - Dependency review: required on pull requests.
   - CodeQL: required security gate.
   - Scorecard: scheduled and branch-aware OSSF Scorecard workflow.
   - Pages: deploy a Korean static manual from repository sources.
   - Container release: multi-arch `linux/amd64` and `linux/arm64` build/push to GHCR on version tags.

### Korean manual design

- Publish a Korean GitHub Pages manual as a static site generated from repository sources.
- Keep the site dependency-light and self-contained, using bundled CSS/JS and no external font endpoints.
- Cover:
  - project overview
  - Snowflake profile setup
  - CLI usage
  - REST API usage with request/response examples
  - Docker usage
  - Git Flow / contribution path
  - security and release notes

### API security baseline

- Bind to localhost by default for local development.
- Validate request body fields with schema validation.
- Return explicit JSON error payloads for validation/runtime failures.
- Avoid reflecting sensitive environment details in errors.
- Document that upstream deployment owners should add network/auth controls when exposing the API outside localhost.

## Data flow

1. Client calls the CLI or REST API.
2. Delivery layer validates input and builds a `TranslationRequest`.
3. `TranslationService` delegates to `SnowflakeTranslationGateway`.
4. The gateway opens the named Snowflake connection and executes `AI_TRANSLATE`.
5. The result is returned as a CLI string or JSON API response.

## Testing strategy

- Keep existing unit tests green.
- Add REST API tests for success, validation failure, and gateway failure paths.
- Verify coverage remains at 100%.
- Verify static manual files are lintable and deployable.
- Verify Docker build locally if the container runtime is available.
- Verify GitHub Actions by pushing branch/tag workflows and collecting PR/release evidence.

## Decisions and assumptions

- Choose FastAPI because it gives typed request validation, OpenAPI generation, and a minimal REST surface with low ceremony.
- Keep the package name `cortex-translate-service` to minimize churn even though
  the public repository slug is `snowflake-cortex-translate`.
- Use a static Pages site instead of a JS-heavy docs framework to reduce maintenance overhead.
- Use Git Flow because the user explicitly requested it, even though a simpler trunk-only model would also work.
- Treat GHCR publication through GitHub Actions as the authoritative release path.
