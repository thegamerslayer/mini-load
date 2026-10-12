# CATCH_UP.md — read this first after a break

> Written from a real audit of this repo on 2026-10-11 (not from memory).
> This file is a *handbook*, not a spec. It does not replace README_FIRST.md,
> ROADMAP.md or PROFESSOR.md — it gets you back to the point where those make
> sense again. Nothing in here is a substitute for the contract in PROFESSOR.md
> R1: the code in `src/` and `backends/` is written by YOU.

---

## 1. The project in 60 seconds

You are building a **reverse-proxy load balancer** by hand.

```
client ──► YOUR LB on :8080 ──► picks one backend ──► :8001 / :8002 / :8003
                │
                ├── strategy       (round robin, weighted, least-conn, P2C)
                ├── health checks  (are backends alive? background loop)
                ├── metrics        (who served what, how fast, p50/p95/p99)
                └── /stats + /ui   (the observability surface)
```

The backends are deliberately dumb (identity + `/health` + `/work`). **All the
interesting code lives in the LB.** That is the whole design: the parts that
make Nginx/HAProxy/cloud LBs interesting are the parts you write yourself, so
you can explain them in an interview instead of naming a product.

The demo that defines "done": *kill a backend during live traffic and traffic
keeps flowing — and you can point at the line of code that made that happen.*

---

## 2. The mental model: one request, end to end

This is DO10, and it is the single best way to re-load the project into your
head. Follow one GET through your own system:

| # | Step | Where it lives | Concept being learned |
| --- | --- | --- | --- |
| 1 | Client connects to `:8080` | uvicorn | socket accept, ASGI server |
| 2 | FastAPI matches a **catch-all route** | `src/app.py` (`api_route`) | routing, why one route covers all paths/methods |
| 3 | Strategy picks a backend | `src/strategies.py` | scheduling algorithms |
| 4 | Active-connection counter incremented | `src/pool.py` | in-flight tracking → least-connections |
| 5 | Request forwarded (method, path, query, headers, body) | `src/proxy.py` using httpx | reverse proxying, streaming, hop-by-hop headers |
| 6 | Backend answers | `backends/server.py` | the "dumb" peer |
| 7 | Response flows back, metrics recorded | `src/metrics.py` | observability |
| 8 | Counter decremented in `finally` | `src/pool.py` | why `finally` — exception safety |
| 9 | Background health loop, meanwhile, pings `/health` | `src/health.py` | proactive failure detection |
| 10 | `/stats` answers "who is up, who got traffic, how slow" | `src/dashboard.py` | the LB observing itself |

If you can retell that table from memory, you are caught up on the *shape*.
Everything else is detail.

---

## 3. Where you actually are — audited, with evidence

I ran your code. This is the truth, not the plan.

### Milestone status

| Milestone | Claimed | Actual |
| --- | --- | --- |
| M0 recon / architecture.md | — | **Not done.** `docs/architecture.md` is still the template with `TODO(M0)` in it. The three M0 questions are unanswered. |
| M1 three backends | — | **Mostly done.** `backends/server.py` runs and works (verified below). `/crash` is missing. |
| M2 dumb proxy | — | **Started, does not run.** `src/proxy.py` fails on import. `src/app.py` and `src/main.py` are empty (docstring only). |
| M3 strategies + tests | — | **Started.** `RoundRobinBalancer` exists. No tests. No lock. No healthy filtering. |
| M4–M9 | — | **Not started.** Empty stubs + templates. |

### What I verified by running it

Backend works (started on :8001 with `SERVER_NAME=server1`):

```
GET /              -> {"backend":"server1","port":8001,"delay_ms":0}   ✅
GET /health        -> {"status":"OK"}                                   ✅
GET /work?ms=300   -> 200, time_total=0.518s                            ⚠ see below
GET /crash?seconds=5 -> 404 NOT IMPLEMENTED                             ❌
```

That `/work?ms=300` took **0.52s, not 0.30s** — worth chasing as a warm-up/measurement
exercise (M1 checkpoint: "measures ~300ms"). Re-run it 5 times with `curl -w` and
see whether the first request is the slow one. That gap IS the lesson.

The LB half does not run at all:

```
$ python -c "import src.proxy"
ImportError: cannot import name 'round_robin' from 'src.strategies'

$ python -c "from src.config import load_config; print(load_config())"
(8080, [])      <-- backend list is EMPTY, and it should have 3 entries
```

### The three concrete things blocking you (concept first, no code)

