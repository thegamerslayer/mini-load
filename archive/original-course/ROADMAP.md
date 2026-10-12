================================================================================
  ROADMAP.md - THE MILESTONES
  Ten milestones, in order. Do not skip. Do not merge two into one.
  Each one: what you build, what to read first, what to search when stuck,
  the checkpoint I will grade you on, and the traps that catch everyone.

  Effort estimate: 24-30 sessions of 1-2 hours. 6-8 weeks at 4 sessions/week.
================================================================================

HOW TO READ EACH MILESTONE:
  GOAL ............ one sentence. If you cannot restate it, re-read it.
  BUILD ........... the concrete artifacts that must exist when you finish.
  READ FIRST ...... documentation to read BEFORE writing code (not after).
  SEARCH WHEN STUCK the queries that work. Steal them, then make them yours.
  CHECKPOINT ...... the evidence I will demand. Numbers, not adjectives.
  TRAPS ........... the mistakes everybody makes here. The questions are the
                    hint; the answers are in the docs you were told to read.

--------------------------------------------------------------------------------
  M0 - RECONNAISSANCE: THE SPEC, THE STANDARDS, THE SHAPE        (1 session, no code)
--------------------------------------------------------------------------------

GOAL
  Understand the request/response path of the thing you are about to build,
  well enough to explain it to a classmate - before writing any code.

BUILD
  - docs/architecture.md started, with a hand-drawn (or ASCII) diagram of:
    client -> LB socket -> strategy pick -> backend -> response path back.
    Annotate every hop with which HTTP actor owns it (client/LB/backend).
  - A one-paragraph answer, in that doc, to each of these:
    * What is the difference between a proxy and a reverse proxy? Which is
      yours, and how would a client notice the difference?
    * What is the difference between L4 and L7 load balancing? Your LB is
      which, and what do you therefore see (and never see) of the request?
    * What are hop-by-hop vs end-to-end headers? Name two of each and say
      which side is responsible for each category in YOUR system.
  - answers.md (or the same file): what round robin, weighted round robin,
    least connections, and P2C each optimise FOR, and when each loses.
    One sentence per pair.

READ FIRST
  - MDN: HTTP overview + "What is a URL" - you need the request anatomy cold.
  - MDN: HTTP headers category page. Skim the list once; you will meet
    Host, X-Forwarded-For, Connection, Content-Length, Transfer-Encoding.
  - RFC 9110 section 9.2.1 (idempotent methods) and RFC 9112 sections on
    message routing. You do not read RFCs for pleasure; you read the two
    sections your design depends on. C6 in README_FIRST depends on 9110.
  - Wikipedia or nginx docs: "smooth weighted round robin". The algorithm is
    two lines of pseudocode; find it and copy it BY HAND into your notes.

SEARCH WHEN STUCK
  - "reverse proxy vs forward proxy difference example"
  - "layer 4 vs layer 7 load balancer difference"
  - "nginx smooth weighted round robin algorithm explained"
  - "httpx streaming response proxy"  (for later, but read the doc titles)

CHECKPOINT
  You can state, without notes: which side closes a keep-alive connection in
  your design, where the body bytes live at each hop, and why POST is
  dangerous to retry. If any of those takes more than one sentence of
  hesitation, re-read and come back.

TRAPS
  - Skimming this and starting to code. The M1 code is easy; M0 is what makes
    M3 and M4 survivable.
  - Confusing load balancer with API gateway. Write one sentence on the
    difference now so you never blur it in an interview.
  - Reading about Kubernetes ingress at this stage. Not yet. Local first.

--------------------------------------------------------------------------------
  M1 - THREE BACKENDS AND AN ENVIRONMENT THAT RUNS               (1-2 sessions)
--------------------------------------------------------------------------------

GOAL
  Three independent backend servers on :8001/:8002/:8003, one shared codebase,
  run and verified by you - with zero LB code yet.

