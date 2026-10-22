"""
Dashboard module: /stats, /ui, strategy-switch endpoints.

These routes are registered BEFORE the catch-all door, so /stats and /ui
answer from the door itself instead of being proxied to a helper.
"""

import logging
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from src.metrics import metrics
from src.strategies import STRATEGY_LABELS, manager

logger = logging.getLogger(__name__)

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
DASHBOARD_FILE = STATIC_DIR / "dashboard.html"

router = APIRouter()


def _pool(request: Request):
    return getattr(request.app.state, "pool", None)


@router.get("/stats")
async def stats(request: Request):
    """The whole tally board as one tidy snapshot, for humans and the UI."""
    snapshot = metrics.snapshot(_pool(request), manager.active, STRATEGY_LABELS)
    return JSONResponse(snapshot, headers={"Cache-Control": "no-store"})


@router.get("/ui", include_in_schema=False)
@router.get("/dashboard", include_in_schema=False)
async def dashboard_page():
    return FileResponse(
        DASHBOARD_FILE,
        media_type="text/html",
        headers={"Cache-Control": "no-store"},
    )


class StrategyChoice(BaseModel):
    strategy: str


@router.post("/ui/strategy")
async def switch_strategy(choice: StrategyChoice):
    """Swap the choosing rule while kids are still coming in.

    This changes ONE name on the single event loop. Requests already being
    forwarded keep the rule they started with; the next request reads the
    new one. Nothing is dropped.
    """
    try:
        active = manager.set_strategy(choice.strategy)
    except ValueError:
        return JSONResponse(
            {
                "ok": False,
                "error": f"unknown strategy: {choice.strategy}",
                "available": STRATEGY_LABELS,
            },
            status_code=400,
        )

    logger.info("[STRATEGY] switched to %s", active)
    return {"ok": True, "active": active, "available": STRATEGY_LABELS}