**1. `src/proxy.py` imports a function that does not exist.**
`strategies.py` defines a *class* `RoundRobinBalancer` with a *method*
`round_robin`. `proxy.py` does `from src.strategies import round_robin`.
  - Concept: module-level function vs class method vs bound method.
  - Decide: do you want strategies as **functions taking a Pool** (simple) or
    **objects holding state like the RR cursor** (needed for smooth weighted RR,
    which carries `current_weight` per backend)? ROADMAP says
    `round_robin(pool) -> Backend`. Either is fine — but pick one and make the
    *interface* consistent across all four, because M3 requires "four algorithms
    behind one interface".
  - Read: Python docs on classes → "Class and Instance Variables".

**2. `src/config.py` reads env vars that were never loaded.**
`load_config()` uses `os.getenv("BACKENDS")`, but nobody called
`load_dotenv()` unless you happen to import `backends.server` first.
`backends/server.py` calls `load_dotenv()`; `src/config.py` does not.
  - Concept: **import side effects and initialisation order.** A module that
    reads config at import time inherits whatever state existed at that moment.
  - The deeper decision C7 forces: *who* loads `.env`, and *when*? One entry
    point that loads config once and passes it down beats every module doing
    its own `getenv`. Read python-dotenv README → `load_dotenv()` vs
    `dotenv_values()`.
  - Also: `.env` currently holds BOTH LB settings (`LB_PORT`, `BACKENDS`) and
    backend settings (`SERVER_NAME=server2`, `SERVER_PORT=8002`). Two roles in
    one file means whichever process starts first wins the ambiguous ones.
    Write down one sentence in `BUILD_LOG.md` about how you will keep them
    separate.

**3. There is no app to run.** `src/app.py` and `src/main.py` are empty, so
`run.py` at the project root currently starts a **backend** (it imports
`backends.server`), not the load balancer:
```
$ python -c "import backends.server as s; print(s.SERVER_PORT)" -> 8002
```
  - Concept: entry points. ROADMAP allots `src/main.py` to the LB CLI and
    `backends/server.py` to the backend. Two processes, two entry points.
  - Read: FastAPI "First Steps" + uvicorn docs on `uvicorn.run` programmatically.

### Smaller drifts I noticed (record them, don't fix them all today)

- `strategies.py`: the RR counter `total_requests` is bumped **inside** the
  strategy. Metrics leaking into scheduling — M6 will want counters in one
  place. Note it for M3.
- `strategies.py`: `itertools.cycle(backends)` is built in `__init__` and the
  pool list cannot update it. I verified the exact behaviour (see §3 note
  below) — it is subtler than "it takes a snapshot":
  - items appended while the cycle is still on its first live pass ARE picked
    up;
  - items appended after the underlying iterator first runs out are NEVER
    picked up;
  - **items REMOVED from the pool list are still handed out forever** — after
    `pool.remove('B')`, the cycle kept returning `B` across 30+ picks.

  So the M5 hazard is real and worse than a frozen snapshot: an *ejected*
  backend stays in the rotation until the object is rebuilt. M3's trap about
  "strategies return only HEALTHY backends" points exactly here. Working out
  *why* this happens is a genuinely good exercise — read the `itertools.cycle`
  docs, then predict all three cases above before you run them.
- `strategies.py`: no `asyncio.Lock` / atomic pattern yet — that is the M3
  concurrency bug the roadmap wants you to *feel* first. Don't fix it before
  you can explain the interleaving.
- `pool.py`: `Backend`/`Pool` have no health state and no active-connection
  count. Both are M3/M5 work, and the file is shaped to receive them.
- `tests/`: no `__init__.py`, and all three test files are TODO templates.
- **No git repo.** `git log` says *not a git repository*. PROFESSOR.md Part 2
  says "commit after each slice", and YOUR OWN rule ("never delete a row")
  needs version history. `git init` here is arguably the highest-value 30
  seconds available to you.

---

## 4. Is this a good project to learn backend from? Yes — here is why

Your worry is "I've always had AI write it, so I never learned it." This project
is unusually good for fixing that, for four reasons:

1. **It has a written contract that forbids the AI from writing `src/`**
   (PROFESSOR.md R1–R4). That is the exact discipline you said you were missing.
   Honour it and it works; break it and this becomes another tutorial you watched.
2. **It has a failure curriculum.** `docs/chaos_log.md` says: kill a backend,
   send a huge body, flap a server. Backend engineering is mostly the study of
   what happens when the happy path stops — most tutorials hide that part.
3. **Every concept has a checkpoint with numbers.** "30/30 requests, zero
   failures, ejected at t+3.2s" beats "it works". Numbers are what make a claim
   interview-proof.