BUILD
  - The file tree from README Part 5 (you create every file yourself; empty
    modules with pass are fine, but the names and homes are fixed).
  - .env.example committed, .env ignored, backend name/port/delay from env.
  - backends/server.py: GET / (identity JSON), GET /health (instant 200),
    GET /work?ms=N (sleep then 200). Run it three times with different env
    vars, locally, without Docker.
  - A README or scripts section: the three exact commands to run the three
    backends, plus curl lines proving each answers.

READ FIRST
  - FastAPI tutorial: "First Steps", "Path Parameters", "Query Parameters",
    and the section on running uvicorn programmatically (Server + uvicorn.run
    with a factory). Note how --reload interacts with env vars.
  - Python docs: venv section + argparse basics (you will need --port soon).
  - python-dotenv README (short) - then write one line in BUILD_LOG on why
    .env is ignored and .env.example is not.

SEARCH WHEN STUCK
  - "fastapi run programmatically uvicorn port env var"
  - "uvicorn workers reload env vars"
  - "curl show response headers -i -v"   (learn -v properly; you will live in it)

CHECKPOINT
  - Three terminals (or one script) run three backends. curl each: identity
    JSON differs, /health is fast, /work?ms=300 measures ~300ms (verify with
    curl -w or your watch).
  - git grep for any hardcoded port or name outside env parsing: zero hits
    in the code paths that matter.
  - You can explain what happens if two backends start on the same port,
    including the OS error you saw when you deliberately tried it.

TRAPS
  - Writing three copies of the server. One file, three env invocations.
  - Putting the sleep inside a sync def and freezing the event loop - then
    wondering why /health stops responding while /work sleeps. Read FastAPI's
    async/sync docs NOW and decide which /work is, and why.
  - Skipping the deliberate port-collision experiment. Error messages you
    have seen once are worth ten you have read about.

--------------------------------------------------------------------------------
  M2 - THE DUMBEST POSSIBLE LOAD BALANCER (ROUND ROBIN, NO HEALTH)  (2 sessions)
--------------------------------------------------------------------------------

GOAL
  localhost:8080 forwards to 8001/8002/8003 in rotation and returns the
  backend's response as its own. That is the whole milestone.

BUILD
  - src/config.py: parses LB_PORT and the backend list from env. Nothing
    hardcoded, no defaults for things that must be explicit.
  - src/pool.py: Backend class (name, url, counters placeholder) and the
    pool holding them.
  - src/strategies.py: round_robin(pool) -> Backend. Plain implementation
    first; you will make the counter safe in M3.
  - src/proxy.py: forwards method + path + query + headers + body via httpx
    ASGI transport or AsyncClient. Returns status/headers/body from backend.
  - src/app.py: FastAPI catch-all route (@app.api_route with path, methods
    including GET, POST, PUT, DELETE, PATCH, HEAD) wired to proxy.
  - src/main.py: CLI (--port, --backends) or env-only; document the choice.
  - First entry in docs/architecture.md: one request traced through your
    actual function names.

READ FIRST
  - httpx docs: the AsyncClient quickstart, THEN "Supported Transports"/ASGI
    transport page - decide which of the two fits proxying to a URL, and
    write why in architecture.md. (One proxies to an app object, the other
    opens a real connection - the difference matters for what you are
    simulating.)
  - httpx docs: timeouts page. Your LB must not hang forever on a dead
    backend; choose connect/read/write/timeout values and justify them.
  - Starlette docs (FastAPI sits on it): routing and the Request/Response
    objects, especially .stream() and how to re-emit a body.
  - MDN: X-Forwarded-For and Host - what you must add or preserve before
    forwarding (you are now the proxy in the chain).

SEARCH WHEN STUCK
  - "fastapi catch all route proxy httpx async example"
  - "httpx ASGITransport vs AsyncClient base_url"
  - "fastapi proxy request body streaming forward"
  - "<your exact error>"   (httpx errors name the transport step clearly)

CHECKPOINT
  - curl 8080/hello five times: backends rotate 1-2-3-1-2, response body
    shows the backend identity, and your response headers are sane (no
    leaked hop-by-hop headers - name which you stripped, where, and why).
  - POST to 8080/echo with a JSON body: the backend receives the body intact
    (log it backend-side to prove it) and content-length matches.
  - Stop backend 2 entirely. Requests now FAIL (this is expected in M2 -
    there is no health checking yet). Count the failure rate by hand: it
    should be exactly 1/3. Write that number down; M3 must improve it.
  - The trace paragraph in architecture.md matches the real function names.

