## 2024-06-01 - [FastAPI Dependency Memoization]
**Learning:** Re-instantiating the translation gateway and service per-request can add significant overhead in FastAPI when reading from env/files or constructing connections, especially in `get_service()`.
**Action:** Use `@lru_cache` on the `get_service` dependency function to ensure the service instance is built exactly once and reused for all requests, avoiding redundant allocation and configuration lookup per API call.
