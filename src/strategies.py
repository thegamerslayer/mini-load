"""
Strategies module: Round robin, weighted round robin, least connections, P2C.

Step 6 adds ``StrategyManager``: all four rules live behind one plug, and the
dashboard can swap the active rule by changing ONE name. On a single event
loop that assignment is atomic - a request in flight keeps the rule it
started with, the next request uses the new one, and nobody is dropped.

Every rule hands out AWAKE helpers only. If everyone is asleep it returns
None and the door answers a clean "everyone is busy, sorry" (503).
"""

import asyncio
import random
from typing import List, Optional

from src.config import get_strategy_config
from src.pool import Backend, Pool

STRATEGY_LABELS = {
    "round_robin": "Round robin - take turns",
    "weighted_round_robin": "Weighted - smooth 3:1:1",
    "least_connections": "Least connections - shortest line",
    "p2c": "Power of two choices",
}


def _alive(backends: List[Backend]) -> List[Backend]:
    return [backend for backend in backends if getattr(backend, "is_alive", True)]


def _count_turn(backend: Backend) -> Backend:
    backend.counters["total_requests"] = backend.counters.get("total_requests", 0) + 1
    return backend


class RoundRobinBalancer:
    def __init__(self, pool: Optional[Pool] = None):
        self.pool = pool
        self._index = 0
        self.lock = asyncio.Lock()

    async def choose(self, pool: Optional[Pool] = None) -> Optional[Backend]:
        async with self.lock:
            if pool is not None:
                self.pool = pool
            if self.pool is None:
                return None

            backends = _alive(self.pool.get_all_backends())
            if not backends:
                return None

            backend = backends[self._index % len(backends)]
            self._index += 1
            return _count_turn(backend)


class WeightedRoundRobinBalancer:
    """Smooth weighted round robin (the nginx trick).

    Each helper keeps a running score: add its weight, pick the highest
    score, then take the total weight away from the winner. That spreads a
    3:1:1 split out instead of dealing three turns in a row.
    """

    def __init__(self, weights: Optional[List[float]] = None, pool: Optional[Pool] = None):
        self.pool = pool
        self.weights = list(weights) if weights else []
        self._current: dict[int, float] = {}
        self.lock = asyncio.Lock()

    def _weight_for(self, index: int) -> float:
        if index < len(self.weights):
            return max(0.0, float(self.weights[index]))
        return 1.0

    async def choose(self, pool: Optional[Pool] = None) -> Optional[Backend]:
        async with self.lock:
            if pool is not None:
                self.pool = pool
            if self.pool is None:
                return None

            backends = self.pool.get_all_backends()
            indexes = [i for i, backend in enumerate(backends) if getattr(backend, "is_alive", True)]
            if not indexes:
                return None

            total_weight = 0.0
            best_index = None
            best_score = None

            for index in indexes:
                weight = self._weight_for(index)
                score = self._current.get(index, 0.0) + weight
                self._current[index] = score
                total_weight += weight
                if best_score is None or score > best_score:
                    best_index, best_score = index, score

            # Forget scores for helpers that are asleep / gone, so they do not
            # come back with a stale advantage.
            for index in list(self._current):
                if index not in indexes:
                    self._current.pop(index, None)

            if best_index is None or total_weight <= 0:
                return None

            self._current[best_index] = best_score - total_weight
            return _count_turn(backends[best_index])


class LeastConnectionsBalancer:
    async def choose(self, pool: Pool) -> Optional[Backend]:
        if not pool or not pool.get_all_backends():
            return None
        backends = _alive(pool.get_all_backends())
        if not backends:
            return None
        backend = min(backends, key=lambda b: b.counters.get("connections", 0))
        return _count_turn(backend)


class P2CBalancer:
    async def choose(self, pool: Pool) -> Optional[Backend]:
        if not pool or not pool.get_all_backends():
            return None
        backends = _alive(pool.get_all_backends())
        if not backends:
            return None
        if len(backends) == 1:
            return _count_turn(backends[0])

        first, second = random.sample(backends, 2)
        chosen = (
            first
            if first.counters.get("connections", 0) <= second.counters.get("connections", 0)
            else second
        )
        return _count_turn(chosen)


class StrategyManager:
    """One plug, four shapes. Swap ``active`` while the door is running."""

    def __init__(self, name: str = "round_robin", weights: Optional[List[float]] = None):
        self._balancers = {
            "round_robin": RoundRobinBalancer(),
            "weighted_round_robin": WeightedRoundRobinBalancer(weights),
            "least_connections": LeastConnectionsBalancer(),
            "p2c": P2CBalancer(),
        }
        self.active = name if name in self._balancers else "round_robin"

    @property
    def names(self) -> List[str]:
        return list(self._balancers)

    async def choose(self, pool: Pool) -> Optional[Backend]:
        # Read the name once: this request uses the rule it started with,
        # even if the dashboard swaps it during the await below.
        balancer = self._balancers[self.active]
        return await balancer.choose(pool)

    def set_strategy(self, name: str) -> str:
        if name not in self._balancers:
            raise ValueError(f"unknown strategy: {name}")
        self.active = name
        return self.active


manager = StrategyManager(*get_strategy_config())