TRAPS
  - Reading the whole request body into memory with await request.body() and
    calling it done. Acceptable in M2 ONLY if you write the TODO + know the
    streaming section you will apply in M4. If you cannot name it, you are
    not accepting it, you are ignoring it.
  - Forwarding Host unmodified (backends will 4xx or mis-route) or
    forwarding Connection: keep-alive (hop-by-hop; read the RFC section
    again). Both are classic; you will hit at least one.
  - A synchronous httpx client inside async def - this silently serialises
    all traffic and teaches you nothing about async. The tutorial's warning
    about blocking calls is the hint.
  - Testing with only GETs. The POST path (body forwarding) breaks
    differently. Test both from M2 onward.

--------------------------------------------------------------------------------
  M3 - STRATEGIES, CONCURRENCY SAFETY, AND FIRST TESTS           (3 sessions)
--------------------------------------------------------------------------------

GOAL
  Four algorithms behind one interface, each correct under concurrent
  requests, each with unit tests that fail if you break it.

BUILD
  - weighted round robin (smooth interleave) and least connections, plus
    keep round robin; each takes the healthy pool only.
  - Fix the concurrency bug in round robin's counter (asyncio.Lock or an
    atomic pattern - pick one and defend it in algorithm_notes.md).
  - Active-connection tracking per backend: increment at forward start,
    decrement in finally (find out why finally, then write it down).
  - tests/test_strategies.py: no HTTP involved. Feed fake pools; assert the
    exact pick sequence for RR and weighted 3:1:1; for least-connections,
    assert the least-loaded backend wins under a scripted in-flight state;
    run a small concurrent RR test and assert the sequence stays valid.

READ FIRST
  - Python asyncio docs: Locks (and re-read the coroutines/tasks pages from
    the tutorial if awaits still feel fuzzy - this milestone is where fuzzy
    becomes broken).
  - The smooth-WRR reference you found in M0 (nginx algorithm) - implement
    from the pseudocode, not from memory of the behaviour.
  - pytest docs: fixtures, parametrize, and testing asyncio code (anyio
    plugin that ships with FastAPI, or pytest-asyncio - pick one, justify).
  - Python docs: random.choices vs secrets - decide which belongs in a load
    balancer's P2C and why (M4 uses P2C, but read now).

SEARCH WHEN STUCK
  - "smooth weighted round robin nginx algorithm pseudocode"
  - "asyncio lock vs no lock single thread event loop"
  - "pytest async test fixture anyio pytest-asyncio"
  - "least connections load balancing implementation in flight requests"

CHECKPOINT
  - Weighted 3:1:1 over 50 sequential curls: counts are 30/10/10 +/-1, and
    the interleaving is smooth (no three same backends in a row) - show the
    actual sequence.
  - test_strategies.py passes and each test NAME states the behaviour it
    pins (read your own test list out loud; if a name says "test_rr" it
    says nothing - rename it).
  - Kill a test (deliberately flip the weighted logic) and watch it fail;
    then restore. Show me both runs. A test you have never seen fail is
    decoration.
  - algorithm_notes.md has one paragraph per algorithm: what it optimises,
    your implementation's key line(s), and when it loses.

TRAPS
  - Implementing weighted RR as "3 of A, 1 of B, 1 of C" bursts. That is
    what smooth-WRR exists to prevent; the M5 checkpoint will measure it.
  - Counting "active connections" without a finally block. One exception
    path and the counter drifts forever - least connections then routes by
    a lie. Deliberately raise inside the handler once and check the counter
    recovered (do this once, record it in chaos_log.md).
  - Asserting on exact sequences under real concurrency in tests - sequence
    tests belong to the sync layer; concurrency tests assert invariants
    (no backend over-picked beyond weight tolerance), not positions.

--------------------------------------------------------------------------------
  M4 - PRODUCTION-GRADE PROXYING: STREAMING, TIMEOUTS, RETRY     (3 sessions)
