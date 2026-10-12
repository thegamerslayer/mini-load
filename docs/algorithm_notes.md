# mini-load - Notes on the Choosing Rules

One short write-up per rule, **with your own numbers**. A claim here with no
number next to it is just a guess - write "guess" if it is one.

## take turns (round robin)

- What it is good at:
- Where it loses when one helper is slow:
- Many-kids note: what two kids see if the turn counter is a plain
  `int += 1`, and what you did about it.
- Measured split over 1000+ asks: `FILL ME IN`

## weighted, spread out (smooth weighted round robin)

- Copy the smooth weighted rule in BY HAND here first (Step 0 tells you to
  do this before Step 3).
- Why spreading the turns out beats "three in a row for the strong one":
- DONE-5 - 3:1:1 target, measured over 1000+ asks:

  | helper | weight | expected % | what I saw % | asks |
  | --- | --- | --- | --- | --- |
  | Sunny (server1) | 3 | 60 | | |
  | Buddy (server2) | 1 | 20 | | |
  | Rosie (server3) | 1 | 20 | | |

## fewest waiting (least connections)

- What it is good at:
- DONE-4 - one helper slow: "/work" nap 900ms on one helper, 50ms on the
  others. Same load, both rules, latency table:

  | rule | mean | middle | p95 | p99 | errors |
  | --- | --- | --- | --- | --- | --- |
  | take turns | | | | | |
  | fewest waiting | | | | | |

- Verdict, in one sentence you could say out loud:

## P2C (pick two by luck, keep the less busy)

- Why picking two by luck beats picking one by luck (the clever part):
- What it costs compared to "fewest waiting":

## Swapping the rule while running (DONE-8)

`FILL ME IN` - how the rule is changed without restarting, which button/URL,
and what the tally board shows right after.
