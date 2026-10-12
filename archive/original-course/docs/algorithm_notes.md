# mini-load - Algorithm Notes

Per-algorithm write-ups **with your own test results**. A claim here without a
measurement attached is a guess; label it as one.

## round_robin

- What it optimises for:
- Weakness under skewed backend cost:
- Concurrency note: what two simultaneous requests see if the counter is a
  plain `int += 1`, and what you did about it.
- Measured split over >= 1000 requests: `TODO`

## weighted_round_robin (smooth)

- The smooth weighted round robin algorithm, copied BY HAND into your notes
  first (ROADMAP M0 tells you to do this before M3).
- Why smooth interleaving beats "three in a row":
- DO5 - 3:1:1 target split, measured over >= 1000 requests:

  | backend | weight | expected % | observed % | requests |
  | --- | --- | --- | --- | --- |
  | server1 | 3 | 60 | | |
  | server2 | 1 | 20 | | |
  | server3 | 1 | 20 | | |

## least_connections

- What it optimises for:
- DO4 - skewed load: `/work` delay 900ms on one backend, 50ms on the others.
  Same offered load, both algorithms, latency table:

  | algorithm | mean | p50 | p95 | p99 | errors |
  | --- | --- | --- | --- | --- | --- |
  | round_robin | | | | | |
  | least_connections | | | | | |

- Verdict, in one sentence you could say in an interview:

## p2c (power of two choices)

- Why two random picks beats one random pick (the instructive part):
- What it costs versus least connections:

## Runtime switching (DO8)

`TODO` - how the strategy is changed without a restart, which endpoint, and
what `/stats` shows immediately afterwards.