4. **It is genuinely the small version of a real product.** Reverse proxy,
   health checking, weighted scheduling, observability, graceful drain,
   autoscaling — this is the vocabulary of every backend/infra interview, and
   you will have *built* each piece rather than read about it.

The one caveat: what this project teaches **less** well is *data* backend work —
databases, schema design, transactions, caching layers, auth. It teaches the
**traffic/infrastructure half** of backend. That is a real half, and it is the
half most courses skip. Plan a second small project later for the data half.

---

## 5. Your next three sessions (concrete, in order)

**Session A — clean the deck (30–45 min, mostly non-code)**
1. `git init` + first commit. Add a `.gitignore` check (it already ignores
   `venv/` and `.env` — good).
2. Open `BUILD_LOG.md` and write a real session row: date, `M1/M2`, and the
   three bugs from §3 written as YOUR diagnosis. The FDI columns are the point
   of that file — fill them honestly. Right now: `backends/server.py` is
   probably DRIFTING ("works, cannot explain why"), and everything else IGNORED.
3. Answer the four M0 questions in `docs/architecture.md` (proxy vs reverse
   proxy, L4 vs L7, hop-by-hop vs end-to-end, what each algorithm optimises).
   No code this session. It is the cheapest 45 minutes in the project.

**Session B — make M1 honest (1–2 h)**
1. Add `/crash?seconds=N` to `backends/server.py` (make `/health` hang, process
   stays alive). It is your failure injector for every later demo — you cannot
   do M5 without it.
2. Chase the `/work?ms=300 -> 0.52s` gap, 5 timed runs, write the numbers down.
3. Run all three backends on one screen and `curl` each one's identity.

**Session C — make M2 run (2 h)**
1. Fix the `proxy.py` / `strategies.py` interface mismatch (§3.1) — pick
   functions or objects, then commit to it for all four algorithms.
2. Fix the config loading order (§3.2) and prove it:
   `python -c "from src.config import load_config; print(load_config())"` must
   print 3 backend URLs.
3. Write `src/app.py` with ONE catch-all `@app.api_route` and wire it to
   `forward()`. Then `curl localhost:8080/hello` five times and watch 1-2-3-1-2.
4. That first rotating response is the moment the project stops being a
   document and starts being yours. Commit it.

---

## 6. Self-quiz (do this before you read the docs again)

Answer out loud. If any takes more than one sentence of hesitation, that is
your next reading assignment.

- What is the difference between a (forward) proxy and a reverse proxy? Which
  one are you building, and how would a client notice?
- L4 vs L7 load balancing — which are you, and what do you therefore see and
  never see of the request?
- Why is `POST` dangerous to retry but `GET` is not? (Answer in one sentence —
  it is RFC 9110 §9.2.1, and it is part of DO6.)
- Which HTTP headers are hop-by-hop and must NOT be forwarded? Name two.
- Why does the active-connection decrement have to be in a `finally`?
- If `await request.body()` is wrong for a proxy, what is right and why?
- What does "smooth" weighted round robin fix compared to "3 of A, then 1 of B"?
- Why does health checking need *consecutive* failures rather than one?

---

## 7. Where the given documentation is

| File | What it is | Status |
| --- | --- | --- |
| `README_FIRST.md` | The spec: mission, constraints C1–C9, definition of done DO1–DO10 | given — read once fully |
| `ROADMAP.md` | M0–M9 with READ FIRST / CHECKPOINT / TRAPS per milestone | given — your map |
| `PROFESSOR.md` | Rules of engagement: the escalation ladder, the session loop | given — this is the contract |
| `HOW_TO_SEARCH_DOCS.md` | How to find answers in official docs (site: searches, reading signatures) | given — the meta-skill |
| `BUILD_LOG.md` | Your session log + FDI (Frozen/Drifting/Ignored) | **only session 00 — fill it in** |
| `docs/architecture.md` | Diagram + decisions + run commands | template, all TODO |
| `docs/algorithm_notes.md` | Per-algorithm write-ups + measurements | template, all TODO |
| `docs/chaos_log.md` | Every injected failure + timeline | template, empty |
| `tests/*.py` | Test specifications in docstrings | templates, no assertions |
| `scripts/load_test.py`, `static/dashboard.html` | M6 rig + dashboard | templates |

---

## 8. One rule to carry forward

When you hit the next wall: **make it fail on demand first, then bring the
error, the smallest repro, the doc section you read, and the experiment you
ran.** PROFESSOR.md Part 3 is the ladder. The AI is rung 5, for naming the
concept and pointing at the page — never for handing over `src/`.

Grading yourself with the FDI row each session is what turns this from
"a project that runs" into "a project you own".
