========================================================================
  ROADMAP.md - THE TEN STEPS
  Ten steps, in order. Do not skip. Do not squish two into one.

  Every step says:
     WHAT YOU WANT ... one sentence. If you cannot say it back, read again.
     BUILD ........... the things that must exist when you are done.
     READ FIRST ...... read this BEFORE you build. Not after.
     SEARCH .......... what to type in a search box when you are stuck.
     PROVE IT ........ what I will ask to see. NUMBERS, not feelings.
     OOPSIES ......... the mistakes everybody makes here.

  It is about 24-30 sittings. One short sitting a day beats one giant day.
========================================================================

------------------------------------------------------------------------
  STEP 0 - LOOK BEFORE YOU BUILD                       (1 sitting, no code)
------------------------------------------------------------------------

WHAT YOU WANT
  Understand how an ask travels from kid to answer, well enough to explain
  it to a friend - BEFORE writing any code.

BUILD
  - Start docs/architecture.md with a drawing (hand-drawn or with slashes
    and dashes) of: kid -> the door :8080 -> a helper -> the answer back.
    Mark on the drawing who owns each hop (kid / door / helper).
  - In the same file, write one short paragraph for each:
      * What is a proxy vs a reverse proxy? Which are we? How would a kid
        even notice the difference?
      * What is L4 vs L7 sharing? Which are we, and what does that mean
        we can see (and can never see) about the ask?
      * What are "hop-by-hop" headers vs "end-to-end" headers? Name two of
        each and say who is in charge of each, in OUR system.
  - Write what each of the four choosing rules is GOOD at, and when it
    loses. One sentence each: round robin, weighted, fewest-waiting, P2C.

READ FIRST
  - MDN: "HTTP overview" + "What is a URL". You need to know the shape of
    an ask by heart.
  - MDN: the HTTP headers list. Skim it once. You will meet Host,
    X-Forwarded-For, Connection, Content-Length, Transfer-Encoding.
  - RFC 9110 section 9.2.1 (which asks are SAFE to repeat) and the RFC 9112
    parts about where a message goes. You do not read RFCs for fun; you
    read the two parts your design depends on. RULE 6 needs 9110.
  - Wikipedia or the nginx docs: "smooth weighted round robin". It is two
    lines of pretend-code. Find it and COPY IT BY HAND into your notes.

SEARCH
  - "reverse proxy vs forward proxy difference example"
  - "layer 4 vs layer 7 load balancer difference"
  - "nginx smooth weighted round robin algorithm explained"
  - "httpx streaming response proxy"   (for later - just read the titles)

PROVE IT
  Without looking, you can say: who closes a keep-alive connection in our
  design, where the body bytes sit at each hop, and why asking for ice
  cream twice is bad. If any one takes more than a sentence of thinking,
  read again and come back.

OOPSIES
  - Skimming this and starting to code. Step 1 is easy. Step 0 is what
    makes Steps 3 and 4 survivable.
  - Mixing up "load balancer" and "API gateway". Write one sentence on the
    difference now, so you never blur it later.
  - Reading about Kubernetes before you can run three helpers on your own
    computer. Not yet. Your own computer first.

------------------------------------------------------------------------
  STEP 1 - THREE HELPERS THAT ACTUALLY RUN              (1-2 sittings)
------------------------------------------------------------------------

WHAT YOU WANT
  Three separate helper programs on :8001/:8002/:8003, all made from ONE
  file, all started by you and seen working - with ZERO Door Helper code
  written yet.

BUILD
  - Make the file tree from README Part 5. You create every file yourself.
    Empty files with just a name are fine. But the names and homes are set.
  - .env.example is shared; .env stays secret. Helper name, port, and nap
    time all come from settings.
  - backends/server.py: "/" says who I am; "/health" says awake, fast;
    "/work?ms=N" naps N milliseconds then says done. Start it three times
    with three different names, on your own computer, no boxes yet.
  - Write down the three exact commands to start the three helpers, plus
    the ask-commands that prove each one answers.

