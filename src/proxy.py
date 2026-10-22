"""
Proxy module: Request-forwarding core (simplified version)
"""

import time

import httpx
from fastapi import Request

from src.metrics import metrics
from src.strategies import manager

# Shared HTTP client with base timeout
client = httpx.AsyncClient(timeout=httpx.Timeout(10.0, connect=2.0))

# Headers we should NOT forward (hop-by-hop)
HOP_BY_HOP = {"host", "transfer-encoding", "content-length", "connection", "keep-alive"}


async def forward(pool, request: Request):
    """
    Forward incoming request to one backend chosen by the balancer.
    Adds safe headers, X-Forwarded-For, and handles timeouts.

    Every attempt is timed and counted on the tally board - including the
    ones that fail, so the dashboard cannot report a 0% error rate during a
    break.
    """

    # STEP 1: Decide if retry is safe (idempotent methods only)
    safe_to_retry = request.method in {"GET", "HEAD", "PUT", "DELETE", "OPTIONS", "TRACE"}
    max_attempts = 2 if safe_to_retry else 1

    # STEP 2: Copy headers safely (skip hop-by-hop)
    forward_headers = {}
    for incoming_name, incoming_value in request.headers.items():
        if incoming_name.lower() not in HOP_BY_HOP:
            forward_headers[incoming_name] = incoming_value

    # STEP 3: Add X-Forwarded-For with client IP
    client_ip = request.client.host if request.client else "127.0.0.1"
    if "x-forwarded-for" in forward_headers:
        forward_headers["x-forwarded-for"] += f", {client_ip}"
    else:
        forward_headers["x-forwarded-for"] = client_ip

    # STEP 4: Build target path and timeout
    path = request.url.path
    timeout = httpx.Timeout(5.0, connect=2.0)
    body = await request.body()

    # STEP 5: Try sending to backend (with retry if allowed)
    for attempt in range(max_attempts):
        backend = await manager.choose(pool)
        if backend is None:
            metrics.note_no_backend()
            return httpx.Response(status_code=503, text="No backends available in pool")

        target_url = backend.url.rstrip("/") + path

        # Build request (use body for simplicity instead of stream)
        req = client.build_request(
            method=request.method,
            url=target_url,
            params=request.query_params,
            headers=forward_headers,
            content=body,
            timeout=timeout,
        )

        # "waiting now" goes up right before we knock, and down in the
        # finally below - ALWAYS, even if the helper breaks.
        metrics.begin(backend)
        started = time.perf_counter()

        try:
            # Send request (timeout is configured on req via build_request)
            backend_response = await client.send(req, stream=True)
        except httpx.TimeoutException:
            metrics.end(backend, ok=False, latency_ms=_elapsed_ms(started), status=504)
            # If last attempt or unsafe to retry → return error
            if attempt == max_attempts - 1 or not safe_to_retry:
                return httpx.Response(status_code=504, text="Gateway Timeout")
            metrics.note_retry(backend)
        except (httpx.ConnectError, httpx.NetworkError):
            metrics.end(backend, ok=False, latency_ms=_elapsed_ms(started), status=502)
            # If backend is dead / unreachable
            if attempt == max_attempts - 1 or not safe_to_retry:
                return httpx.Response(status_code=502, text="Bad Gateway: backend unavailable")
            metrics.note_retry(backend)
        except BaseException:
            metrics.end(backend, ok=False, latency_ms=_elapsed_ms(started))
            raise
        else:
            # 4xx from a helper is its answer, not a door failure.
            metrics.end(
                backend,
                ok=backend_response.status_code < 500,
                latency_ms=_elapsed_ms(started),
                status=backend_response.status_code,
            )
            return backend_response


def _elapsed_ms(started: float) -> float:
    return round((time.perf_counter() - started) * 1000, 2)
