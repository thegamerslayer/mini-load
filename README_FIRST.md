========================================================================
  READ ME FIRST!  MINI-LOAD
  "The Friendly Door Helper"
  A tiny helper that shares the work, built with your own two hands.
  No magic boxes. No grown-up shortcuts. No robot writing your code.
========================================================================

  (This is the kid-friendly telling of the project. The original
   grown-up wording still lives in archive/original-course/ if you ever
   want to peek. Same course. Simpler words.)

>>> START HERE: read this whole page once. It takes about 20 minutes.
>>> Then open ROADMAP.md and do Step 0. Do NOT write any code until
>>> Step 0 is done. Step 0 is just thinking and drawing. That is on purpose.

------------------------------------------------------------------------
  PART 1 - THE BIG IDEA
------------------------------------------------------------------------

Imagine a playground with three helpers. Kids keep running up and
asking for a turn. If every kid runs to the SAME helper, that helper gets
tired and the line gets long. The other two helpers just stand there.

So we build one friendly helper at the door. Every kid talks to the door
helper. The door helper quietly picks a helper who is NOT busy, and sends
the kid there.

You are going to build that door helper. With your own hands.

  The grown-up name for it:  a "reverse-proxy load balancer".
  The kid name for it:       the Door Helper.
  (We will use both. Learning the grown-up name is the whole point.)

Here is the magic trick at the end. You will pull a helper away while
kids are still coming in. Nothing bad happens. The kids keep getting
their turns. And you can point at the exact line of your own code that
made that happen.

That is the whole game. Do the trick, and explain it.

WHAT YOU ARE REALLY LEARNING (grown-up words, so you sound smart later)
  sharing work between helpers  ....  load balancing
  passing a turn along          ....  reverse proxying and streaming
  doing many things at once     ....  async concurrency
  "are you awake?" checks       ....  health checking and failure detection
  counting who is busy          ....  active connections
  safely asking again           ....  retries and idempotency
  the tally board               ....  observability and metrics
  putting helpers in boxes      ....  containers and service discovery
  lots of kids at once          ....  load testing

------------------------------------------------------------------------
  PART 2 - THE RULES (promise these to yourself)
------------------------------------------------------------------------

  RULE 1.  We use Python + FastAPI + httpx. Nothing else does the work.
           No Nginx. No HAProxy. No ready-made sharing box.
           We are building the small version of that thing, so we
           understand what it does for us.

  RULE 2.  The Door Helper really passes the turn along. It does not just
           point and say "go over there." It takes the kid's request,
           carries it to the helper, carries the answer back, and hands
           it over as if the answer came from the door itself.
           (Grown-up name: a reverse proxy, not a redirect.)

  RULE 3.  The three helpers are dumb on purpose. They can only do three
           things: say who they are, say "I am awake", and "do some work
           for N milliseconds". ALL the smart stuff lives in the Door
           Helper. That is the whole design.

  RULE 4.  The Door Helper checks on helpers by itself. Every few
           seconds it knocks: "knock knock, are you awake?"
           If a helper misses several knocks in a row, we skip that
           helper. When it knocks back again, we welcome it home.
           We do NOT wait for a kid to get hurt before noticing.

  RULE 5.  If we do not count it, it did not happen. For every helper we
           count: how many turns, how many good, how many bad, how fast,
           how many kids are waiting right now. One page (/stats) shows
           the whole tally board.

  RULE 6.  Asking again is only allowed for SAFE asks.
           "What time is it?" is safe - ask again, no harm.
           "One ice cream, please!" is NOT safe - ask twice and you get
           two ice creams and a tummy ache.
           (Grown-up: GET/HEAD/PUT/DELETE may be asked again once;
            POST never is. We write this rule right in the code.)

  RULE 7.  Every knob comes from a setting, not from your memory.
           Ports, weights, how often we knock, how many misses before we
           skip a helper - all from settings. And you can pick the
           sharing rule with a flag when you start up.

  RULE 8.  NOBODY writes your code for you. Not me, not any robot.
           I read your code. I tell you the name of the thing and which
           page to read. I do not hand you code to paste.
           (Full version in PROFESSOR.md. This rule is the whole course.)

  RULE 9.  One helper per box later on. When we get to boxes, making MORE
           helpers is changing ONE number. That is the lesson.

