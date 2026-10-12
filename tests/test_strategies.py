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
