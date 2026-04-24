"""Monkey-patches for third-party library bugs.

This module applies targeted fixes for known issues in dependencies.
Each patch is documented with the upstream issue URL (when filed) and
the version range it applies to.  Patches are idempotent and safe to
import multiple times.

Apply by importing this module early in the boot sequence (e.g. plugins.py).
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable

logger = logging.getLogger(__name__)

_PATCHES_APPLIED: set[str] = set()


# ---------------------------------------------------------------------------
# Patch 1: litestar-vite proxy sends chunked body on GET requests
# ---------------------------------------------------------------------------
# Affected versions: litestar-vite 0.22.1 (and likely earlier)
# Root cause: ViteProxyMiddleware._proxy_http() always passes an async
#   generator from _stream_request_body() as the `content` parameter to
#   httpx.AsyncClient.stream(), even for GET/HEAD/OPTIONS requests.
#   httpx interprets any async generator as a streaming body and adds
#   Transfer-Encoding: chunked.  Vite's dev server (and many other HTTP
#   servers) reject GET requests with a chunked body -> 400 Bad Request.
# Fix: Replace _proxy_http with a version that passes content=None for
#   HTTP methods that don't carry a request body.
# Upstream: https://github.com/litestar-org/litestar-vite/issues/XXX
# ---------------------------------------------------------------------------

_BODY_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})


def patch_vite_proxy_chunked_body() -> None:
    """Patch ViteProxyMiddleware._proxy_http to skip body for bodiless methods."""
    if "vite_proxy_chunked_body" in _PATCHES_APPLIED:
        return

    try:
        # NOTE: check_http2_support lives in _proxy, NOT _utils
        import httpx
        from litestar_vite.plugin._proxy import (
            ViteProxyMiddleware,
            _filter_hop_by_hop_headers,
            _proxy_stream_response,
            _stream_request_body,
            check_http2_support,
        )
    except ImportError as exc:
        logger.debug("litestar-vite not installed or incompatible, skipping proxy patch: %s", exc)
        return

    # Mark as applied only AFTER imports succeed
    _PATCHES_APPLIED.add("vite_proxy_chunked_body")

    async def _patched_proxy_http(
        self: Any,
        scope: dict[str, Any],
        receive: Callable[..., Any],
        send: Callable[..., Any],
    ) -> None:
        """Patched version of _proxy_http that skips body for GET/HEAD/OPTIONS."""
        target_base_url = self._get_target_base_url()
        if target_base_url is None:
            await send({"type": "http.response.start", "status": 503, "headers": [(b"content-type", b"text/plain")]})
            await send({"type": "http.response.body", "body": b"Vite server not running", "more_body": False})
            return

        method = scope.get("method", "GET")
        raw_path = scope.get("raw_path", b"").decode()
        query_string = scope.get("query_string", b"").decode()
        proxied_path = raw_path
        if self.asset_prefix != "/" and not raw_path.startswith(self.asset_prefix):
            proxied_path = f"{self.asset_prefix.rstrip('/')}{raw_path}"

        url = f"{target_base_url}{proxied_path}"
        if query_string:
            url = f"{url}?{query_string}"

        headers = _filter_hop_by_hop_headers(scope.get("headers", []))

        # FIX: Only stream request body for methods that carry a body.
        # Passing an async generator as content for GET/HEAD causes httpx to add
        # Transfer-Encoding: chunked, which Vite dev server rejects with 400.
        request_body = _stream_request_body(receive) if method in _BODY_METHODS else None

        # Use shared client from plugin when available (connection pooling)
        client = self._plugin.proxy_client if self._plugin is not None else None

        try:
            if client is not None:
                async with client.stream(
                    method, url, headers=headers, content=request_body, timeout=10.0, follow_redirects=False
                ) as upstream_resp:
                    await _proxy_stream_response(upstream_resp, send)
            else:
                http2_enabled = check_http2_support(self.http2)
                async with (
                    httpx.AsyncClient(http2=http2_enabled) as fallback_client,
                    fallback_client.stream(
                        method, url, headers=headers, content=request_body, timeout=10.0, follow_redirects=False
                    ) as upstream_resp,
                ):
                    await _proxy_stream_response(upstream_resp, send)
        except Exception as exc:  # noqa: BLE001
            await send({"type": "http.response.start", "status": 502, "headers": [(b"content-type", b"text/plain")]})
            await send({"type": "http.response.body", "body": f"Upstream error: {exc}".encode(), "more_body": False})

    ViteProxyMiddleware._proxy_http = _patched_proxy_http  # type: ignore[assignment]  # noqa: SLF001
    logger.info("Applied patch: vite_proxy_chunked_body (GET requests no longer send chunked body)")


# ---------------------------------------------------------------------------
# Apply all patches on import
# ---------------------------------------------------------------------------


def apply_all() -> None:
    """Apply every registered patch."""
    patch_vite_proxy_chunked_body()


apply_all()
