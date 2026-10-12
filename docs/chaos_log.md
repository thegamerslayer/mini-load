# mini-load - The Break-It Log

Every time you break something ON PURPOSE, and what really happened. Write
it **while** you run it, with real clock times - a made-up timeline is a
story, not a record.

Rule: one row per break, plus a short story underneath. "Zero kids saw a
problem" is only believable with the exact clock times next to it.

| # | date/time | what I did | what I expected | what happened | did any kid notice? | time to skip | time to welcome back |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | | turn Buddy off / `/crash?seconds=60` | | | | | |

## Story template

```
BREAK      <what I did, when, against which helper>
T+0s       kids asking at <rate>, problems: 0
T+few s
T+few s    tally board shows the helper skipped
T+few s    I fixed it
T+few s    tally board shows the helper welcomed back
VERDICT    kids who noticed during the window:
```

## Still to break (README DONE-3, DONE-7)

- [ ] turn Buddy off mid-traffic, safe asks only: zero kids notice
- [ ] same window, ice-cream asks: confirm they are NOT asked twice (DONE-6)
- [ ] a SLOW helper (900ms) instead of a dead one - which rule copes?
- [ ] a helper that breaks then wakes, to catch skip -> welcome timing
- [ ] many kids before vs during a break: slow-tail time + error rate (DONE-7)