READ FIRST
  - FastAPI tutorial: "First Steps", "Path Parameters", "Query
    Parameters", and how to run it from a start button (the section on
    running the server from code). Notice how "auto-restart" and settings
    behave together.
  - Python docs: the venv section (your own little box of toys) and
    the basics of reading start-up flags.
  - python-dotenv README (it is short). Then write ONE line in
    BUILD_LOG.md about why .env stays secret and .env.example does not.

SEARCH
  - "fastapi run programmatically uvicorn port env var"
  - "uvicorn workers reload env vars"
  - "curl show response headers -i -v"   (learn -v well - you will live in it)

PROVE IT
  - Three helpers run. Ask each one: the "who am I" answer is different,
    "/health" is fast, and "/work?ms=300" measures about 300ms (use the
    timing trick in the ask-command, or a stopwatch).
  - Search your code for any hardcoded port or name outside the settings
    reader: ZERO hits in the parts that matter.
  - You can say what happens if two helpers try to use the SAME door at
    once - including the exact grumpy message the computer gave you when
    you tried it on purpose.

OOPSIES
  - Writing THREE copies of the helper. One file, three starts.
  - Putting the nap in a "blocking" place, so the whole playground freezes
    while one helper naps - then wondering why "/health" stops answering
    during "/work". Read FastAPI's async/sync page NOW and decide which
    kind "/work" is, and why.
  - Skipping the "same door" experiment. A grumpy message you have SEEN
    beats ten you have only read about.

------------------------------------------------------------------------
  STEP 2 - THE MOST BORING DOOR HELPER EVER       (take turns, no checking)
                                                             (2 sittings)
------------------------------------------------------------------------

WHAT YOU WANT
  The door :8080 passes the ask to Sunny, then Buddy, then Rosie, then
  back to Sunny, and hands the helper's answer back as its own.

BUILD
  - src/config.py: read LB_PORT and the list of helpers from settings.
    Nothing hardcoded, no sneaky defaults for things that must be chosen.
  - src/pool.py: a Helper thing (name, address, and empty counting spots)
    plus the "group" that holds them.
  - src/strategies.py: take-turns choosing. Keep it simple first; you make
    it safe-not-broken in Step 3.
  - src/proxy.py: carry the ask (kind + path + extras + headers + inside)
    using httpx, and bring back the answer.
  - src/app.py: ONE catch-all door that accepts every path and every kind
    of ask, wired to the carrying part.
  - src/main.py: the start button (a flag for the door number, or settings
    only - pick one and say why).
  - First real entry in docs/architecture.md: one ask traced through YOUR
    real function names.

READ FIRST
  - httpx docs: the AsyncClient quickstart, THEN the "transports" page.
    Decide which one fits carrying an ask to a real address, and write WHY
    - because one talks to a pretend app and the other opens a real
    connection. That difference is the whole point here.
  - httpx docs: timeouts. Our door must never wait forever on a sleeping
    helper. Pick your waiting times and say why.
  - Starlette docs (FastAPI is built on it): how doors and asks work, and
    especially how to send a body in pieces.
  - MDN: X-Forwarded-For and Host - what to add or keep before passing the
    ask along, since WE are now the in-between.

SEARCH
  - "fastapi catch all route proxy httpx async example"
  - "httpx ASGITransport vs AsyncClient base_url"
  - "fastapi proxy request body streaming forward"
  - "<paste your exact error here>"   (httpx errors name the step clearly)

PROVE IT
  - Ask the door 5 times: the helpers go 1-2-3-1-2, and the answer says
    which helper gave it. Your answer's headers look clean - name which
    "hop-by-hop" headers you secretly removed, where, and why.
  - Send an ice-cream ask (POST) with a small note inside: the helper
    receives the note unharmed (print it helper-side to prove it) and the
    size matches.
  - Turn off Buddy completely. Now asks FAIL. That is EXPECTED here -
    there is no checking yet. Count the failures by hand: it should be
    exactly 1 in 3. WRITE THAT NUMBER DOWN. Step 3 must do better.
  - The traced paragraph in architecture.md uses your REAL function names.

