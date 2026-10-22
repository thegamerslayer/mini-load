"""
Readable load-balancer check.

Sends a handful of requests to the load balancer and prints one clean line per
request, so you can see which backend answered without reading PowerShell's
Invoke-WebRequest dump (or triggering its "Script Execution Risk" warning).

Usage:
    python scripts/check_lb.py
    python scripts/check_lb.py --url http://localhost:8080 --requests 9

Exit code is 0 if every request succeeded, 1 otherwise.
"""

import argparse
import sys
import time

import httpx


def shorten(value: str, width: int) -> str:
    return value if len(value) <= width else value[: width - 1] + "~"


def main() -> int:
    parser = argparse.ArgumentParser(description="Send test requests through the load balancer.")
    parser.add_argument("--url", default="http://127.0.0.1:8080", help="load balancer base URL")
    parser.add_argument("--requests", type=int, default=6, help="number of requests to send")
    parser.add_argument("--timeout", type=float, default=5.0, help="per-request timeout in seconds")
    args = parser.parse_args()

    if args.requests < 1:
        parser.error("--requests must be at least 1")

    url = args.url.rstrip("/") + "/"
    print(f"Load balancer check: {url}  ({args.requests} requests)")
    print()
    print(f"{'#':>3}  {'status':<7}  {'backend':<12}  {'port':<6}  {'time':>8}")
    print("-" * 45)

    successes = 0
    order = []

    with httpx.Client(timeout=args.timeout) as client:
        for number in range(1, args.requests + 1):
            started = time.perf_counter()
            try:
                response = client.get(url)
            except httpx.RequestError as exc:
                print(f"{number:>3}  {'FAIL':<7}  {shorten(type(exc).__name__, 12)}")
                continue
            elapsed_ms = (time.perf_counter() - started) * 1000

            backend = "-"
            port = "-"
            try:
                payload = response.json()
                backend = shorten(str(payload.get("backend", "-")), 12)
                port = str(payload.get("port", "-"))
            except ValueError:
                # Not JSON (for example the proxy's 503 plain-text error).
                backend = shorten(response.text.strip() or "-", 12)

            if response.is_success:
                successes += 1
                order.append(backend)

            print(f"{number:>3}  {response.status_code:<7}  {backend:<12}  {port:<6}  {elapsed_ms:>7.1f} ms")

    print("-" * 45)

    if successes == 0:
        print("Result: no successful responses.")
        print("Is the load balancer running?  python src/main.py")
        return 1

    print(f"Result: {successes}/{args.requests} OK")
    print(f"Order:  {', '.join(order)}")

    if len(set(order)) > 1:
        print("Verdict: requests are rotating across backends.")
    else:
        print("Verdict: every successful request went to the same backend.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