------------------------------------------------------------------------
  PART 3 - THE PICTURE
------------------------------------------------------------------------

                          a kid (browser, curl, or a load tester)
                             |
                             v
                 +-----------------------+
                 |   THE DOOR HELPER     |   door :8080
                 |   (this is YOUR code) |
                 |   - pick who is next  |
                 |   - carry the turn    |
                 |   - knock knock check |
                 |   - the tally board   |
                 +-----------+-----------+
              +--------------+--------------+
              v              v              v
        +---------+    +---------+    +---------+
        | Sunny   |    | Buddy   |    | Rosie   |
        | :8001   |    | :8002   |    | :8003   |
        +---------+    +---------+    +---------+

  Everything from the kid to the answer back is YOUR code.
  (Later, boxes are added at the very end - and even then, just boxes.)

------------------------------------------------------------------------
  PART 4 - WHAT EACH PART MUST DO
------------------------------------------------------------------------

THE DOOR HELPER'S CARRYING PART  (src/proxy.py)
  - Carry the whole ask: the kind of ask, the path, the extras, the
    headers, and the stuff inside. Do not drop any of it.
  - Carry it in small pieces, not all at once. A giant pile of bricks
    should travel brick by brick, not as one heavy pile we hold in our
    arms. (Grown-up: stream the body; do not buffer it.)
  - Put a little name tag on every ask so we can follow it. If the kid
    forgot the name tag, make one.
  - The answer must say WHICH helper gave it.
  - If the chosen helper is asleep or gone: for SAFE asks, quietly ask a
    different helper once (RULE 6). Otherwise, say a clean "sorry, try
    again later" kind of answer. NEVER a scary error dump.

THE CHOOSING PARTS  (src/strategies.py)
  Four ways to choose. Same plug, four shapes - like four toy heads on
  one body. You can swap the head while the toy is running.
    1. Take turns in a circle.        (round robin)
       Careful: with many kids at once, two kids might grab the same
       turn number. Find out why, then fix it.
    2. Stronger helper gets more turns, spread out smoothly - NOT
       three turns in a row to the strong one. (weighted round robin)
    3. Send the next kid to whoever has the FEWEST kids waiting.
       (least connections)
    4. Pick two helpers by luck, send to the one with fewer waiting.
       Fewer lines than you think. Very clever. (P2C)
  - All four must hand out ONLY awake helpers.

THE KNOCK-KNOCK PART  (src/health.py)
  - One quiet helper-in-the-background knocks on every helper's "/health"
    door every few seconds. It is not part of the kid's path. It runs
    alongside.
  - Miss N times in a row -> skip the helper. Come back N times in a
    row -> welcome it home. You choose N. Write down why.
  - Skipping and welcoming are written down and counted, never silent.

THE TALLY BOARD  (src/metrics.py)
  - Count and time everything, per helper and overall.
  - Keep at least the "middle one" and the "roughly-the-slow-tail" times
    (grown-up: p50, p95, p99). You cannot keep every single time forever
    - your notebook would explode. Keep a small clever sample instead and
    say how you chose it.
  - One page, /stats, shows everything as a tidy list. If the tally board
    cannot even tell you how it is doing, it is just decoration.

THE BIG WINDOW  (src/dashboard.py + static/)
  - One simple page that peeks at /stats every second.
  - Shows who is awake, who is busy, how fast, and lets you swap the
    choosing rule without restarting.
  - ONE plain page. No fancy toy boxes, no frameworks. The Door Helper
    is the project. Do not let the window become the project.

THE THREE HELPERS  (backends/)
  - One small program, started three times with different settings.
    NOT three copies. One file, three starts.
    1. Say who you are.
    2. "/health" answers fast: "yep, awake." Nothing more.
    3. "/work?ms=N" naps for N milliseconds, then says done.
    4. "/crash?seconds=N" pretends to be asleep for N seconds while
       still standing there. This is our fake-broken button for demos.
       (We break things ON PURPOSE. That is the fun part.)