OOPSIES
  - Reading the whole body into memory and calling it done. Okay in Step 2
    ONLY IF you write a "fix this in Step 4" note and know which docs page
    fixes it. If you cannot name the page, you are not "allowing" it, you
    are ignoring it.
  - Passing Host along without a thought (helpers get confused), or
    passing Connection: keep-alive along (that is hop-by-hop - read the
    RFC part again). Everybody hits one of these.
  - Using the slow "blocking" httpx style inside fast code. That quietly
    makes all kids wait in one line and teaches you nothing about doing
    many things at once.
  - Only testing easy asks. Ice-cream asks break in their own way. Test
    both kinds from Step 2 on.

------------------------------------------------------------------------
  STEP 3 - FOUR CHOOSING RULES + SAFE WHEN MANY KIDS COME AT ONCE
                                                          (3 sittings)
------------------------------------------------------------------------

WHAT YOU WANT
  Four choosing rules behind ONE plug shape, each correct even when many
  kids arrive at the same moment, each with tests that shout if you break
  it.

BUILD
  - Add weighted and fewest-waiting to take-turns. Added rule stays too.
    Every rule picks from AWAKE helpers only.
  - Fix the take-turns boo-boo: two kids at once can grab the same turn
    number. Pick a lock (a grown-up "one at a time" gate) or another safe
    trick, and defend your choice in algorithm_notes.md.
  - Count "how many kids are waiting" per helper: add 1 when the turn
    starts, take 1 away at the very end - ALWAYS, even if something goes
    wrong. Find out why "at the very end, always" matters, and write it
    down.
  - tests/test_strategies.py: no internet needed. Feed pretend groups;
    check the exact turn order for take-turns and for weighted 3:1:1; for
    fewest-waiting, check the least-busy helper wins; run a small
    many-kids-at-once test and check the order stays fair.

READ FIRST
  - Python asyncio docs: the "Lock" page (the one-at-a-time gate). If
    "await" still feels fuzzy, re-read the coroutines/tasks pages -
    this step is where fuzzy becomes broken.
  - The smooth weighted rule you found in Step 0. Build from the
    pretend-code, not from memory of how it behaves.
  - pytest docs: fixtures, parametrize, and testing fast code (pick the
    async test helper that ships with FastAPI, or the other one - say why).

SEARCH
  - "smooth weighted round robin nginx algorithm pseudocode"
  - "asyncio lock vs no lock single thread event loop"
  - "pytest async test fixture anyio pytest-asyncio"
  - "least connections load balancing implementation in flight requests"

PROVE IT
  - Weighted 3:1:1 over 50 asks: counts are about 30/10/10 (plus or minus
    1), and the turns are SPREAD OUT (never the same helper three times in
    a row). Show the actual order.
  - test_strategies.py is green, and every test NAME says what it protects
    ("test_take_turns_visits_each_helper_once"), not just "test_rr".
  - Break a test on purpose (flip the weighted math), watch it go red, put
    it back, watch it go green. Show both runs. A test you have never seen
    fail is just decoration.
  - algorithm_notes.md has one paragraph per rule: what it is good at,
    your key line, and when it loses.

OOPSIES
  - Building weighted as "3 for Sunny, then 1 for Buddy, then 1 for
    Rosie". That clumping is exactly what smooth-weighted exists to
    prevent. Step 5's proof will catch it.
  - Counting waiting kids without the "always take 1 away at the end"
    part. One error and the number drifts forever - then "fewest-waiting"
    is choosing based on a lie. Make something go wrong on purpose once
    and check the number recovered. Write it in chaos_log.md.
  - Checking exact turn ORDER inside a many-kids-at-once test. Order
    checks belong to the simple case; for many-at-once, check FAIRNESS
    (nobody gets way more than their share), not positions.

------------------------------------------------------------------------
  STEP 4 - CARRYING BIG THINGS, WAITING, AND ASKING AGAIN SAFELY
                                                          (3 sittings)
------------------------------------------------------------------------

WHAT YOU WANT
  The carrying part handles big and slow bodies, sleeping helpers, and
  RULE 6 (only safe asks get repeated) the way a real Door Helper would -
  and you can prove each one.

