# Korean Pages Copy Cleanup Design

**Goal:** Remove manual/meta framing from the public Korean Pages experience while preserving the service setup and operation guidance.

## Context

- `site/index.html` still presents the public page as a "manual" and contains self-referential copy such as `매뉴얼`, `Manual`, and `안내서`.
- `README.md` and `ARCHITECTURE.md` still describe the public Korean page as a manual, which would leave top-level repo messaging inconsistent after the site copy is cleaned up.
- The latest user instruction requires removing meta/manual wording from the Korean site/manual.

## Constraints

- Keep the existing static site structure, assets, and section layout intact.
- Avoid expanding scope into archival design/implementation plan documents unless technically necessary.
- Use the existing pytest-based test harness rather than adding new tooling.
- Re-verify the public page through Playwright on a clean localhost port after the copy change.

## Approaches considered

### 1. Patch only `site/index.html`
- **Pros:** Smallest diff.
- **Cons:** Leaves `README.md` and `ARCHITECTURE.md` inconsistent with the published page.

### 2. Align the public page and top-level public docs (**recommended**)
- **Pros:** Keeps the public-facing repo entry points consistent, contains scope to the current surface area, and is easy to lock with a lightweight regression test.
- **Cons:** Slightly broader diff than a site-only patch.

### 3. Replace the wording repo-wide, including historical plans and changelog entries
- **Pros:** Removes every occurrence from the repository.
- **Cons:** Rewrites historical records and creates unnecessary churn in archival documents.

## Recommended design

- Rewrite the public site copy so it describes the translation service and usage flow directly rather than labeling itself as a manual.
- Replace the top-level README and architecture references with neutral phrasing such as "page", "site", or "public guidance".
- Add a lightweight pytest regression test that reads the public-facing files and rejects banned manual/meta terms.

## Verification

- Run a targeted pytest check for the new copy regression test.
- Sweep the public-facing files for banned terms.
- Re-run the existing Python verification suite (`pytest`, `mypy`, `interrogate`).
- Verify the updated page with Playwright against a localhost-served copy on a free port.

## Decisions

- Scope the cleanup to `site/index.html`, `README.md`, and `ARCHITECTURE.md`.
- Treat `매뉴얼`, `Manual`, `안내서`, and repo/publication self-reference in the public page copy as banned user-facing framing for this cleanup.
- Leave archival plan and changelog text unchanged for now.
