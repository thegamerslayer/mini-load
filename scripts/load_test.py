"""
The many-kids machine (Step 6).

Sends a FIXED number of asks per second at the door, because "as fast as
possible" is not a number you can write down or compare later.

We drive httpx directly instead of Locust: httpx is already a dependency,
and a fixed rate is just "start ask i at i/rps seconds". Locust can replace
this in Step 8 if you want its pretty reports.

Examples
--------
    # 50 asks/second for 10 seconds, each helper napping 200ms
    python scripts/load_test.py --rps 50 --duration 10 --ms 200

    # prove the 3:1:1 weighted rule (DONE-5)
    python scripts/load_test.py --rps 50 --duration 20 --ms 20

    # POST ice-cream asks (never retried) instead of /work
    python scripts/load_test.py --method POST --path / --rps 20 --duration 5

The summary prints the client-side latency (what the kid waited), the status
spread, and how the turns were split between helpers.
"""

from __future__ import annotations

import argparse
import asyncio
import math
import sys
import time
from collections import Counter

import httpx


def percentile(sorted_values, p):
    if not sorted_values:
        return None
    if len(sorted_values) == 1:
        return sorted_values[0]
    rank = math.ceil((p / 100.0) * len(sorted_values)) - 1
    return sorted_values[max(0, min(rank, len(sorted_values) - 1))]


async def one_request(client, method, url, semaphore, timeout):
    """Send one ask, return (ok, status, backend, elapsed_ms)."""
    async with semaphore:
        started = time.perf_counter()
        try:
            response = await client.request(method, url, timeout=timeout)
            elapsed_ms = (time.perf_counter() - started) * 1000
        except httpx.HTTPError as exc:
            elapsed_ms = (time.perf_counter() - started) * 1000
            return False, type(exc).__name__, "-", elapsed_ms

        backend = "-"
        try:
            payload = response.json()
            if isinstance(payload, dict):
                backend = str(payload.get("backend", "-"))
        except ValueError:
            backend = "-"

        return response.is_success, str(response.status_code), backend, elapsed_ms


async def run(args) -> int:
    base = args.url.rstrip("/")
    path = args.path if args.path.startswith("/") else "/" + args.path
    url = base + path

    query = []
    if args.ms is not None and path.rstrip("/") != "/health":
        query.append(f"ms={args.ms}")
    if query:
        url += ("&" if "?" in url else "?") + "&".join(query)

    total = max(1, int(round(args.rps * args.duration)))
    interval = 1.0 / args.rps
    semaphore = asyncio.Semaphore(args.concurrency)

    print(f"many kids: {args.rps:.1f} asks/s for {args.duration:g}s -> {total} asks")
    print(f"door:      {args.method} {url}")
    print(f"limit:     {args.concurrency} in flight, {args.timeout:g}s timeout\n")

    limits = httpx.Limits(max_connections=args.concurrency, max_keepalive_connections=args.concurrency)

    async with httpx.AsyncClient(limits=limits) as client:
        started = time.perf_counter()
        tasks = []
        for index in range(total):
            target = started + index * interval
            delay = target - time.perf_counter()
            if delay > 0:
                await asyncio.sleep(delay)
            tasks.append(
                asyncio.create_task(
                    one_request(client, args.method, url, semaphore, args.timeout)
                )
            )

        results = await asyncio.gather(*tasks)
        wall = time.perf_counter() - started

    return report(results, wall, args)


def report(results, wall, args) -> int:
    latencies = sorted(result[3] for result in results)
    successes = [result for result in results if result[0]]
    failures = [result for result in results if not result[0]]
    statuses = Counter(result[1] for result in results)
    backends = Counter(result[2] for result in successes)

    print("-" * 68)
    print(f"{'asks sent':<22}{len(results):>10}")
    print(f"{'OK':<22}{len(successes):>10}")
    print(f"{'failed':<22}{len(failures):>10}")
    print(f"{'error rate':<22}{(len(failures) / len(results) * 100 if results else 0):>9.2f}%")
    print(f"{'achieved rate':<22}{len(results) / wall:>7.1f}/s")
    print(f"{'wall time':<22}{wall:>9.2f}s")
    print()
    print(f"{'p50':<22}{percentile(latencies, 50):>9.1f} ms")
    print(f"{'p95':<22}{percentile(latencies, 95):>9.1f} ms")
    print(f"{'p99':<22}{percentile(latencies, 99):>9.1f} ms")
    print(f"{'max':<22}{latencies[-1] if latencies else 0:>9.1f} ms")
    print()
    print("status spread")
    for status, count in sorted(statuses.items(), key=lambda item: -item[1]):
        print(f"  {status:<16}{count:>10}")
    print()
    print("turns per helper (successful asks only)")
    total_turns = sum(backends.values()) or 1
    for backend, count in backends.most_common():
        share = count / total_turns * 100
        bar = "#" * max(1, int(round(share / 4)))
        print(f"  {backend:<16}{count:>8}  {share:>5.1f}%  {bar}")
    print("-" * 68)

    if args.ms is not None:
        expected = percentile(latencies, 50) - args.ms
        print(f"reality check: median {percentile(latencies, 50):.1f} ms vs {args.ms} ms nap "
              f"({expected:+.1f} ms of door + queueing)")

    if failures:
        print("The tally board should show these too - open /ui and compare.")
        return 1
    return 0


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Fixed-rate load generator for the door helper.")
    parser.add_argument("--url", default="http://127.0.0.1:8080", help="door base URL")
    parser.add_argument("--path", default="/work", help="path to hit (default /work)")
    parser.add_argument("--method", default="GET", help="HTTP method (default GET)")
    parser.add_argument("--rps", type=float, default=20.0, help="asks per second (default 20)")
    parser.add_argument("--duration", type=float, default=10.0, help="seconds (default 10)")
    parser.add_argument("--ms", type=int, default=100, help="nap time for /work in ms (default 100; -1 to omit)")
    parser.add_argument("--concurrency", type=int, default=100, help="in-flight limit (default 100)")
    parser.add_argument("--timeout", type=float, default=10.0, help="per-ask timeout in seconds")
    args = parser.parse_args(argv)

    if args.rps <= 0:
        parser.error("--rps must be greater than 0")
    if args.duration <= 0:
        parser.error("--duration must be greater than 0")
    if args.concurrency < 1:
        parser.error("--concurrency must be at least 1")
    if args.ms is not None and args.ms < 0:
        args.ms = None
    return args


if __name__ == "__main__":
    try:
        sys.exit(asyncio.run(run(parse_args())))
    except KeyboardInterrupt:
        print("\nstopped")
        sys.exit(130)
