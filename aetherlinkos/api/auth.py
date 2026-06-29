"""API key authentication for the AetherLinkOS REST server.

Keys are loaded from the ``AETHERLINKOS_API_KEYS`` environment variable
(comma-separated) or passed explicitly to :func:`api_key_dependency`.
When no keys are configured, authentication is disabled and every request
is allowed — this keeps local development frictionless while letting
deployments lock the API down by setting a single env var.
"""
from __future__ import annotations

import os
import secrets
from typing import TYPE_CHECKING, Callable, Iterable

if TYPE_CHECKING:
    from fastapi import FastAPI

try:
    from fastapi import HTTPException, Security, status
    from fastapi.security import APIKeyHeader
    _HAS_FASTAPI = True
except ImportError:
    _HAS_FASTAPI = False


API_KEY_HEADER = "X-API-Key"
API_KEY_ENV_VAR = "AETHERLINKOS_API_KEYS"


def load_keys_from_env() -> tuple[str, ...]:
    raw = os.environ.get(API_KEY_ENV_VAR, "")
    return tuple(k.strip() for k in raw.split(",") if k.strip())


def api_key_dependency(keys: Iterable[str] | None = None) -> Callable[..., str | None]:
    """Build a FastAPI dependency that validates the ``X-API-Key`` header.

    Pass ``keys`` to override the env-var configuration. An empty key set
    disables auth and the returned dependency always resolves to ``None``.
    """
    if not _HAS_FASTAPI:
        raise RuntimeError("FastAPI is required for api_key_dependency()")

    configured = tuple(keys) if keys is not None else load_keys_from_env()
    header_scheme = APIKeyHeader(name=API_KEY_HEADER, auto_error=False)

    async def _require_api_key(presented: str | None = Security(header_scheme)) -> str | None:
        if not configured:
            return None
        if presented is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing API key",
                headers={"WWW-Authenticate": API_KEY_HEADER},
            )
        for candidate in configured:
            if secrets.compare_digest(presented, candidate):
                return candidate
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )

    return _require_api_key


def protect_app(app: "FastAPI", keys: Iterable[str] | None = None) -> "FastAPI":
    """Gate every request on ``app`` behind the ``X-API-Key`` header.

    Installed as a middleware so it works regardless of whether routes
    are registered before or after this call. When no keys are configured
    the app is returned untouched.
    """
    if not _HAS_FASTAPI:
        return app

    configured = tuple(keys) if keys is not None else load_keys_from_env()
    if not configured:
        return app

    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.responses import JSONResponse

    class APIKeyMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            presented = request.headers.get(API_KEY_HEADER)
            if presented is None:
                return JSONResponse(
                    {"detail": "Missing API key"},
                    status_code=401,
                    headers={"WWW-Authenticate": API_KEY_HEADER},
                )
            for candidate in configured:
                if secrets.compare_digest(presented, candidate):
                    return await call_next(request)
            return JSONResponse({"detail": "Invalid API key"}, status_code=403)

    app.add_middleware(APIKeyMiddleware)
    return app


__all__ = [
    "API_KEY_HEADER",
    "API_KEY_ENV_VAR",
    "api_key_dependency",
    "load_keys_from_env",
    "protect_app",
]
