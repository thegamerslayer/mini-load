"""
Tally board: counters, a small memory of "how fast", and percentiles.

Design notes (Step 6):

  * The door runs on ONE event loop thread. Every add/subtract below happens
    between two ``await`` points, so no lock is needed. If this ever moves to
    several threads, each counter would need a lock (or an atomic type), and
    the latency deques would need one too.
  * We do NOT keep every latency forever. Each backend keeps its LAST
    ``PER_BACKEND_WINDOW`` samples; the whole door keeps the last
    ``GLOBAL_WINDOW``. That is a fixed amount of memory (a few tens of KB)
    no matter how many kids arrive.
  * Percentiles are nearest-rank over the kept sample - an approximation of
    the true p50/p95/p99, which is the trade-off we accept for bounded memory.
  * Failures are timed too. If we only recorded happy requests, the error
    rate would read 0% during a break - a lying tally board.
"""

from __future__ import annotations

import math
import time
from collections import deque
from datetime import datetime
from typing import Any, Deque, Dict, List, Optional

GLOBAL_WINDOW = 2048        # ~16 KB of floats for the whole door
PER_BACKEND_WINDOW = 256    # ~2 KB per helper
EVENT_WINDOW = 40           # recent skips/welcomes kept for the window
RPS_WINDOW_SECONDS = 5.0
RETRY_WINDOW_SECONDS = 10.0


def percentile(sorted_values: List[float], p: float) -> Optional[float]:
    """Nearest-rank percentile. ``sorted_values`` must already be sorted."""
    if not sorted_values:
        return None
    if len(sorted_values) == 1:
        return sorted_values[0]
    rank = math.ceil((p / 100.0) * len(sorted_values)) - 1
    rank = max(0, min(rank, len(sorted_values) - 1))
    return sorted_values[rank]


class LatencyWindow:
    """A fixed-size memory of the most recent response times."""

    def __init__(self, maxlen: int = GLOBAL_WINDOW):
        self.samples: Deque[float] = deque(maxlen=maxlen)
        self.total = 0

    def add(self, milliseconds: float) -> None:
        self.samples.append(milliseconds)
        self.total += 1

    def summary(self) -> Dict[str, Optional[float]]:
        ordered = sorted(self.samples)
        return {
            "p50": _round(percentile(ordered, 50)),
            "p95": _round(percentile(ordered, 95)),
            "p99": _round(percentile(ordered, 99)),
            "max": _round(ordered[-1] if ordered else None),
            "samples": len(ordered),
        }


class BackendMetrics:
    """Everything the tally board remembers about ONE helper."""

    __slots__ = (
        "in_flight",
        "in_flight_peak",
        "good",
        "bad",
        "retries",
        "latency",
        "last_status",
        "last_latency_ms",
        "last_seen",
    )

    def __init__(self) -> None:
        self.in_flight = 0
        self.in_flight_peak = 0
        self.good = 0
        self.bad = 0
        self.retries = 0
        self.latency = LatencyWindow(PER_BACKEND_WINDOW)
        self.last_status: Optional[int] = None
        self.last_latency_ms: Optional[float] = None
        self.last_seen: Optional[float] = None


