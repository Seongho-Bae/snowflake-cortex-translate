## 2024-05-24 - [Fix API key timing attack vulnerability]
**Vulnerability:** The API key verification in `api.py` used a simple equality check (`x_api_key != configured_api_key`), which is vulnerable to timing attacks. An attacker could potentially deduce the API key by measuring the time it takes for the comparison to fail.
**Learning:** This existed because Python's default string comparison operators (`==` and `!=`) return early as soon as a character mismatch is found.
**Prevention:** Always use a constant-time comparison function, such as `secrets.compare_digest()`, when comparing sensitive strings like passwords, tokens, or API keys.
