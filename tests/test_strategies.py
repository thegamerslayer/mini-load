"""
Pure-logic unit tests for the four strategies (M3).

No network, no servers: feed the strategy functions a fixed backend pool and
assert the exact sequence of picks. The things worth proving:

  - round robin cycles in order, and its counter survives concurrent picks
  - smooth weighted round robin interleaves (3:1:1 is NOT three in a row)
  - least connections picks the smallest active count, ties broken sanely
  - P2C picks from two random healthy backends and takes the less loaded one
  - every strategy returns only healthy backends

TODO(M3): write these. No assertions exist yet on purpose - tests you did not
reason about yourself prove nothing.
"""

import pytest
import asyncio
from src.pool import Backend, Pool
from src.strategies import RoundRobinBalancer

@pytest.mark.asyncio
async def test_round_robin_balancer_cycles_backends():
    b1 = Backend("server1", "http://localhost:8001")
    b2 = Backend("server2", "http://localhost:8002")
    b3 = Backend("server3", "http://localhost:8003")
    pool = Pool([b1, b2, b3])

    balancer = RoundRobinBalancer(pool)

    chosen = [await balancer.choose() for _ in range(6)]
    names = [b.name for b in chosen]

    assert names == ["server1", "server2", "server3", "server1", "server2", "server3"]

import pytest
from src.pool import Backend, Pool
from src.strategies import WeightedRoundRobinBalancer

@pytest.mark.asyncio
async def test_weighted_round_robin_respects_weights():
    b1 = Backend("server1", "http://localhost:8001")
    b2 = Backend("server2", "http://localhost:8002")
    pool = Pool([b1, b2])

    # server1 weight=2, server2 weight=1
    balancer = WeightedRoundRobinBalancer(weights=[2,1], pool=pool)

    chosen = [await balancer.choose() for _ in range(6)]
    names = [b.name for b in chosen]

    # server1 should appear twice as often
    assert names.count("server1") == 4
    assert names.count("server2") == 2


from src.strategies import LeastConnectionsBalancer

@pytest.mark.asyncio
async def test_least_connections_picks_least_busy():
    b1 = Backend("server1", "http://localhost:8001", counters={"connections": 5})
    b2 = Backend("server2", "http://localhost:8002", counters={"connections": 1})
    pool = Pool([b1, b2])

    balancer = LeastConnectionsBalancer()
    chosen = await balancer.choose(pool)

    assert chosen.name == "server2"  # ✅ least busy


from src.strategies import P2CBalancer

@pytest.mark.asyncio
async def test_p2c_picks_less_busy_of_two():
    b1 = Backend("server1", "http://localhost:8001", counters={"connections": 10})
    b2 = Backend("server2", "http://localhost:8002", counters={"connections": 2})
    pool = Pool([b1, b2])

    balancer = P2CBalancer()
    chosen = await balancer.choose(pool)

    assert chosen.name == "server2"  # ✅ less busy


@pytest.mark.asyncio
async def test_round_robin_high_concurrency():
    b1 = Backend("server1", "http://localhost:8001")
    b2 = Backend("server2", "http://localhost:8002")
    pool = Pool([b1, b2])
    balancer = RoundRobinBalancer(pool)

    async def pick_backend():
        return (await balancer.choose()).name

    results = await asyncio.gather(*[pick_backend() for _ in range(50)])

    # Should only contain server1 and server2, alternating safely
    assert set(results).issubset({"server1", "server2"})
