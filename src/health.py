"""
Health module: Background health-check loop.
"""

import asyncio
import httpx

from src.pool import Backend, Pool


async def check_backend_health(backend: Backend, client: httpx.AsyncClient):
    try:
        response = await client.get(
            f"{backend.url}/health",
            timeout=2.0,
        )

        if response.status_code == 200:
            backend.mark_success()
        else:
            backend.mark_failure()

    except Exception:
        backend.mark_failure()


async def health_check_loop(pool: Pool):
    # One client for the whole loop, and knock on everyone at the same time:
    # a sleepy helper must not delay the knock on the others - or the door.
    async with httpx.AsyncClient() as client:
        while True:
            await asyncio.gather(
                *(check_backend_health(backend, client) for backend in pool.get_all_backends()),
                return_exceptions=True,
            )

            await asyncio.sleep(5)