BUILD
  - Carry in pieces both ways: pass the body along as it arrives, and
    send the answer back in pieces too. Check it with a BIG transfer and
    watch your memory stay flat (watch the process size or count the
    pieces). Do NOT buffer it all and just say it streams.
  - Waiting times from settings: a short "can I even reach you" time and a
    sensible "how long for the answer" time. A sleeping helper should fail
    FAST, not hang forever.
  - Ask-again ONCE on a DIFFERENT helper, for safe kinds only, when the
    connection breaks or the helper says "sorry". Put the RULE 6 sentence
    in a comment right AT that line.
  - A name tag on every ask; add your own if the kid forgot one. Add the
    kid's "where I came from" note (X-Forwarded-For) - read the safety
    part about not blindly trusting it.
  - tests/test_proxy.py: start the door app + two pretend helpers (one
    awake, one asleep); check safe asks get retried onto the awake one,
    ice-cream asks do NOT, and the "sorry" answer is your own clean note.

READ FIRST
  - httpx: streaming asks and answers, fine-tuning the waiting times, and
    the error FAMILY (the names of what can go wrong) - your ask-again
    decision switches on those names, not on the text of a message.
  - MDN: "sorry" answers 502 vs 503 vs 504 - which one is yours when the
    helper refuses, times out, or is skipped-and-gone? Decide and write it
    down.
  - Starlette: how to read a body in pieces and send a body in pieces.
  - MDN: the X-Forwarded-For part about faking/trusting.

SEARCH
  - "httpx async streaming proxy request body chunks"
  - "httpx connect timeout vs read timeout proxy dead backend"
  - "x-forwarded-for append proxy real client ip security"
  - "fastapi testclient httpx ASGITransport test proxy"

PROVE IT
  - Send a 100MB body through the door. The door's memory stays flat
    (show the number before / during / after), and the helper gets ALL the
    bytes (the fingerprints match).
  - Turn off Buddy, run 30 safe asks: ZERO failures (the retry saved
    them), and the tally board shows the retries happened. Turn Buddy back
    on.
  - Same test with ice-cream asks: the failures ARE visible (about 1 in 3
    while Buddy is off, until Step 5 shrinks that window) - and the "no
    retry" test is green.
  - You can point at the exact line that chooses between 502 / 503 / 504
    and say which situation each one covers.

OOPSIES
  - Asking again on a "took too long" answer for safe asks by default: the
    helper may have ALREADY done the work. Decide on purpose (a setting,
    default careful) and write the trade-off in architecture.md.
  - Forgetting to fix the size number when you send in pieces. The twin
    bug (sending an OLD size number) causes horrible hangs. The cure is
    understanding, not a magic line you found online.
  - Testing ask-again only with pretend helpers, never against a real
    turned-off door. Do BOTH: pretend for the logic, real for the truth.
  - Swallowing errors to "return something". Map each error to a clear
    answer on purpose, or your tally board will lie about failures.

------------------------------------------------------------------------
  STEP 5 - KNOCK-KNOCK CHECKS AND AUTOMATIC SKIPPING     (3 sittings)
------------------------------------------------------------------------

WHAT YOU WANT
  The door notices sleeping helpers within seconds, WITHOUT any kid
  traffic, and welcomes them back when they wake - so real failures drop
  toward zero, even for ice-cream asks, and the "dead window" you
  measured in Steps 2 and 4 disappears.

BUILD
  - src/health.py: one quiet background helper (started when the app
    starts up, NOT from a random import line - find out why), looping:
    for each helper, knock on "/health" with a short wait; skip or welcome
    based on how many misses/wins in a row, using numbers from settings.
  - The group only hands out AWAKE helpers. If ALL are asleep, say a clean
    "everyone is busy, sorry" answer. Decide this now - it WILL happen in
    a demo.
  - Skipping and welcoming are written down with clock times, and shown by
    the tally board.
  - Helpers get "/crash?seconds=N" (the health door goes quiet for N
    seconds, the helper still stands there). This is your fake-broken
    button for every demo.
  - tests/test_health.py: with the knock-every-dot-1s setting, check skip
    after the chosen misses, welcome after the chosen wins, and that the
    tally board shows each change within a few knocks.
  - docs/chaos_log.md: first three entries - break Buddy, break ALL of
    them, then break-and-fix Buddy over and over - each with the clock
    times of what the tally board showed.

