================================================================================
  HOW_TO_SEARCH_DOCS.md - HOW TO FIND ANSWERS IN DOCUMENTATION
  A skill, not a talent. The exact method, plus the canonical doc map for
  this project's stack. Use it from M0 onward.
================================================================================

--------------------------------------------------------------------------------
  PART 1: THE SEARCH ORDER THAT WORKS (use it every time, in this order)
--------------------------------------------------------------------------------

  1. OFFICIAL DOCS FIRST. Always. Before blogs, before YouTube, before AI.
     For this project: fastapi.tiangolo.com, python-httpx.org,
     www.starlette.io, docs.python.org (asyncio/argparse/logging/venv),
     docs.docker.com, docs.locust.io, MDN for anything HTTP.
     Reason: tutorials rot and copy errors; the official page is maintained
     by the people who wrote the code and states the defaults.

  2. SITE-SCOPED WEB SEARCH - the single highest-leverage search trick:
       fastapi lifespan site:fastapi.tiangolo.com
       httpx streaming site:www.python-httpx.org
       healthcheck depends_on site:docs.docker.com
     This forces results from the official site only. Learn it once, use
     it for years.

  3. THE SOURCE ITSELF. Docs lag code. For any library question, the GitHub
     repo's search box IS documentation: search the class name, read the
     docstring and the signature. FastAPI/Starlette/httpx source is readable
     - try it once and the fear goes away.

  4. THEN the ecosystem: GitHub issues (search the exact error message in
     quotes), Stack Overflow (newest answers, check the date), release
     notes/changelog for version surprises.

  5. AI (including me) LAST, and only with rungs 1-4 done - bring evidence.
     AI is a good EXPLAINER of docs you have read and a terrible REPLACEMENT
     for them: confidently wrong, and you cannot tell which parts are wrong
     until you have read the source of truth yourself.

--------------------------------------------------------------------------------
  PART 2: HOW TO READ A DOC PAGE (most people read docs wrong)
--------------------------------------------------------------------------------

  - READ THE SIGNATURE FIRST. Parameters, their types, and especially their
    DEFAULTS. Half of all framework bugs are a default you did not know.
  - THEN the example, line by line, asking "why is this line here?"
  - THEN the "Raises"/"Errors"/notes section if present - the page's most
    valuable and most-skipped part.
  - CTRL-F is a skill: search the page for your exact error string, the
    parameter name, or "timeout"/"default" before reading linearly.
  - THE VERSION QUESTION, every time: which version am I running?
    (pip show fastapi / docker image tag). Docs for the wrong version are
    the #1 cause of "I did exactly what the docs said and it did not work."
  - WHEN TWO SOURCES DISAGREE, the newer primary source wins. Check dates
    and the library's own release notes before believing either.

--------------------------------------------------------------------------------
  PART 3: THE CANONICAL DOC MAP FOR THIS PROJECT
--------------------------------------------------------------------------------

  HTTP / INTERNET FUNDAMENTALS (M0, M2, M4)
    MDN HTTP overview ............. developer.mozilla.org/en-US/docs/Web/HTTP
    MDN headers ................... .../Web/HTTP/Reference/Headers
                                    (Host, X-Forwarded-For, Connection,
                                    Content-Length, Transfer-Encoding)
    RFC 9110 sec 9.2.1 ............ idempotent methods (GET/HEAD/PUT/DELETE
                                    vs POST) - the basis of the C6 retry rule
    RFC 9112 ...................... message syntax/routing; hop-by-hop headers

  FASTAPI / STARLETTE (M1-M6)
    fastapi.tiangolo.com/tutorial/ first-steps, path & query params, and the
                                    section on bigger applications
    Lifespan events ............... fastapi.tiangolo.com/advanced/events
                                    (where the health loop starts/stops, M5)
    Testing ....................... fastapi.tiangolo.com/tutorial/testing
                                    (TestClient + httpx ASGITransport, M4)
    Starlette routing/requests .... www.starlette.io/routing, /requests,
                                    /responses - FastAPI is Starlette plus
                                    sugar; when docs disagree, Starlette's
                                    page is closer to the metal

  HTTPX (M2-M4: the forwarding engine)
    python-httpx.org/async/ ....... AsyncClient quickstart (M2)
    .../api/ ...................... Client, timeouts, exception hierarchy
    .../advanced/transports/ ...... ASGITransport vs real connections - the
                                    M2 design decision lives here
    .../advanced/clients/ ......... limits, pooling, timeouts (M4)

  PYTHON STDLIB (M3, M5, M9)
    docs.python.org/3/library/asyncio.html  especially: coroutines & tasks,
                                    Lock, wait_for, gather, sleep,
                                    create_subprocess_exec, cancellation
    .../logging.html + logging howto (M2 onward: named loggers, one per
                                    module, run id in every line)

  DOCKER (M7)
    docs.docker.com/reference/dockerfile/   the instructions you actually use
    docs.docker.com/reference/compose-file/ services, networks, healthcheck,
                                    depends_on condition, scale, env_file
    docs.docker.com/network/ ...... "Networking overview": user-defined
                                    bridge = DNS by service name. THE page
                                    that cures the localhost trap.

  LOAD TESTING (M6, M8)
    docs.locust.io ................ writing a locustfile, wait_time,
                                    headless mode, CSV reporting, LoadShape

  BACKGROUND READING (optional, interviews only)
    nginx docs: "ngx_http_upstream_module" - how the real thing describes
      the same four algorithms you are building (plus least_time, which you
      can reimplement as an extension in AFTER-M9)
    Google paper: "The Power of Two Choices in Randomized Load Balancing"
      - the one-page intuition behind P2C (M3/M8)

--------------------------------------------------------------------------------
  PART 4: THE SEARCH-QUERY PATTERNS THAT ACTUALLY HIT
--------------------------------------------------------------------------------

  - THE EXACT ERROR, in quotes, minus your file paths:
      "TypeError: object NoneType can't be used in 'await' expression"
    Add the library name: fastapi httpx "exact error". File paths and your
    variable names only add noise.
  - THE BEHAVIOUR, not the goal:
      not: "how to make my load balancer handle failures"
      but: "httpx ConnectError retry different backend async"
  - VERSION PINNING when things are weird:
      "httpx 0.28 breaking change Client"
  - ERROR -> SOURCE: paste the error class into the library's GitHub search,
    read where it is RAISED. Reading where an exception is born beats every
    SO answer.

--------------------------------------------------------------------------------
  PART 5: THE NOTE-TAKING RULE
--------------------------------------------------------------------------------

  Every time a doc page answers a question you will meet again, write the
  answer - in your own words, max 3 lines - into docs/architecture.md or
  algorithm_notes.md, with the URL. The project you build is also the notes
  you keep; in an interview, your notes ARE your experience.
  If a page was so good you would read it again, put the URL in BUILD_LOG.md
  under "sources this session". BUILD_LOG + these two docs = your private
  handbook by the end of the project.

================================================================================
