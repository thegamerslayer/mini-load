"""
Health-checker tests (M5).

Use short intervals or a fake clock - never sleep 5 real seconds in a test.

  - N consecutive failures ejects a backend; a single blip does not (flap
    damping - write down why in docs/architecture.md)
  - M consecutive successes re-admits it
  - the check timeout is shorter than the interval, and a timeout counts as a
    failure, not a hang
  - ejections and re-admissions are logged and counted

TODO(M5): write these.
"""