READ FIRST
  - FastAPI: "lifespan" (when the app wakes up and goes to sleep) - this
    is where the knock-knock helper starts and stops. Read the asyncio
    part on stopping tasks cleanly.
  - asyncio docs: "sleep" vs "wait_for" (your knock needs a time limit and
    must be stoppable), "gather with errors kept" if you knock on everyone
    at once, and how tasks get cancelled.
  - Think about the knock that ITSELF times out - is that a miss? Decide
    and write it down.

SEARCH
  - "fastapi lifespan startup background task asyncio create_task"
  - "asyncio wait_for timeout gather return_exceptions"
  - "health check consecutive failures flap damping load balancer"
  - "fastapi graceful shutdown cancel background tasks"

PROVE IT
  - THE demo: 60 safe asks while you break Buddy at second 5 (for 20
    seconds) and fix it at second 25. Show the timeline: zero kid
    failures after the FIRST knock, Buddy skipped in about (every-few-
    seconds + misses), welcomed back after it wakes, all visible on the
    tally board. Write exact times in chaos_log.md.
  - Same demo with ice-cream asks: the failure window is now bounded by
    how fast we NOTICE, not by the ask-again rule. Compare it to Step 4's
    number and write BOTH down. That difference IS the lesson.
  - Break ALL helpers: clean "everyone busy" answer, door stays alive,
    recovers when they wake. Show it.
  - Break-and-fix Buddy in a loop for 30 seconds: nothing goes crazy, the
    counts add up, and no leftover background tasks are hiding (check
    the list of tasks before and after).

OOPSIES
  - The knock-knock loop DYING when ONE helper errors. One sleepy
    helper's timeout killing the whole loop is the classic boo-boo.
  - Skipping a helper after ONE miss: one lost whisper, and your group
    flails. "Misses in a row" is the fix; set it from settings and say why
    the default is a good one.
  - Starting the knock-knock helper from a random import line. It works
    in tiny scripts, then breaks under real servers and tests and you
    will not know why until you read the lifespan page. Read first.
  - A knock every 0.1s but each knock allowed to wait 1s: your loop
    starts overlapping itself. Decide if that is allowed and say why.
  - Trusting "/health" while a helper is overloaded - awake and not-busy
    are DIFFERENT things. Fewest-waiting (Step 3) is your busy signal.
    One paragraph on this in algorithm_notes.md.

------------------------------------------------------------------------
  STEP 6 - THE TALLY BOARD AND THE BIG WINDOW            (2-3 sittings)
------------------------------------------------------------------------

WHAT YOU WANT
  One glance answers: who is awake, who is getting the kids, how fast,
  and what just changed - without digging anywhere.

BUILD
  - src/metrics.py: per-helper counts (turns, good, bad, retries, skips),
    a SMALL memory of how-fast (say how you chose the size - a clever
    sample or the last N), and the middle/slow times (p50/p95/p99).
  - Keep the counts safe when many kids come at once. Say which adds
    happen on the single fast thread and what would break with many
    threads later. One paragraph in architecture.md.
  - /stats: the whole tidy snapshot (per helper + totals + which rule is
    active + recent skips/welcomes). Decide: take a clean frozen copy, or
    accept a slightly mixed snapshot and say why that is okay.
  - static/dashboard.html: ONE plain file that peeks at /stats every
    second, shows an awake dot / speed / a little bar chart, and has a
    dropdown to swap the rule LIVE (no restart).
  - scripts/load_test.py: a many-kids machine that hits "/work" with a
    chosen nap time and a fixed "kids per second" mode.

READ FIRST
  - Locust docs: your first locustfile, and the "run without the web page"
    + fixed-rate pages. You will use wait_time and task weight.
  - MDN fetch() + a CSS flexbox reminder if needed. The window is
    DELIBERATELY boring: every fancy thing costs you time.
  - Prometheus docs: histogram vs summary and their "careful about
    quantiles" note. Read it even though we are not exporting yet - your
    memory-of-speed will be compared to these later; know what a "bucket"
    is.

