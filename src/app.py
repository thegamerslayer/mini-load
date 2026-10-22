"""
App module: FastAPI wiring and lifespan (health check loop initialization).
"""
import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
from src.proxy import forward
from src.health import health_check_loop
from src.dashboard import router as dashboard_router




@asynccontextmanager
async def lifespan(app: FastAPI):
    active_pool = getattr(app.state, "pool", None)
    
    health_task = None
    if active_pool:
        health_task = asyncio.create_task(health_check_loop(active_pool))
    try:
        yield  # <-- App runs and handles requests here
    finally:
        if health_task:
            health_task.cancel()
            try:
                await health_task
            except asyncio.CancelledError:
                pass
app = FastAPI(lifespan=lifespan)

# Registered BEFORE the catch-all below, so /stats and /ui belong to the
# door itself and are never proxied to a helper.
app.include_router(dashboard_router)

pool = None

# Response headers we must not copy: hop-by-hop headers, plus headers the
# proxy/server must generate itself (we stream, so length is unknown, and
# uvicorn adds its own date/server).
RESPONSE_HOP_BY_HOP = {
    "transfer-encoding", "content-length", "connection", "keep-alive",
    "trailers", "upgrade", "te", "proxy-authenticate", "proxy-authorization",
    "date", "server",
}


class MultiValueHeaders:
    """Mapping-like wrapper preserving duplicate headers (e.g. Set-Cookie).

    Starlette only calls ``.items()`` on the headers mapping, so returning the
    full list of pairs keeps duplicates instead of joining them with commas.
    """

    def __init__(self, items):
        self._items = items

    def items(self):
        return self._items


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD"])

async def catch_all(request: Request, path: str):
    
    active_pool = getattr(request.app.state, "pool", None) or pool
    
    response = await forward(active_pool, request)

    # multi_items() keeps duplicate headers (e.g. multiple Set-Cookie).
    response_headers = MultiValueHeaders([
        (k, v)
        for k, v in response.headers.multi_items()
        if k.lower() not in RESPONSE_HOP_BY_HOP
    ])

    async def stream_body():
        try:
            # aiter_raw keeps the bytes encoded exactly as the backend sent
            # them, so Content-Encoding (e.g. gzip) stays truthful.
            async for chunk in response.aiter_raw():
                yield chunk
        finally:
            await response.aclose()

    return StreamingResponse(
        content=stream_body(),
        status_code=response.status_code,
        headers=response_headers,
    )

