"""
Locust load-test rig (M6).

Fixed target RPS, not "as fast as possible" - DO7 compares p99 latency and
error rate BEFORE vs DURING a backend crash, so the offered load must be a
constant you chose and can write down.

TODO(M6): write the Locust user class here (locustfile).
  - target the LB on :8080, not the backends
  - mix GET /hello (or /) with GET /work?ms=... to create skew for DO4
  - run: locust -f scripts/load_test.py --headless -u <users> -r <rate> ...
  - record the numbers into docs/algorithm_notes.md and docs/chaos_log.md
"""