THE BOXES  (later, Step 7)
  - One box recipe. Each helper gets its own little box. The Door Helper
    finds them by their NAME ("Sunny"), not by a house address.
    Finding friends by name instead of by address - and you can explain
    why that matters inside boxes - is the whole lesson of Step 7.
  - (Grown-up name: containers and service discovery.)

------------------------------------------------------------------------
  PART 5 - THE FILES YOU WILL MAKE (you make them all in Step 1)
------------------------------------------------------------------------

  mini-load/
    README_FIRST.md          <- this page
    ROADMAP.md               <- the 10 steps
    PROFESSOR.md             <- the working-together rules
    HOW_TO_SEARCH_DOCS.md    <- how to find answers in the real docs
    BUILD_LOG.md             <- your diary of every session
    requirements.txt         <- the shopping list
    .env.example             <- settings we share with everyone
    .env                     <- settings that are just ours (kept secret)
    src/                     <- everything YOU write lives here
      __init__.py
      config.py              <- read the settings
      pool.py                <- who is in the group + how busy
      strategies.py          <- the four choosing rules
      health.py              <- the knock-knock helper
      metrics.py             <- the tally board
      proxy.py               <- the carrying part
      dashboard.py           <- /stats and the big window
      app.py                 <- glue that ties it all together
      main.py                <- the start button
    backends/
      __init__.py
      server.py              <- the dumb helper (one file, three starts)
    static/
      dashboard.html         <- the big window (one plain file)
    tests/
      test_strategies.py     <- tests for the choosing rules
      test_proxy.py          <- tests for the carrying part
      test_health.py         <- tests for the knock-knock part
    docs/
      architecture.md        <- your drawing and your WHYs
      algorithm_notes.md     <- one note per choosing rule + your numbers
      chaos_log.md           <- every time you broke something, and what happened
    scripts/
      load_test.py           <- the many-kids-at-once machine

  You may change the shape. If you do, say why in BUILD_LOG.md.

------------------------------------------------------------------------
  PART 6 - WHAT "FINISHED" MEANS
------------------------------------------------------------------------

  Finished means ALL of these are true. Not "mostly". Not "kind of".

  DONE-1   A friend can copy your project, run ONE command, and get the
           Door Helper + three helpers running. Every command is written
           down in docs/architecture.md.
  DONE-2   Ask the door 5 times in a row and see all three helpers take a
           turn in the right order.
  DONE-3   Take away Buddy while kids are asking. For safe asks, ZERO
           kids see a problem. The tally board shows Buddy was skipped,
           then shows Buddy come back by itself. You wrote the clock
           times down in chaos_log.md.
  DONE-4   Show, with real numbers, that "fewest waiting" beats "take
           turns" when one helper is slow. Table in algorithm_notes.md.
  DONE-5   Weighted 3:1:1 gives about 3 out of 5 to one helper over 1000+
           asks. Show the numbers.
  DONE-6   Ice-cream asks (POST) are NEVER asked twice. Safe asks are
           asked again once. You can say WHY in one sentence, and you
           have a test for both.
  DONE-7   With many kids at once: show the slow-tail time and the error
           rate before vs during a break. Explain the difference.
  DONE-8   You can swap the choosing rule while running. /stats shows it
           right away.
  DONE-9   BUILD_LOG.md has a row for every session, with the honest
           "I know it / I'm not sure / I skipped it" mark.
  DONE-10  You can draw the trip of one ask from the front door all the
           way back, from memory, naming every step it passes through.

------------------------------------------------------------------------
  PART 7 - HOW WE WORK TOGETHER
------------------------------------------------------------------------

  - YOU try first. Then YOU look in the real docs. Then YOU try the
    exact error again. Then YOU do a 2-minute experiment. THEN ask me,
    with all of that written down.
  - I answer with the NAME of the thing and WHERE to read about it.
    Not with code. (See PROFESSOR.md for the full ladder.)
  - If you are still stuck after two rounds, I show a tiny example.
    You close it, rewrite it from memory, and write the date in
    BUILD_LOG.md. Copying is not learning; rebuilding is.

========================================================================
  NEXT: open ROADMAP.md and start Step 0. About 24-30 sittings total.
  One short sitting a day beats one giant Sunday. A little every day
  wins. Really.
========================================================================