--------------------------------------------------------------------------------

GOAL
  The forwarding path handles big/slow bodies, dead backends, and idempotency
  rules the way a real LB would - and you can prove each property.

BUILD
  - Streaming both ways: request body chunks forwarded as they arrive
    (httpx .stream / starlette request.stream), response streamed back.
    Verify with a large transfer and bounded memory (watch the process RSS
    or log chunk counts - do not buffer and claim it streams).
  - Timeout policy from config: short connect timeout, sane read timeout,
    applied to backend calls. Dead backend = fast failure, not a hang.
  - Retry-once-on-a-different-backend for GET/HEAD/PUT/DELETE on connection
    errors and 502/503, with the C6 rule in a comment AT the decision point.
  - X-Request-ID generation/propagation, plus X-Forwarded-For append (read
    the security note: appending vs trusting client-supplied).
  - tests/test_proxy.py: spins the LB app + two fake backends (one healthy,
    one dead); asserts GET retries land on the healthy one, POST does NOT
    retry, and the 502 body is your clean JSON error.

READ FIRST
  - httpx: streaming requests and responses, timeout fine-tuning, and
    exception hierarchy (ConnectError/ReadTimeout/... - your retry decision
    switches on these classes, not on strings).
  - MDN: 502 vs 503 vs 504 - which is yours when the backend refuses
    connection vs times out vs is ejected-and-absent? Decide and document.
  - Starlette: Request.stream() and Response content streaming.
  - MDN: X-Forwarded-For - the whole section on spoofing/trusting.

SEARCH WHEN STUCK
  - "httpx async streaming proxy request body chunks"
  - "httpx connect timeout vs read timeout proxy dead backend"
  - "x-forwarded-for append proxy real client ip security"
  - "fastapi testclient httpx ASGITransport test proxy"

CHECKPOINT
  - Stream a 100MB body through the LB (curl --data-binary @bigfile): LB
    memory stays flat (show RSS before/during/after), backend receives all
    bytes (checksums match).
  - Kill backend 2, run 30 sequential GETs: zero failures (retry absorbed
    it), and /stats (even a temporary debug endpoint) shows the retries
    happened. Restore backend 2.
  - Same experiment with POST: failures ARE visible to the client (1/3 of
    the time while a backend is dead, until M5's health checks shrink that
    window) - and the test proving no-retry passes.
  - 502/503/504 mapping: you can point at the line of code that chooses
    between them and say which situation each covers.

TRAPS
  - Retrying on read timeouts for GETs by default: the backend may have
    DONE the work. Decide explicitly (config flag, default conservative)
    and write the trade-off in architecture.md. Connection errors are
    clearly safe; read-timeouts are not - know why you chose what you chose.
  - Forgetting Content-Length recompute on chunked forwarding; symmetric
    bug: forwarding a stale Content-Length. Both produce maddening hangs -
    the fix is understanding, not a magic header line from Stack Overflow.
  - Testing retry logic only via unit fakes and never against a real dead
    port. Both layers, always: fake for logic, real for transport truth.
  - Swallowing backend exceptions to "return something". Map exceptions to
    status codes deliberately, or your /stats failures counter lies.

--------------------------------------------------------------------------------
  M5 - HEALTH CHECKS AND AUTOMATIC FAILURE DETECTION             (3 sessions)
--------------------------------------------------------------------------------

GOAL
  The LB detects dead backends within seconds, without traffic, and
  re-admits them on recovery - so client-visible failures approach zero
  even for POSTs, and the dead window you measured in M2/M4 disappears.

BUILD
  - src/health.py: asyncio background task (started from FastAPI lifespan,
    NOT from a module import side effect - find out why), looping: for each
    backend, GET /health with timeout, mark up/down per consecutive
    fail/success thresholds from config.
  - Pool consults health state: strategies pick only healthy backends; if
    ALL are down, return 503 with a clear body (decide this now - it will
    happen in demos).
  - Ejection/re-admission events logged with timestamps into a ring or a
    list served by /stats (state + recent transitions).
  - Backends: implement /crash?seconds=N (health endpoint hangs N seconds,
    process stays up) - this is your failure injector for every demo.
  - tests/test_health.py: with interval shortened to ~0.1s, eject after the
    configured misses, re-admit after recoveries; assert /stats reflects
    each transition within a bounded number of loop ticks.
  - docs/chaos_log.md: first three entries - crash 2, crash all, flap 2
    rapidly - each with timeline of what /stats showed and when.

