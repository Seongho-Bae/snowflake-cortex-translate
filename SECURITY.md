# Security Policy

## Supported Versions

The repository is currently maintained on the latest published `0.1.x` line.

| Version | Supported |
| --- | --- |
| `0.1.x` | ✅ |
| `<0.1.0` | ❌ |

## Reporting a Vulnerability

- **Do not** open public GitHub issues for suspected security vulnerabilities.
- Prefer a **private GitHub security advisory** for this repository.
- If private advisories are not available yet, contact the maintainer through a
  private channel and include only the minimum reproduction details needed to
  triage the issue.

Please include:

1. affected version, branch, image tag, or commit SHA
2. impact and exploit prerequisites
3. reproduction steps or proof-of-concept
4. any suggested mitigation or patch direction

## Response Expectations

- initial acknowledgement target: **3 business days**
- triage target: **7 business days**
- coordinated remediation and disclosure timing: based on severity and exploit
  availability

## Security Baseline for Contributors

- never commit Snowflake credentials, `.snowflake/` contents, tokens, or local
  environment files
- prefer `externalbrowser`, OAuth, PAT, key-pair, or workload identity over
  plaintext passwords
- require `TRANSLATION_API_KEY` plus upstream rate limiting / network controls
  before exposing the REST API beyond localhost
- keep translation request bodies at or below the 5,000-character application
  limit unless a reviewed cost-control change is made
- keep API error responses free of secrets or environment-specific internals
- treat CodeQL, dependency review, CI coverage, and Scorecard workflows as
  governance signals, with CI, dependency review, and CodeQL configured as the
  required protected-branch gates
