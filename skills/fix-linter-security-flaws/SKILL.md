# Skill: fix-linter-security-flaws

# Fix Linter Errors and Security Flaws

## Overview
Use this skill when encountering Linter warnings, Deprecated messages, formatting issues, or Security flaws (e.g., CodeQL, Scorecard alerts, or Strix issues) during the workflow.

**Core principle:** Do not ignore warnings. Track the root cause and fix it completely.

## Workflow

### 1. Identify the Warning/Error
- Run the appropriate linter, type checker, or test framework.
- Look at the logs for warnings, deprecated usages, or security issues.
- **Rule:** Warnings are not to be bypassed. Strix findings are absolute blockers and must be fixed (no skipping). Other security scanners should also be treated as items to remediate immediately.

### 2. Root Cause Analysis
- Determine why the warning or error exists. Is it a legacy API, an incorrect configuration, or a missing dependency?
- If it's a security flaw, determine the best mitigation strategy (e.g., input validation, dependency updates, adding fuzzing).

### 3. Remediation
- **Linter Errors/Warnings:** Fix the syntax or logic to conform to the linter's rules. Do NOT simply use `# noqa` or suppression unless the rule is explicitly incompatible with the repository's strict constraints and requires a documented exception.
- **Deprecations:** Upgrade to the recommended replacement API.
- **Security Flaws (including Strix):** Apply the required security patches, add protection rules, or implement the recommended standard practice (e.g., Kubernetes resource limits or RBAC updates for infrastructure).

### 4. Verification
- Re-run tests, linters, and type-checkers to verify the fix.
- Ensure that the remediation did not introduce any regressions.

## Kubernetes Consideration
If the error or security flaw relates to Kubernetes (e.g., missing security contexts, exposed ports):
- Ensure that the corresponding Kubernetes manifests (`.yaml`) or configurations are updated.
- Verify that standard security contexts are applied. Specifically, Kubernetes manifests must define `runAsNonRoot: true`, `readOnlyRootFilesystem: true`, and `allowPrivilegeEscalation: false`.

## Conclusion
Once fixed, report the successful remediation of the root cause in the relevant task or PR.