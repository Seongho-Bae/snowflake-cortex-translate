## 2024-05-24 - FastAPI Dependency Caching
**Learning:** In FastAPI, dependencies like `Depends(get_service)` are re-evaluated on every single request. If the dependency simply builds a stateless service object (e.g., reading env vars and returning an adapter), this causes unnecessary CPU overhead per request.
**Action:** Use `@functools.lru_cache` on factory dependencies that return stateless services or settings to make them singletons and improve request throughput.