READ FIRST
  - FastAPI docs: lifespan events (modern state, not deprecated
    @app.on_event) - this is where the health task starts and stops; read
    the cancellation section of asyncio's task docs to stop it cleanly.
  - asyncio docs: sleep vs wait_for (your health loop needs one of these to
    be cancellable and to bound the check itself), gather with return
    exceptions if you check in parallel, and task cancellation semantics.
  - The retry/backoff side of health: what happens if the check itself
    times out - is that a failure? Decide, document.

SEARCH WHEN STUCK
  - "fastapi lifespan startup background task asyncio create_task"
  - "asyncio wait_for timeout gather return_exceptions"
  - "health check consecutive failures flap damping load balancer"
  - "fastapi graceful shutdown cancel background tasks"

CHECKPOINT
  - THE demo: 60 sequential GETs against 8080 while you crash backend 2 at
    second 5 (crash 20s) and recover it at second 25. Show the timeline:
    zero client failures after the FIRST health-interval detection, backend
    ejected by ~interval+threshold, re-admitted after recovery, all visible
    in /stats events. Record exact times in chaos_log.md.
  - Same demo with POST: the failure window is now bounded by detection
    time, not by your retry rule. Compare the number with M4's number and
    write both down - that difference IS the milestone's lesson.
  - Kill ALL backends: 503 with your JSON body, LB stays alive, recovers
    when backends return. Show it.
  - Rapid-flap test (crash/recover in a loop for 30s): system stays sane,
    counters reconcile, no task leaks (asyncio.all_tasks before/after).

TRAPS
  - Health checks that stop when one raises. One dead backend's timeout
    killing the whole loop is the classic bug; the gather/
    return_exceptions docs exist for you.
  - Ejecting on ONE failed check: a single lost packet then ejects backends
    and your pool flaps. Consecutive-failures threshold is the fix; set it
    from config and justify the default.
  - Starting the health task via module-level asyncio.create_task at import
    time: works in scripts, breaks under uvicorn workers and tests, and you
    will not know why until you read the lifespan docs. Read first.
  - A health interval shorter than the health timeout. Your loop then
    checks concurrently with itself; decide if that is legal and say why.
  - Trusting /health checks that succeed while the backend is overloaded -
    health and load are different things; least-connections (M3) is your
    load signal. One paragraph on this in algorithm_notes.md.

--------------------------------------------------------------------------------
  M6 - METRICS AND THE LIVE DASHBOARD                            (2-3 sessions)
--------------------------------------------------------------------------------

GOAL
  One glance answers: who is up, who is getting traffic, how fast, and what
  changed - without attaching to any process or reading a log line.

BUILD
  - src/metrics.py: per-backend counters (requests, 2xx, 5xx, retries,
    ejections), latency reservoir (bounded; document your choice: reservoir
    sampling vs a ring of the last N), and percentile computation (p50/95/99).
  - Concurrency safety for counters: know which increments happen on the
    event loop (safe-ish) and what would break with threads later; one
    paragraph in architecture.md.
  - /stats: full JSON snapshot (per-backend + totals + current algorithm +
    health events). Freezes a consistent snapshot (decide: copy under lock
    or accept torn reads of counters and say why it is acceptable).
  - static/dashboard.html: one file, ~200 lines, fetches /stats every 1s,
    renders status dot / RPS / latency bars, and a dropdown to switch
    strategy live (PUT /config or POST /admin/strategy -> validates + swaps
    the strategy object; no restart).
  - scripts/load_test.py: a locust file hitting /work with configurable
    delay; fixed target RPS mode.

