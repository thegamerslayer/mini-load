# mini-load - Chaos Log

Every failure you inject, and what actually happened. Written **during** the
run, with real timestamps - a reconstructed timeline is fiction.

Rule: one row per injection, plus a short narrative underneath. "Zero
client-visible failures" is only believable with the exact timeline next to it.

| # | date/time | what I did | what I expected | what happened | client-visible impact | time to eject | time to re-admit |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | | `docker stop` server2 / `/crash?seconds=60` | | | | | |

## Narrative template

```
INJECTION  <what, when, against which backend>
T+0s       request loop running at <rate>, errors: 0
T+?
T+?        /stats shows backend ejected
T+?        injection removed
T+?        /stats shows backend re-admitted
VERDICT    client-visible errors during window:
```

## Still to inject (README_FIRST DO3, DO7)

- [ ] kill backend 2 mid-traffic, GET-only load: zero client-visible failures
- [ ] same window, POST load: confirm the POST failures are NOT retried (DO6)
- [ ] slow backend (900ms) rather than dead backend - which algorithm copes
- [ ] backend that fails then recovers, to capture eject -> re-admit timing
- [ ] Locust before vs during crash, p99 + error rate (DO7)