SEARCH
  - "reservoir sampling latency percentiles implementation"
  - "locust fixed requests per second target rps example"
  - "javascript fetch interval update dashboard vanilla js"
  - "prometheus histogram vs summary quantiles"

PROVE IT
  - The tally board adds up: total turns == sum of per-helper turns. Say
    where retries are counted. Decide and write it down.
  - Weighted 3:1:1 under 1000 asks from the many-kids machine: the real
    split is within 5% of target, shown as a little table (this finishes
    DONE-5).
  - Speed sanity-check: the middle number from /stats is in the same
    ballpark as hand-timed asks. If not, find the bug before moving on.
    State your memory size and what it costs.
  - The big window shows the Step 5 break-helper demo live: the dot flips
    red, the kids reroute to the awake helpers, the dot flips green when
    it wakes. Swapping the rule mid-traffic drops ZERO asks.

OOPSIES
  - Keeping every single speed number forever: memory grows until the
    machine dies. Use a SMALL memory from day one.
  - A window so fancy it becomes the whole project. ONE file, no build
    step, no framework. The Door Helper is the project.
  - Swapping the rule and breaking the ONE ask that was holding the old
    rule. Swap by flipping ONE name at a time - and know why that is safe
    on a single fast thread.
  - Counting speeds only when everything goes well: errors skip the
    counting and your failure rate reads 0% during a break. (The 1-in-3
    number from Step 2 should have made you suspicious.)

------------------------------------------------------------------------
  STEP 7 - BOXES, AND FINDING FRIENDS BY NAME            (2 sittings)
------------------------------------------------------------------------

WHAT YOU WANT
  ONE command starts the Door Helper + three helpers, each in its own
  little box, all able to find each other BY NAME - and adding a helper is
  a settings edit, not a code change.

