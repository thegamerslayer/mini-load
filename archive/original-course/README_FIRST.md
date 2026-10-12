================================================================================
  MINI-LOAD - PROJECT BRIEF
  A lightweight distributed load balancer, built from scratch.
  No Nginx. No HAProxy. No Kubernetes. No cloud. No AI-written code.
  You write every line of src/. I hand you the spec, the docs, and the
  checkpoints - like a professor who sets the assignment and then sits down
  beside you and waits.
================================================================================

>>> START HERE: read this whole file once (20 min), then open ROADMAP.md and
>>> do M0. Do not write code until you have finished M0.

--------------------------------------------------------------------------------
  PART 1: THE MISSION
--------------------------------------------------------------------------------

Build a reverse-proxy load balancer that stands between clients and N backend
servers, and answer with facts: who got each request, how long it took, which
servers are alive right now, and what happened when one died mid-traffic.

At the end, you can kill a backend during a live demo and traffic keeps
flowing - and you can explain, line by line, the code that made that happen.

WHAT THIS PROJECT IS ACTUALLY TEACHING (in interview words)
  reverse proxying and streaming | async concurrency | scheduling algorithms
  health checking and failure detection | active connections tracking
  graceful retry and idempotency (GET vs POST) | observability and metrics
  containerisation and service discovery | load testing under target load

--------------------------------------------------------------------------------
  PART 2: THE CONSTRAINTS (do not negotiate with yourself)
--------------------------------------------------------------------------------

C1. Stack is Python + FastAPI + httpx. Nothing else does the work.
    No nginx, no HAProxy, no Traefik, no cloud load balancers, and no
    ready-made proxy middleware. You are building the small version of the
    thing Nginx does so you understand what it does for you.

C2. The load balancer is a reverse PROXY, not a redirect.
    Clients connect to your LB port; your LB forwards the request to a
    backend and returns the backend's response (status, headers, body)
    as if it were its own. A 302 round-trip would be a toy.

C3. Backends are dumb on purpose.
    Each backend serves /, /health, and /work (a configurable delay endpoint
    for load testing) and reports its own identity. No business logic. The
    interesting code all lives in the LB.

C4. Health checking is proactive, not reactive.
    A background task pings every backend's /health on an interval. When a
    backend fails N consecutive checks it is ejected; when it passes again
    it is re-admitted. Do not discover death only when a client request
    fails - real LBs check independently of traffic.

C5. Every request is measured or it did not happen.
    Per-backend: requests, successes, failures, avg/min/max latency, active
    connections, ejection count. LB-wide: totals and algorithm in use.
    Metrics are collected in code, served from one /stats endpoint.

C6. Retries only on idempotent methods, and only on connection errors.
    GET/HEAD/PUT/DELETE may be retried once on a different backend.
    POST must NEVER be auto-retried (the first attempt may have committed
    something). Document this rule in code where you implement it.

C7. Configuration comes from environment variables and a --strategy CLI flag.
    Nothing about the topology (ports, weights, intervals, thresholds) is
    hardcoded. .env is git-ignored; .env.example is committed.

C8. AI writes none of src/. See PROFESSOR.md for the exact contract and what
    you must do before you ask for help.

C9. One backend container, one process. In Phase 7+, scaling = changing one
    number in Docker Compose, which is exactly what you are demonstrating.

--------------------------------------------------------------------------------
  PART 3: THE SHAPE OF THE SYSTEM
--------------------------------------------------------------------------------

                         CLIENT (browser, curl, Locust)
                            |
                            v
                  +------------------+
                  |  LOAD BALANCER   |   :8080
                  |  src/ (you)      |
                  |  - strategy pick |
                  |  - proxy forward |
                  |  - health checks |
                  |  - metrics       |
                  |  - /stats, /ui   |
                  +--------+---------+
             +------------+------------+
             v            v            v
        +---------+  +---------+  +---------+
        | server1 |  | server2 |  | server3 |
        |  :8001  |  |  :8002  |  |  :8003  |
        +---------+  +---------+  +---------+

Everything from the client onward is your code (except Docker in phase 7).

--------------------------------------------------------------------------------
  PART 4: HARD REQUIREMENTS PER COMPONENT
--------------------------------------------------------------------------------

THE PROXY (src/proxy.py)
  - Forward method, path, query string, headers, and body to the chosen
    backend. Hop-by-hop headers must be handled (read the RFC section).
  - Stream request and response bodies - do not buffer whole bodies in
    memory. Find the httpx section on streaming.
  - Every request carries an X-Request-ID; if the client did not send one,
    the LB generates it. The response includes which backend served it.
  - If the chosen backend is dead/unreachable: one retry on another backend
    for idempotent methods only (C6); otherwise 502/503 with a clean JSON
    error body. Never a raw traceback.

THE STRATEGIES (src/strategies.py)
  - Round robin (with the counter made safe under concurrency - think about
    what two simultaneous requests see if the counter is a plain int += 1).
  - Weighted round robin (smooth weighted interleaving, not 3-in-a-row;
    research the "smooth weighted round robin" algorithm nginx uses).
  - Least connections (active in-flight request count per backend).
  - P2C (power of two choices): pick two random healthy backends, forward to
    the less-loaded one. Fewer lines than you expect, very instructive.
  - All strategies return only HEALTHY backends. Strategy is swappable at
    runtime via an endpoint or env var - no restart to change strategy.