class Metrics:
    """The whole tally board: per-helper counts, totals and recent changes."""

    def __init__(self) -> None:
        self.started_at = time.time()
        self.global_latency = LatencyWindow(GLOBAL_WINDOW)
        self._backends: Dict[str, BackendMetrics] = {}
        self._completions: Deque[float] = deque()
        self._retry_events: Deque[float] = deque()
        self._events: Deque[Dict[str, Any]] = deque(maxlen=EVENT_WINDOW)
        self._last_transitions: Dict[str, tuple] = {}
        self._orphan_errors = 0
        self._requests_started = 0

    # ------------------------------------------------------------------ #
    # Recording (called from the proxy, once per attempt)
    # ------------------------------------------------------------------ #
    def begin(self, backend) -> None:
        """A kid is now being served by this helper."""
        stats = self._for(backend)
        stats.in_flight += 1
        stats.in_flight_peak = max(stats.in_flight_peak, stats.in_flight)
        # pool.Backend keeps the live "waiting now" number too, because the
        # least-connections rule reads it from there.
        backend.counters["connections"] = stats.in_flight
        self._requests_started += 1

    def end(self, backend, ok: bool, latency_ms: float, status: Optional[int] = None) -> None:
        """The attempt is over - ALWAYS called, even when it broke."""
        stats = self._for(backend)
        stats.in_flight = max(0, stats.in_flight - 1)
        backend.counters["connections"] = stats.in_flight

        if ok:
            stats.good += 1
        else:
            stats.bad += 1

        stats.latency.add(latency_ms)
        self.global_latency.add(latency_ms)

        stats.last_status = status
        stats.last_latency_ms = round(latency_ms, 2)
        stats.last_seen = time.time()

        now = time.time()
        self._completions.append(now)
        self._prune(now)

    def note_retry(self, backend) -> None:
        """A safe ask is about to be tried again on a different helper."""
        self._for(backend).retries += 1
        self._retry_events.append(time.time())

    def note_no_backend(self) -> None:
        """Nobody was awake to take the ask - counted, not hidden."""
        self._orphan_errors += 1

    # ------------------------------------------------------------------ #
    # Snapshot (called by /stats)
    # ------------------------------------------------------------------ #
    def snapshot(self, pool, strategy: str, strategies: Dict[str, str]) -> Dict[str, Any]:
        """A tidy, slightly-mixed-at-the-edges view of the tally board.

        We do not freeze the world: on a single event loop no awaits happen
        inside this method, so the numbers are consistent enough to read.
        Taking a deep copy would buy nothing except a stale dashboard.
        """
        backends: List[Dict[str, Any]] = []
        total_turns = total_good = total_bad = total_in_flight = 0
        total_retries = total_skips = total_welcomes = 0

        now = time.time()
        self._record_health_changes(pool, now)

        for backend in pool.get_all_backends() if pool else []:
            stats = self._for(backend)
            turns = int(backend.counters.get("total_requests", 0))
            skips = int(getattr(backend, "unhealthy_transitions", 0))
            welcomes = int(getattr(backend, "healthy_transitions", 0))
            changed_at = getattr(backend, "status_changed_at", None)

            latency = stats.latency.summary()
            total_turns += turns
            total_good += stats.good
            total_bad += stats.bad
            total_in_flight += stats.in_flight
            total_retries += stats.retries
            total_skips += skips
            total_welcomes += welcomes

            backends.append(
                {
                    "name": backend.name,
                    "url": backend.url,
                    "alive": bool(getattr(backend, "is_alive", True)),
                    "turns": turns,
                    "good": stats.good,
                    "bad": stats.bad,
                    "retries": stats.retries,
                    "skips": skips,
                    "welcomes": welcomes,
                    "in_flight": stats.in_flight,
                    "in_flight_peak": stats.in_flight_peak,
                    "misses": int(getattr(backend, "consecutive_misses", 0)),
                    "wins": int(getattr(backend, "consecutive_wins", 0)),
                    "last_status": stats.last_status,
                    "last_latency_ms": stats.last_latency_ms,
                    "latency_ms": latency,
                    "status_changed_at": changed_at,
                    "down_for_seconds": (
                        round(now - changed_at, 1)
                        if (changed_at is not None and not getattr(backend, "is_alive", True))
                        else None
                    ),
                }
            )

        attempts = total_good + total_bad + self._orphan_errors
        error_rate = (total_bad + self._orphan_errors) / attempts if attempts else 0.0

        return {
            "now": datetime.now().isoformat(timespec="seconds"),
            "started_at": datetime.fromtimestamp(self.started_at).isoformat(timespec="seconds"),
            "uptime_seconds": round(now - self.started_at, 1),
            "strategy": {
                "active": strategy,
                "available": strategies,
            },
            "totals": {
                "requests": self._requests_started,
                "turns": total_turns,
                "good": total_good,
                "bad": total_bad,
                "unreached": self._orphan_errors,
                "error_rate": round(error_rate, 4),
                "in_flight": total_in_flight,
                "retries": total_retries,
                "retries_recent": len(self._retry_events),
                "skips": total_skips,
                "welcomes": total_welcomes,
                "rps": self._rps(now),
                "latency_ms": self.global_latency.summary(),
            },
            "backends": backends,
            "recent_events": list(reversed(self._events)),
        }

    # ------------------------------------------------------------------ #
    # Internals
    # ------------------------------------------------------------------ #
    def _for(self, backend) -> BackendMetrics:
        stats = self._backends.get(backend.name)
        if stats is None:
            stats = BackendMetrics()
            self._backends[backend.name] = stats
        return stats

    def _prune(self, now: float) -> None:
        cutoff = now - RPS_WINDOW_SECONDS
        while self._completions and self._completions[0] < cutoff:
            self._completions.popleft()

        retry_cutoff = now - RETRY_WINDOW_SECONDS
        while self._retry_events and self._retry_events[0] < retry_cutoff:
            self._retry_events.popleft()

    def _rps(self, now: float) -> float:
        self._prune(now)
        return round(len(self._completions) / RPS_WINDOW_SECONDS, 2)

    def _record_health_changes(self, pool, now: float) -> None:
        """Turn the cumulative skip/welcome counters into timestamped events.

        The health loop bumps those counters; we compare against the last
        values we saw so the window can show "buddy skipped at 12:00:03"
        without the health checker having to know about the dashboard.
        """
        for backend in pool.get_all_backends() if pool else []:
            skips = int(getattr(backend, "unhealthy_transitions", 0))
            welcomes = int(getattr(backend, "healthy_transitions", 0))
            previous = self._last_transitions.get(backend.name)

            if previous is None:
                # First look: remember the counters, invent no history.
                self._last_transitions[backend.name] = (skips, welcomes)
                continue

            old_skips, old_welcomes = previous
            if skips > old_skips:
                self._events.append(
                    {
                        "at": _clock(getattr(backend, "last_unhealthy_at", None) or now),
                        "kind": "skip",
                        "backend": backend.name,
                        "detail": "ejected from rotation",
                    }
                )
            if welcomes > old_welcomes:
                self._events.append(
                    {
                        "at": _clock(getattr(backend, "last_healthy_at", None) or now),
                        "kind": "welcome",
                        "backend": backend.name,
                        "detail": "back in rotation",
                    }
                )

            self._last_transitions[backend.name] = (skips, welcomes)


def _clock(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")


def _round(value: Optional[float]) -> Optional[float]:
    return None if value is None else round(value, 2)


# One tally board for the whole door. Imported by proxy.py and dashboard.py.
metrics = Metrics()