READ FIRST
  - Locust docs: writing a first locustfile, and the "running without web
    UI / target RPS" pages. You will use wait_time and task weight.
  - MDN fetch() + a CSS flexbox primer if needed - the dashboard is
    deliberately boring tech; every fancy thing costs you time.
  - Prometheus docs: histogram vs summary AND their quantile caveats (read
    even though you are not exporting yet - your percentile logic will be
    compared to these in interviews; know what a histogram bucket is).

SEARCH WHEN STUCK
  - "reservoir sampling latency percentiles implementation"
  - "locust fixed requests per second target rps example"
  - "javascript fetch interval update dashboard vanilla js"
  - "prometheus histogram vs summary quantiles"

CHECKPOINT
  - /stats reconciles: total requests == sum of per-backend requests (state
    the exception cases: retries counted where? decide and document).
  - Weighted 3:1:1 under 1000 locust requests: measured split within 5%,
    shown as a table (this completes README DO5).
  - The percentile sanity check: p50 from /stats vs hand-timed curl -w
    medians on 20 requests - same ballpark; if not, find the bug before
    moving on. State your reservoir size and its memory cost.
  - Dashboard shows the M5 crash demo live: dot flips red, RPS reroutes to
    survivors, flips green on recovery. Strategy switch works mid-load with
    no dropped requests (locust keeps running through the switch).

TRAPS
  - Percentiles from the full list, forever: memory grows with traffic
    until the demo machine dies. Bounded reservoir from day one.
  - A dashboard so elaborate it becomes the project. One HTML file, no
    build step, no framework - the LB is the project.
  - Strategy switching that swaps the object mid-request and throws for the
    one request that held a reference. Atomic swap (single attribute
    assignment) - and know why that is safe on one event loop.
  - Metrics counted AFTER the response returns but exceptions skip them:
    wrap the forward in try/except so failures count as failures, at the
    right place, or your failure rate reads 0% during outages (the M2
    number you already measured should have made you suspicious).

--------------------------------------------------------------------------------
  M7 - DOCKER COMPOSE: CONTAINERS, NETWORKS, SERVICE DISCOVERY   (2 sessions)
--------------------------------------------------------------------------------

GOAL
  docker compose up -d stands up LB + 3 backends on one network, reached by
  service name - and your topology (more/fewer backends, different weights)
  is a compose-file edit, not a code change.

BUILD
  - Dockerfile: python:slim base, requirements install, parameterised by
    command (same image runs LB or backend - document the trick: command
    overrides in compose).
  - docker-compose.yml: one user-defined network; lb + 3 backends; health-
    check blocks for the backends; depends_on with condition; env for names
    and /work delays. LB's backend list now uses service names (server1:8000)
    not localhost - INSIDE containers localhost means the container itself.
    This sentence is the milestone; internalise it.
  - Scale check: docker compose up -d --scale server=4 against a 3-backend
    config - observe what your config does; then parametrise properly and
    note the result in architecture.md (service discovery, in the simple
    form, is "compose DNS name -> your pool builder reads N names").
  - .dockerignore (venv, .env, __pycache__, spool if any).

READ FIRST
  - Docker docs: Dockerfile reference (the instructions you actually use),
    and the compose file reference for: networks, depends_on with condition,
    healthcheck, scale, and environment/env_file.
  - Docker docs: "Networking overview" - user-defined bridge networks give
    DNS by service name. This is the page that answers the localhost trap.
  - Docker docs: multi-stage builds - read even if you skip; know the term.

SEARCH WHEN STUCK
  - "docker compose healthcheck depends_on condition service_healthy"
  - "docker compose scale service env var backends list"
  - "docker container localhost vs service name networking"
  - "python slim docker image uvicorn fastapi dockerfile"

CHECKPOINT
  - Fresh clone behaviour: compose up, curl 8080/hello, all three identities
    rotate. docker compose ps shows healthy for all four services.
  - docker stop server-2 mid-traffic: M5's demo runs identically in
    containers (chaos_log.md gets the container timeline with timestamps
    from docker events).
  - You can explain, from the compose file: which network the traffic uses,
    how the LB resolves server1, and what happens to in-flight requests
    when a container stops (hint: what does the healthcheck do, and when).
  - The image is one image, two commands. Show docker images: no per-role
    image build needed.

