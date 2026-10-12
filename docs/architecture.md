# mini-load - How it is built

> This page belongs to YOU. It is not decoration: DONE-1 says *every command
> to run every step* is written here, and Step 0 says the ask-path drawing
> goes here BEFORE any code is written.

## 1. How an ask travels (Step 0)

Draw the trip of one ask, from the front door to the answer back, naming
every step it passes through. Hand-drawn or with slashes and dashes is fine.

```
KID -> DOOR :8080 -> [ choose | carry | tally ] -> helper :800x
```

FILL ME IN (Step 0): replace this squiggle with your own drawing. You must
be able to redraw it from memory (DONE-10).

## 2. Choices I made, and why

| Decision | My choice | Why, in my words |
| --- | --- | --- |
| FastAPI or Starlette | | requirements.txt asks for one sentence |
| httpx "real connection" or "pretend app" | | Step 2 asks for this write-up |
| hop-by-hop headers | | RFC 9110/9112 - which ones, and where I remove them |
| body handling | | in pieces, not all at once: say where the bytes sit at each hop |
| keep-alive: who closes it | | which side closes, and why it matters |
| how I remember "how fast" | | small memory: which trick, why, and what it costs |
| flaky-helper damping | | why "misses in a row" is enough (README Part 4) |

## 3. What happens when things break

- Safe asks (GET/HEAD/PUT/DELETE): asked again ONCE on a different helper.
- Ice-cream asks (POST): NEVER asked again by itself - the first ask may
  already have done something (RULE 6). Write that one sentence here,
  word for word. It is part of DONE-6.

## 4. Finding friends by name (Step 7 and later)

Write this sentence, in these words, in this file:

> Helpers are reached by the box's NAME, not by a hardcoded house address -
> that is how friends find each other inside boxes.

## 5. How to run everything (DONE-1)

Every command for every step goes here, starting from a friend copying your
project. Nothing may live only in your own little window.

```bash
# FILL ME IN (Step 1) my computer: three helpers
# FILL ME IN (Step 1) my computer: the door
# FILL ME IN (Step 2) ask-command proof that all three helpers take turns
# FILL ME IN (Step 7) one command to start the boxes
# FILL ME IN (Step 6) the many-kids machine
```
