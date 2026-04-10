<!-- markdownlint-disable MD013 -->

# Pull Request Summary

-

## Intent / Why

| File / Area | Intent | Why this changed | Risk / Notes |
| --- | --- | --- | --- |
| | | | |

## Verification

- [ ] `uv run pytest --cov=src/cortex_translate_service --cov-report=term-missing`
- [ ] `uv run mypy src tests`
- [ ] `uv run interrogate src tests`
- [ ] `docker build -t cortex-translate-service:local .`
      (if runtime/container files changed)

## Security Review

- [ ] no secrets or credentials added
- [ ] error messages remain safe for public-repo exposure
- [ ] workflow permission changes reviewed for
      least privilege

## Operational Notes

- [ ] changelog updated if behavior, release, or governance changed
- [ ] docs updated if operator workflow changed
