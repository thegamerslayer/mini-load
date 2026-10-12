========================================================================
  HOW_TO_SEARCH_DOCS.md - HOW TO FIND ANSWERS ALL BY YOURSELF
  This is a SKILL, like tying your shoes - not a special talent you are
  born with. Here is the exact way to do it, plus the map of all the
  instruction books for our toy box. Use it from Step 0 onward.
========================================================================

------------------------------------------------------------------------
  PART 1 - THE RIGHT ORDER (do it this way EVERY time)
------------------------------------------------------------------------

  1. THE REAL INSTRUCTIONS FIRST. Always. Before blogs, before videos,
     before any chat robot.
     For our project, the real instructions are:
        fastapi.tiangolo.com      (our web door)
        python-httpx.org          (our carrying tool)
        www.starlette.io          (what FastAPI is built on)
        docs.python.org           (the Python toy box: asyncio, argparse,
                                   logging, venv)
        docs.docker.com           (the boxes, later)
        docs.locust.io            (the many-kids machine)
        MDN for anything about the internet and asks
     WHY: blogs and videos get old and copy each other's mistakes. The
     real instructions are kept fresh by the people who MADE the tool, and
     they tell you the DEFAULT values - which is where half the bugs hide.

  2. THE BEST SEARCH TRICK EVER - search ONE website only.
     Type the word "site:" then the website, then your word. Like:
        fastapi lifespan site:fastapi.tiangolo.com
        httpx streaming site:www.python-httpx.org
        healthcheck depends_on site:docs.docker.com
     This shows results from the real instructions ONLY. Learn it once,
     use it for years.

  3. THE TOY'S OWN CODE. The instructions sometimes fall behind the toy.
     The tool's own code page has a search box - and THAT is instructions
     too. Search the name of the thing, read how it is used. FastAPI,
     Starlette, and httpx are readable. Try it once and the fear goes away.

  4. THEN the neighborhood: the tool's own bug reports (search the exact
     error in quote marks), the big answer website (newest answers, always
     check the date!), and the "what changed" notes for surprises when a
     version goes up.

  5. A CHAT ROBOT (including me) LAST, and only after steps 1-4, and only
     with the evidence you found.
     A robot is a good EXPLAINER of pages you already read, and a terrible
     REPLACEMENT for them: it sounds sure even when it is wrong, and you
     cannot tell which parts are wrong until you have read the real page
     yourself.

------------------------------------------------------------------------
  PART 2 - HOW TO READ A PAGE (most people read pages wrong)
------------------------------------------------------------------------

  - READ THE NAME-LINE FIRST: the parts it takes, what kind each part is,
    and especially the DEFAULTS. Half of all bugs are a default you did
    not know about.
  - THEN the example, line by line, asking "why is this line here?"
  - THEN the "what can go wrong" section if the page has one. It is the
    most useful part and the part everybody skips.
  - SEARCHING A PAGE IS A SKILL: use Ctrl-F to look for your exact error
    text, the part name, or the words "timeout" / "default" before you
    read the whole page top to bottom.
  - THE VERSION QUESTION, every time: which version am I running?
    (ask your toy box: "pip show fastapi"). Reading instructions for the
    WRONG version is the number-one reason people say "I did exactly what
    the page said and it still did not work."
  - WHEN TWO PAGES DISAGREE, the newer real one wins. Check the dates and
    the "what changed" notes before believing either one.

------------------------------------------------------------------------
  PART 3 - THE MAP OF ALL OUR INSTRUCTION BOOKS