TRAPS
  - Hardcoding localhost:8001 into containerised LB config: inside the
    container that is the LB itself. The DNS-by-service-name page is the
    cure; read it before debugging for an hour.
  - No healthcheck on backends so compose reports them up before uvicorn
    binds: LB starts, finds nobody home, and health ejection logic races
    the boot. Healthcheck + condition fixes the race deterministically.
  - Copying .env into the image (ADD . /app). .dockerignore is a security
    file, not a convenience. Prove it: docker run --rm image env | grep
    shows no secrets (there are none here - the habit is the point).
  - --scale with a config that does not read the backend list dynamically:
    observe the honest failure, then make pool construction read env N
    names, and log the final list at startup (visible in docker logs lb).

--------------------------------------------------------------------------------
  M8 - LOAD TESTING AND THE PROOF OF ALGORITHMS                  (2 sessions)
--------------------------------------------------------------------------------

GOAL
  Numbers, not vibes: each algorithm's behaviour under load, captured in
  tables you generated, and a load-test rig you can rerun any time.

BUILD
  - The full locust rig: fixed RPS profile, /work with per-test delay
    pattern (skewed: one slow backend via env), a headless run mode, and a
    results directory (git-ignored) of per-run CSVs.
  - Run matrix (all into docs/algorithm_notes.md):
      1. RR, healthy pool, equal delays -> equal split (baseline sanity).
      2. RR vs least-connections, delays 900/50/50ms, 100 RPS, 60s ->
         least-connections wins on p99; the table shows by how much.
      3. Weighted 3:1:1, equal delays -> split within 5% (already done in
         M6; rerun under load now - tolerance under load is the lesson).
      4. P2C vs RR under the skewed pattern -> the queueing you see is the
         whole point; one paragraph on why P2C approximates least-loaded
         without global state.
  - The crash-under-load run: locust at 100 RPS; crash server2 for 30s at
    t=20s; capture p99 + error rate before/during/after (README DO7).

READ FIRST
  - Locust docs: headless mode, CSV reporting, custom shape/LoadShape for
    the fixed-RPS profile, and how its own stats are computed (so you know
    what the numbers include).
  - Little's Law (one page, any source) - to sanity-check that your RPS x
    delay math matches the concurrency you observe in /stats.

SEARCH WHEN STUCK
  - "locust headless csv result fixed rps load shape"
  - "little's law load testing sanity check"
  - "tail latency least connections power of two choices"

CHECKPOINT
  - The run matrix exists with real CSVs behind every table (file names
    cited next to each table; no orphan numbers).
  - The M8.2 table demonstrates least-connections > RR on p99 under skew,
    with numbers a reader could defend in an interview.
  - Crash-under-load: the error-rate spike and its duration are visible and
    explained (detection window + retry policy), tying together M4 and M5.
  - Little's Law check: predicted in-flight vs /stats active connections
    within the same order of magnitude; deviation explained in one line.

TRAPS
  - Load testing on one machine with everything on localhost and concluding
    anything about absolute numbers. Your numbers are comparative only;
    write that caveat on every table. (In M7+ the containers make it a bit
    more honest, still one kernel.)
  - Running the LB and the load generator in the same terminal with the
    same process competing for the event loop; separate terminals, and
    know that even then your client is not the internet.
  - Cherry-picking the best run. Three runs each, show the median. One
    cherry-picked table is a lie with formatting.
  - Forgetting to reset metrics between runs (or not labeling which run a
    CSV belongs to) - unlabelled numbers are unreadable a week later.

--------------------------------------------------------------------------------
  M9 - AUTO-SCALING (THE FINAL BOSS)                             (3-4 sessions)
--------------------------------------------------------------------------------

GOAL
  Under sustained high load, a new backend joins the pool and traffic
  redistributes; when load drops, it leaves - driven by YOUR signals, with
  the whole loop observable.