THE HEALTH CHECKER (src/health.py)
  - One asyncio background task looping over backends, calling GET /health
    with a timeout shorter than your interval.
  - Configurable: interval, timeout, consecutive failures to eject,
    consecutive successes to re-admit. Flap damping comes free with the
    consecutive-failures rule; write down why in docs/.
  - Ejections and re-admissions are logged and counted, not silent.

THE METRICS (src/metrics.py)
  - Thread-safe/async-safe counters and latency percentiles (at least p50,
    p95, p99) per backend. Decide and document how you compute percentiles
    from a bounded reservoir - you do not keep every latency forever.
  - /stats returns the full picture as JSON. If a scrape endpoint cannot
    answer questions about its own health, it is decoration.

THE DASHBOARD (src/dashboard.py + static/)
  - Server-rendered or tiny-HTML dashboard polling /stats every second.
  - Shows per-backend status, request counts, RPS, latencies, and lets you
    switch algorithm without restarting. No JS frameworks. One HTML file.

THE BACKENDS (backends/)
  - One FastAPI app, parameterised by env: name, port, /work delay in ms.
  - /health returns 200 in under 50ms and says nothing interesting.
  - /work sleeps the configured delay then returns 200 (load-test target).
  - A /crash?seconds=N endpoint that makes the app stop responding for N
    seconds without the process dying (for demos). Implement it by making
    the health endpoint hang, and document exactly what it does.

DOCKER (phase 7+)
  - One Dockerfile (parameterised by command), one docker-compose.yml with
    lb + 3 backends on one user-defined network. Backends are reached by
    service name - that is service discovery, and it replaces hardcoded
    localhost ports. Say this sentence in docs/architecture.md.

--------------------------------------------------------------------------------
  PART 5: TARGET FILE TREE (yours to create in M1)
--------------------------------------------------------------------------------

  mini-load/
    README_FIRST.md          <- this brief (given)
    ROADMAP.md               <- milestones + docs to read (given)
    PROFESSOR.md             <- the rules of engagement (given)
    HOW_TO_SEARCH_DOCS.md    <- the doc-search method (given)
    BUILD_LOG.md             <- your progress log (you fill it)
    requirements.txt         <- dependency shopping list (given, commented)
    .env.example             <- committed
    .env                     <- ignored
    src/
      __init__.py
      config.py              <- env parsing, backend list, tunables
      pool.py                <- Backend class + the healthy/backend pool
      strategies.py          <- the four algorithms
      health.py              <- the background health-check loop
      metrics.py             <- counters, latency reservoirs, percentiles
      proxy.py               <- the request-forwarding core
      dashboard.py           <- /stats, /ui, strategy-switch endpoints
      app.py                 <- FastAPI wiring + lifespan (start health loop)
      main.py                <- CLI entry: uvicorn factory, args
    backends/
      __init__.py
      server.py              <- the dumb backend (one file, env-driven)
    static/
      dashboard.html         <- single-page dashboard (M6)
    tests/
      test_strategies.py     <- pure-logic unit tests (M3)
      test_proxy.py          <- against running backends (M4)
      test_health.py         <- fake-clock or short intervals (M5)
    docs/
      architecture.md        <- your diagram + decisions + why
      algorithm_notes.md     <- per-algorithm write-ups with your test results
      chaos_log.md           <- every failure you injected and what happened
    scripts/
      load_test.py           <- locust file (M6)

You may change the shape; if you do, say why in BUILD_LOG.md.

--------------------------------------------------------------------------------
  PART 6: DEFINITION OF DONE
--------------------------------------------------------------------------------

The project is finished when ALL of these are true. Not "mostly".

  DO1  From a clean checkout: docker compose up -d brings up LB + 3 backends;
       every command to run every phase is documented in docs/architecture.md.
  DO2  curl localhost:8080/hello in a loop shows all three backends serving,
       in an order consistent with the active algorithm.
  DO3  Kill backend 2 (docker stop, or /crash?seconds=60). Within interval +
       ejection threshold, zero client-visible failures for GETs; /stats
       shows the backend ejected; it is re-admitted automatically on recovery.
       You recorded the exact timeline in docs/chaos_log.md.
  DO4  Least-connections demonstrably beats round-robin under skewed load
       (/work delays of 900ms on one backend, 50ms on others), and you have
       the latency table to prove it in docs/algorithm_notes.md.
  DO5  Weighted 3:1:1 yields within tolerance of the target split, measured
       over >= 1000 requests, numbers shown.
  DO6  POST failures are NOT retried (you can explain why in one sentence),
       GET failures are retried once elsewhere, and both behaviours have a
       test.
  DO7  Locust at a fixed target RPS: p99 latency and error rate before vs
       during a backend crash are captured and explained.
  DO8  Strategy is switchable at runtime; /stats reflects it immediately.
  DO9  BUILD_LOG.md has a row per session with the freeze diagnosis (U/D/I).
  DO10 You can whiteboard the path of one request through your LB - from
       socket accept to response returned - naming every function it
       passes through, from memory.

--------------------------------------------------------------------------------
  PART 7: HOW TO WORK WITH ME
--------------------------------------------------------------------------------

Same contract as market-pulse (PROFESSOR.md has the full version):
  - You try. Then you try the docs. Then you try the exact error. Then a
    2-minute experiment. THEN you ask me, with evidence of all four.
  - I answer with the name of the thing and where to read about it, not code.
  - If you are still stuck after two rounds, I show a minimal example. You
    close it, rewrite it from memory, and log a rebuild date in BUILD_LOG.md.

================================================================================
  NEXT: open ROADMAP.md and start M0. Estimated effort: 24-30 sessions.
  1-2 hours a day beats a Sunday marathon. Streak beats intensity.
================================================================================