------------------------------------------------------------------------

  THE INTERNET AND ASKS (Steps 0, 2, 4)
    MDN "HTTP overview" ......... developer.mozilla.org/en-US/docs/Web/HTTP
    MDN headers list ............ .../Web/HTTP/Reference/Headers
                                  (Host, X-Forwarded-For, Connection,
                                  Content-Length, Transfer-Encoding)
    RFC 9110 section 9.2.1 ...... which asks are SAFE to repeat
                                  (the basis of RULE 6)
    RFC 9112 .................... how a message is shaped and where it goes;
                                  the "hop-by-hop" headers

  FASTAPI / STARLETTE (Steps 1-6)
    fastapi.tiangolo.com/tutorial/ ... first steps, path parts, query parts,
                                  and building bigger apps
    "lifespan events" ........... fastapi.tiangolo.com/advanced/events
                                  (where the knock-knock helper starts/stops,
                                  Step 5)
    Testing ..................... fastapi.tiangolo.com/tutorial/testing
    Starlette doors & asks ...... www.starlette.io/routing, /requests,
                                  /responses - FastAPI is Starlette plus
                                  sugar; when the two disagree, Starlette's
                                  page is closer to the metal

  HTTPX (Steps 2-4: the carrying tool)
    python-httpx.org/async/ ..... the AsyncClient quickstart (Step 2)
    .../api/ .................... Client, waiting times, the error family
    .../advanced/transports/ .... "pretend app" vs real connection - the
                                  Step 2 design choice lives right here
    .../advanced/clients/ ....... limits, reusing connections, waiting (Step 4)

  THE PYTHON TOY BOX (Steps 3, 5, 9)
    docs.python.org/3/library/asyncio.html  especially: coroutines & tasks,
                                  Lock, wait_for, gather, sleep,
                                  create_subprocess_exec, cancelling
    .../logging.html ............ how to print tidy notes from your code
                                  (a named note-writer per file, from Step 2 on)

  BOXES (Step 7)
    docs.docker.com/reference/dockerfile/     the box recipe commands
    docs.docker.com/reference/compose-file/   services, pretend-
                                  playgrounds, "are you healthy?", "wait
                                  until healthy", scale, settings files
    docs.docker.com/network/ .... "Networking overview": a shared
                                  pretend-playground lets boxes find each
                                  other BY NAME. THE page that cures the
                                  "localhost inside a box" boo-boo.

  THE MANY-KIDS MACHINE (Steps 6, 8)
    docs.locust.io .............. your first locustfile, wait_time,
                                  no-web-page runs, spreadsheet saving,
                                  custom shapes

  BONUS READING (for sounding smart later)
    nginx docs: "ngx_http_upstream_module" - how the real grown-up Door
      Helper describes the same four choosing rules you are building
    Google paper: "The Power of Two Choices in Randomized Load Balancing"
      - the one-page idea behind P2C (Steps 3 and 8)

------------------------------------------------------------------------
  PART 4 - SEARCH WORDS THAT ACTUALLY WORK
------------------------------------------------------------------------

  - THE EXACT ERROR, in quote marks, minus your own file paths:
        "TypeError: object NoneType can't be used in 'await' expression"
    Add the tool's name: fastapi httpx "exact error". Your file paths and
    your own names of things only add noise.
  - THE BEHAVIOUR you want, not the big goal:
        instead of: "how to make my load balancer handle failures"
        try:        "httpx ConnectError retry different backend async"
  - VERSION PINNING when things are strange:
        "httpx 0.28 breaking change Client"
  - ERROR -> SOURCE: paste the error's NAME into the tool's own code
    search and read the line where it is BORN. Seeing where an error is
    born beats every answer you will ever find online.

------------------------------------------------------------------------
  PART 5 - THE NOTE-TAKING RULE
------------------------------------------------------------------------

  Every time a page answers a question you will meet again, write the
  answer - in YOUR OWN words, at most 3 lines - into docs/architecture.md
  or docs/algorithm_notes.md, with the web address.

  The project you build is also the notebook you keep. Later, your notes
  ARE your experience.

  If a page was so good you would read it again, put its address in
  BUILD_LOG.md under "pages I read this sitting". BUILD_LOG + those two
  docs = your own private handbook by the end.

========================================================================