BUILD
  - One box recipe (box = a lightweight container, a program in its own
    tidy room): a small Python base, install the shopping list, then run
    ONE of two commands. The SAME box runs the door OR a helper. Say the
    trick: the command can be overridden.
  - A "start everything" file: one shared pretend-playground; the door +
    three helpers; a "are you healthy?" check for each helper; a
    "wait until healthy before starting" rule; settings for names and nap
    times. The door now finds helpers BY NAME ("sunny:8000"), NOT by house
    address. INSIDE a box, "localhost" means the box ITSELF. That sentence
    IS the step. Learn it cold.
  - Adding a helper: start a 4th box against a 3-helper settings list.
    Watch what your settings do. Then make the list read however many
    names it is given, and note the result in architecture.md. (Finding
    friends by name, the simple form, is "the box's own phone book ->
    your group builder reads however many names are there".)
  - A "do not copy this into the box" list (your secret settings, your
    own toy box, junk files).

READ FIRST
  - Docker docs: the box-recipe reference (only the commands you use) and
    the "start everything" reference for: pretend-playgrounds, "wait until
    healthy", "are you healthy?", scale, and settings.
  - Docker docs: "Networking overview" - a shared pretend-playground lets
    boxes find each other BY NAME. This is the page that cures the
    localhost-boo-boo.
  - Docker docs: the "two-stage" box idea - read it even if you skip it.
    Know the word.

SEARCH
  - "docker compose healthcheck depends_on condition service_healthy"
  - "docker compose scale service env var backends list"
  - "docker container localhost vs service name networking"
  - "python slim docker image uvicorn fastapi dockerfile"

PROVE IT
  - A friend copies your project and runs ONE command. Ask the door 5
    times: all three helpers take turns. The "what is running" list shows
    all four boxes healthy.
  - Turn off Buddy's box mid-traffic: the Step 5 demo runs the same way in
    boxes. chaos_log.md gets the box timeline with real clock times.
  - From the start-everything file, you can explain: which pretend-
    playground the traffic uses, how the door finds "sunny", and what
    happens to asks in progress when a box stops.
  - It is ONE box recipe, two commands. Show the list of boxes: you did
    not build a separate recipe per role.

OOPSIES
  - Writing a house address (localhost:8001) into the boxed door's
    settings: inside the box, that is the door ITSELF. The "find friends
    by name" page is the cure. Read it before debugging for an hour.
  - No "are you healthy?" check on helpers, so the start-everything file
    says they are up before they have really opened their doors. The door
    starts, finds nobody home, and the skip logic races the start-up.
    The check + "wait until healthy" fixes the race every time.
  - Copying your SECRET settings into the box. The "do not copy" list is a
    safety file, not a convenience. Prove it: run the box and look at what
    it is carrying - your secrets should not be there.
  - Adding a box while your settings only know 3 helpers: SEE the honest
    failure first, THEN make the group builder read however many names it
    gets, and print the final list at start-up so you can see it.

------------------------------------------------------------------------
  STEP 8 - MANY KIDS AT ONCE: PROVING THE RULES           (2 sittings)
------------------------------------------------------------------------

WHAT YOU WANT
  Numbers, not feelings: how each rule behaves under load, in little
  tables YOU made, with a machine you can run again any time.

BUILD
  - The full many-kids machine: a fixed "kids per second" shape, "/work"
    with a chosen nap pattern (make ONE helper slow on purpose), a
    no-web-page run, and a results folder (kept out of sharing) of
    per-run spreadsheets.
  - The run list (all saved into docs/algorithm_notes.md):
      1. Take-turns, all awake, equal naps -> equal split (sanity check).
      2. Take-turns vs fewest-waiting, naps 900/50/50ms, 100 kids per
         second, 60s -> fewest-waiting wins on the slow tail; the table
         shows by how much.
      3. Weighted 3:1:1, equal naps -> split within 5% (already done in
         Step 6; do it again under load now - staying within tolerance
         under load is the lesson).
      4. P2C vs take-turns under the slow pattern -> the waiting you see
         IS the point; one paragraph on why P2C is almost as good as
         "fewest-waiting" without knowing everyone's numbers.
  - The break-under-load run: 100 kids per second; break Buddy for 30s at
    20s in; capture the slow-tail time and error rate before/during/after
    (DONE-7).

READ FIRST
  - Locust docs: no-web-page runs, spreadsheet reporting, a custom shape
    for the fixed rate, and how its OWN numbers are computed (so you know
    what your numbers include).
  - Little's Law (one page, anywhere) - to sanity-check that your math
    (kids-per-second x nap-time) matches the "waiting now" you see in
    /stats.

SEARCH
  - "locust headless csv result fixed rps load shape"
  - "little's law load testing sanity check"
  - "tail latency least connections power of two choices"

PROVE IT
  - The run list exists with REAL spreadsheets behind every table (file
    names written next to each table; no orphan numbers).
  - The 8.2 table shows fewest-waiting beats take-turns on the slow tail,
    with numbers you could defend out loud.
  - Break-under-load: the error spike and how long it lasts are visible
    and explained (how fast we notice + the ask-again rule), tying Steps
    4 and 5 together.
  - Little's Law check: the "waiting now" you predicted is close to the
    /stats number; explain any gap in one line.

OOPSIES
  - Load-testing everything on ONE computer and acting like the numbers
    are the whole internet. Your numbers are only COMPARISONS; write that
    caution on every table. (Boxes make it a little more honest, still one
    machine.)
  - Running the door and the many-kids machine in the same little window,
    fighting for the same fast thread. Separate windows - and even then,
    your machine is not the whole internet.
  - Cherry-picking the best run. Three runs each, show the middle one. One
    cherry-picked table is a lie with nice borders.
  - Forgetting to reset the tally board between runs, or not labeling
    which run a spreadsheet belongs to. Unlabeled numbers are unreadable a
    week later.

------------------------------------------------------------------------
  STEP 9 - CALLING FOR MORE HELPERS (THE FINAL BOSS)     (3-4 sittings)
------------------------------------------------------------------------

WHAT YOU WANT
  When the line is very long, a NEW helper joins by itself and the kids
  spread out. When the line gets short, one helper goes home - all driven
  by YOUR signals, all visible on the tally board.

BUILD
  - Pick ONE "we need help" signal: kids-per-second per helper, or the
    slow-tail time, or how many are waiting. Compute a small average over
    a window. Say why you picked it and why that threshold.
  - Adding-helpers path (do this FIRST): the door has a "call for help"
    button; when pressed it starts a new helper (name + door number from a
    range) with settings, waits for "/health", and adds it to the group.
    Under steady load: the slow tail recovers after the new helper joins.
    Capture it.
  - Sending-helpers-home path: DRAIN, do not yank. Take the helper out of
    the group, let the asks-in-progress finish, THEN stop the program.
    Losing in-progress asks is the classic boo-boo; test for it.
  - A "wait before acting again" timer (so we do not call for help and
    send someone home over and over at the edge). Set it; say why.
  - The whole loop on the tally board (the signal, the thresholds, the
    timer, what is about to happen) and in chaos_log.md with clock times.

READ FIRST
  - asyncio docs: starting other programs from your program, and "task
    groups" (keeping a tidy group of background jobs) for the lifetime of
    the adding/sending-home jobs.
  - Docker command line: how to add boxes from a script; the "what
    happened" event list if you want to react to it.
  - Kubernetes docs, the "auto-scaling" page - READ ONLY, for words only:
    what the real grown-ups call the signal, the wait timer, and the
    target number. You are building a toy version; knowing the real words
    is the point.

SEARCH
  - "asyncio create_subprocess_exec environment variables example"
  - "docker compose scale up programmatically script"
  - "horizontal pod autoscaler stabilization window cooldown"
  - "graceful shutdown drain in-flight requests load balancer"

PROVE IT
  - Demo: steady load at 100 kids per second, make naps longer, watch the
    signal cross the line, a 4th helper appears within one check or two,
    the kids spread out again - show the timeline.
  - Load drops, signal crosses the low line, ONE helper drains: ZERO asks
    lost (you counted waiting asks before/after), the program stops after
    draining - show the timeline.
  - Flap guard: put the load EXACTLY on the line - nothing wobbles up and
    down; explain the wait timer with the tally-board trace.
  - The final architecture.md drawing includes the "call for helpers"
    loop; every magic number (window, line, timer, door range) is in
    .env.example with a friendly comment.

OOPSIES
  - Scaling on a single instant: one burst and you spawn/die/spawn. Average
    the signal over a window (even a simple 10s average); the wait timer is
    the belt, the window is the braces. You need BOTH.
  - Orphaned helper programs: helpers that outlive the door when you press
    Ctrl-C. Handle the stop signal, tidy up your child programs, and
    check the running list after - this is a real bug you WILL hit.
  - Sending a helper home and dropping the asks still in progress: drain
    using the "waiting" counter you built in Step 3 - THAT is why it was
    built.
  - Yanking instead of draining: the "/work" nap makes lost asks visible.
    Test draining against a LONG nap (2s), not against instant answers.

------------------------------------------------------------------------
  AFTER STEP 9
------------------------------------------------------------------------

You will have built, with your own hands, the core of what Nginx, HAProxy,
and the cloud Door Helpers do for you - plus a toy auto-scaler. Fun next
things, in order, only if you want them:

  1. Also notice broken helpers from REAL traffic, not just knocks.
     Compare how fast each way spots trouble.
  2. Sticky kids: remember a kid so they always get the SAME helper.
     Teaches you what you give up (perfect fairness) to get something
     (helper memory). Add a little memory to a helper to SEE it.
  3. A "one kid at a time, please" line at the door (rate limiting).
  4. Show your numbers in the fancy grown-up tools (Prometheus + Grafana)
     and compare to your own tally board.
  5. A second door with a backup, for real grown-up high availability.
  6. Only then: put a helper + door on a real internet computer and run
     the many-kids tests again. Your own computer FIRST, always.

========================================================================
  START STEP 0 AFTER READING: README_FIRST.md, then PROFESSOR.md, then
  this file, then skim HOW_TO_SEARCH_DOCS.md. Then go.
========================================================================