BUILD
  - Scaling signal: RPS per active backend, or p95 latency, or active
    connections - compute a windowed average in the metrics module; pick
    ONE signal, document the choice and the threshold rationale.
  - Scale-UP path (do this first): LB exposes /admin/scale (validated); on
    trigger it adds server-N (port from a range), starts it as a subprocess
    with env vars (local mode) or shells to docker compose --scale (M7
    mode); waits for /health; re-admits to the pool. Under continuous
    locust load: p99 recovers after the new backend joins - capture it.
  - Scale-DOWN path: drain, do not kill - backend gets removed from the
    pool, in-flight requests finish (decrement-based drain), THEN process
    stops. In-flight-loss during drain is the classic bug; test for it.
  - Cooldown between scaling actions (else you flap up/down at threshold
    edges). Configurable; justify the default.
  - The whole loop in /stats (signal value, thresholds, cooldown state,
    pending actions) and in chaos_log.md with timestamps.

READ FIRST
  - asyncio docs: subprocess (create_subprocess_exec) for local mode, and
    task groups / structured concurrency for the lifecycle of scaling tasks.
  - Docker CLI: compose --scale and how to script it; docker events, if you
    want triggers from container state.
  - Kubernetes docs, HPA page - READ ONLY, as vocabulary: what upstream
    calls scale signals, cooldown (stabilization window), and target value.
    You are building a toy HPA; knowing the real vocabulary is the point.

SEARCH WHEN STUCK
  - "asyncio create_subprocess_exec environment variables example"
  - "docker compose scale up programmatically script"
  - "horizontal pod autoscaler stabilization window cooldown"
  - "graceful shutdown drain in-flight requests load balancer"

CHECKPOINT
  - Demo: steady load at 100 RPS, raise /work delays, watch signal cross
    threshold, server-4 appears in /stats within one interval + health
    check, RPS per backend rebalances - timeline shown.
  - Load drops, signal crosses low threshold, one backend drains: ZERO
    in-flight losses (you counted in-flight before/after), process exits
    after drain - timeline shown.
  - Flap guard: put load exactly at threshold - no oscillation; explain the
    cooldown's role with the /stats trace.
  - architecture.md final diagram includes the scaling loop; every magic
    number (window, threshold, cooldown, ports range) is in .env.example
    with a comment.

TRAPS
  - Scaling on instantaneous RPS: one burst and you spawn/die/spawn. Window
    the signal (even a 10s simple average); the cooldown is belt-and-
    suspenders, you need BOTH.
  - Orphaned processes: subprocess backends that outlive the LB on Ctrl-C.
    Handle SIGINT/SIGTERM, reap children (asyncio subprocess docs), verify
    with ps/task manager after a kill - this is a real bug you WILL hit.
  - Scale-down that drops in-flight requests: drain via the active-
    connection counter you built in M3 - this is why that counter existed.
  - Killing instead of draining during in-flight: the /work endpoint with a
    900ms delay makes losses visible; test drain against a long delay
    (2s), not against instant responses.

--------------------------------------------------------------------------------
  AFTER M9
================================================================================

You will have built - by hand - the core of what Nginx, HAProxy, and cloud
load balancers do for you, plus a toy HPA. Natural extensions, in priority
order, only if you want them:

  1. Passive health checking (out-of-band failure counting from real
     traffic) alongside the active checker; compare detection times.
  2. Consistent hashing / session affinity (sticky sessions by cookie) -
     teaches you what you lose (perfect balance) to gain what (cache hit
     rates). Add a cache to backends to SEE the trade-off.
  3. Rate limiting per client at the LB (token bucket) - connects to your
     system-design course module 09.
  4. Prometheus metrics export + Grafana dashboard - replaces your JSON
     /stats with industry tooling; the comparison is the lesson.
  5. A second LB instance with keepalived/VRRP - the vocabulary of HA.
  6. Only then: deploy one backend + LB to a free-tier cloud box and repeat
     the load tests. Local first, always.

================================================================================
  START M0 AFTER READING: README_FIRST.md, then PROFESSOR.md, then this file,
  then HOW_TO_SEARCH_DOCS.md (skim once; use it from M0 onward).
================================================================================
