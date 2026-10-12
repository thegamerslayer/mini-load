# CATCH_UP.md - read me first if you took a break

> I wrote this from REALLY LOOKING at your project on 2026-10-11 - not from
> memory. This page is a quick refresher, not the rulebook. It does not
> replace README_FIRST.md, ROADMAP.md, or PROFESSOR.md. It just gets you
> back to the spot where those make sense again.

> And remember the big promise in PROFESSOR.md: the code in `src/` and
> `backends/` is written by YOU. Nobody builds your Door Helper for you.

---

## 1. The whole project in 60 seconds

You are building a **Door Helper** - a friendly helper that stands at the
front and shares the work among three helpers behind it.

```
kid ──► YOUR DOOR :8080 ──► picks one helper ──► :8001 / :8002 / :8003
             │
             ├── choosing rule   (take turns, weighted, fewest-waiting, P2C)
             ├── knock-knock     (are my helpers awake? a quiet background job)
             ├── tally board     (who did what, how fast, the middle & slow times)
             └── /stats + window (the place you can SEE all of it)
```

The three helpers are deliberately dumb: they can only say who they are,
say "awake", and "work for N milliseconds". **All the interesting code lives
in the Door Helper.** That is the whole design: the parts that make Nginx /
HAProxy / cloud helpers interesting are the parts YOU write - so you can
explain them later instead of just naming a product.

The one demo that means "done": *take a helper away while kids are coming
in, and the kids keep getting served - and you can point at the exact line
of your own code that made that happen.*

---

## 2. The picture in your head: one ask, all the way through

This is DONE-10, and it is the fastest way to reload the project into your
brain. Follow one ask from the front door to the answer back:

| # | Step | Where it lives | The idea you are learning |
| --- | --- | --- | --- |
| 1 | A kid connects to `:8080` | the server | accepting a connection |
| 2 | FastAPI matches the ONE catch-all door | `src/app.py` | routing - why one door covers all paths and all kinds of ask |
| 3 | A choosing rule picks a helper | `src/strategies.py` | sharing rules |
| 4 | "waiting" count goes up by 1 | `src/pool.py` | counting busy-ness -> "fewest-waiting" |
| 5 | The ask is carried over | `src/proxy.py` (httpx) | passing an ask along, in pieces, hop-by-hop headers |
| 6 | The helper answers | `backends/server.py` | the dumb friend |
| 7 | The answer comes back, the tally board is updated | `src/metrics.py` | watching your own machine |
| 8 | "waiting" count goes down by 1 - ALWAYS, even if it broke | `src/pool.py` | why "at the very end, always" - safety when things go wrong |
| 9 | Meanwhile, the quiet job knocks on `/health` | `src/health.py` | finding trouble before a kid does |
| 10 | `/stats` answers "who is awake, who got kids, how slow" | `src/dashboard.py` | the machine watching itself |

If you can tell that table from memory, you have the SHAPE back. The rest
is details.

---

## 3. Where you ACTUALLY are - looked at, with proof

I ran your code. This is the truth, not the plan.

### Step status

| Step | Claimed | Actual |
| --- | --- | --- |
| Step 0 (look around, architecture.md) | - | **Not done.** `docs/architecture.md` is still the empty template with a "fill me in" note. The Step 0 questions are unanswered. |
| Step 1 (three helpers) | - | **Mostly done.** `backends/server.py` runs and works (see below). The fake-broken button is missing. |
| Step 2 (boring door) | - | **Started, does not run.** `src/proxy.py` breaks when you import it. `src/app.py` and `src/main.py` are empty (just a title line). |
| Step 3 (choosing rules + tests) | - | **Started.** One choosing rule exists. No tests. No "one at a time" gate. It does not filter to awake helpers. |
| Steps 4-9 | - | **Not started.** Empty files and templates. |

### What I saw when I ran it

The helper works (started on :8001 with the name "server1"):

```
GET /                 -> {"backend":"server1","port":8001,"delay_ms":0}   yep
GET /health           -> {"status":"OK"}                                  yep
GET /work?ms=300      -> 200, time_total=0.518s                          hmm, see below
GET /crash?seconds=5  -> 404 NOT IMPLEMENTED                             nope
```

That `/work?ms=300` took **0.52s, not 0.30s**. That gap is a fun little
warm-up puzzle. Run it 5 times with the timing trick and see whether the
FIRST one is the slow one. That gap IS the lesson.

The Door Helper half does not run at all:

```
$ python -c "import src.proxy"
ImportError: cannot import name 'round_robin' from 'src.strategies'

$ python -c "from src.config import load_config; print(load_config())"
(8080, [])      <-- the helper list is EMPTY, and it should have 3
```

### The three things in your way (ideas first, no code)

**1. `src/proxy.py` asks for something that does not exist.**
`strategies.py` has a THING (a class) called `RoundRobinBalancer` with a
CHOICE inside it called `round_robin`. But `proxy.py` does
`from src.strategies import round_robin` - like asking for the choice when
you only have the whole toy.
  - The idea: a choice that lives INSIDE a thing vs a choice that lives on
    its own. They are not the same, even though they share a name.
  - Decide: do you want your choosing rules to be plain "verbs" that take
    the group, or "things" that remember their own turn number? You need
    remembering for smooth weighted, so pick ONE and make all four match -
    because Step 3 says "four rules behind ONE plug shape".

**2. `src/config.py` reads settings that were never loaded.**
`load_config()` asks the computer for a setting called `BACKENDS`, but
nobody told it to READ the `.env` file first. `backends/server.py` does read
it; `src/config.py` does not.
  - The idea: the ORDER things happen. A file that reads settings the
    moment it is opened gets whatever was true AT THAT MOMENT.
  - The bigger question: WHO reads the settings file, and WHEN? One front
    door that reads settings once and passes them down beats every little
    file going fishing for itself.
  - Also: your `.env` today holds BOTH door settings (`LB_PORT`,
    `BACKENDS`) and helper settings (`SERVER_NAME=server2`,
    `SERVER_PORT=8002`). Two jobs in one file means whoever starts first
    wins the confusing ones. Write one sentence in BUILD_LOG.md about how
    you will keep them apart.

**3. There is no door to run.** `src/app.py` and `src/main.py` are empty,
so `run.py` at the top currently starts a HELPER, not the Door Helper.
  - The idea: start buttons. Two programs, two start buttons. Today there
    is only one, and it starts the wrong thing.

### Little wobbles I noticed (write them down, do not fix them all today)

- `strategies.py`: the turn counter is bumped INSIDE the choosing rule.
  Count-keeping is leaking into choosing. Step 6 will want counts in one
  place. Note it for Step 3.
- `strategies.py`: the helper list is passed to a cycle-maker built once at
  the start, so the group can never update it. I checked what really
  happens, and it is sneakier than "it froze a copy":
  - helpers added while the cycle is still on its first pass DO get picked
    up;
  - helpers added after the cycle runs out are NEVER picked up;
  - **a helper REMOVED from the group is STILL handed out forever** - after
    removing "B", the cycle kept returning "B" more than 30 times.
  So the Step 5 danger is real and worse than a plain frozen copy: a helper
  you kicked out stays in the rotation until you rebuild the toy. Working
  out WHY this happens is a genuinely good puzzle.
- `strategies.py`: no "one at a time" gate yet - that is the Step 3 bug the
  roadmap wants you to FEEL first. Do not fix it before you can say the
  exact who-does-what-when that breaks it.
- `pool.py`: the Helper thing has no "awake or not" state and no "how many
  waiting" number. Both are Step 3 / Step 5 work, and the file is shaped to
  receive them.
- `tests/`: all three test files are empty templates.
- **No save-history yet.** PROFESSOR.md says "save after every small
  piece", and your own "never delete an entry" promise needs a history.
  Setting up save-history here is maybe the best 30 seconds available to
  you. Do it first.

---

## 4. Is this a good project to learn from? Yes - here is why

Your worry is: "I always had a robot write it, so I never learned it." This
project is unusually good at fixing that, for four reasons:

1. **It has a written promise that the robot is not allowed to write
   `src/`.** That is exactly the discipline you said you were missing.
   Keep the promise and it works. Break it and this becomes just another
   video you watched.
2. **It comes with things that go wrong on purpose.** Break a helper, send
   a giant body, make a helper flaky. Learning mostly happens when the
   happy path STOPS - most tutorials hide that part.
3. **Every proof is a number.** "30 of 30 asks, zero failures, kicked out
   at 3.2 seconds" beats "it works". Numbers are what make a claim
   believable later.
4. **It is the small version of a real product.** Passing asks along,
   noticing trouble, weighted sharing, watching yourself, draining gently,
   calling for more helpers - this is the everyday vocabulary of the
   grown-up world, and you will have BUILT each piece instead of only
   reading about it.

The one thing this project teaches LESS well: the "data" half - big
databases, saving things, keeping things safe. This teaches the
"traffic/infrastructure" half. That is a real half, and it is the half most
courses skip. Plan a second small project later for the data half.

---

## 5. Your next three sittings (concrete, in order)

**Sitting A - clear the table (30-45 min, mostly no code)**
1. Set up save-history and make your first save. (Check that `.env` is
   kept secret and `venv/` is ignored - good.)
2. Open `BUILD_LOG.md` and write a real entry: today's date, "Step 1/2",
   and the three bugs above written as YOUR OWN diagnosis. The honesty
   marks are the point. Right now `backends/server.py` is probably WIGGLY
   ("runs, but I cannot say why"), and everything else is SKIPPED.
3. Answer the Step 0 questions in `docs/architecture.md` (proxy vs reverse
   proxy, L4 vs L7, hop-by-hop vs end-to-end, what each rule is good at).
   No code this sitting. It is the cheapest 45 minutes in the project.

**Sitting B - make Step 1 honest (1-2 h)**
1. Add the fake-broken button `/crash?seconds=N` to `backends/server.py`
   (the health door goes quiet, the helper stays standing). It is your
   break-on-purpose button for every later demo. You cannot do Step 5
   without it.
2. Chase the `/work?ms=300 -> 0.52s` gap. Five timed runs. Write the
   numbers down.
3. Run all three helpers side by side and ask each one who it is.

**Sitting C - make Step 2 run (2 h)**
1. Fix the `proxy.py` / `strategies.py` mismatch (idea 1) - pick "verbs" or
   "things", then stick with it for all four rules.
2. Fix the settings order (idea 2) and prove it:
   `python -c "from src.config import load_config; print(load_config())"`
   must print 3 helper addresses.
3. Write `src/app.py` with ONE catch-all door wired to the carrying part.
   Then ask the door 5 times and watch 1-2-3-1-2.
4. That first turning answer is the moment the project stops being a
   document and starts being yours. Save it.

---

## 6. Little quiz (do this before you open the docs again)

Say the answers out loud. If any one takes more than a second of thinking,
that is your next reading homework.

- What is the difference between a (forward) proxy and a reverse proxy?
  Which one are you building, and how would a kid even notice?
- L4 vs L7 sharing - which are you, and so what do you see and never see
  about the ask?
- Why is asking for ice cream (POST) dangerous to repeat but asking the
  time (GET) is not? (One sentence. It is RFC 9110 section 9.2.1.)
- Which headers are "hop-by-hop" and must NOT be passed along? Name two.
- Why does "take 1 away from the waiting count" have to happen at the very
  end, always?
- If reading the whole body into memory is wrong for a door, what is right,
  and why?
- What does "smooth" weighted fix, compared to "3 for Sunny, then 1 for
  Buddy"?
- Why do we need SEVERAL misses in a row before we skip a helper, instead
  of just one?

---

## 7. Where all the pages are

| Page | What it is | Status |
| --- | --- | --- |
| `README_FIRST.md` | The big picture: mission, rules 1-9, "what finished means" | given - read once, all the way |
| `ROADMAP.md` | Steps 0-9 with READ FIRST / PROVE IT / OOPSIES | given - your map |
| `PROFESSOR.md` | How we work together: the ladder, the sitting loop | given - this is the promise |
| `HOW_TO_SEARCH_DOCS.md` | How to find answers in the real instructions | given - the meta-skill |
| `BUILD_LOG.md` | Your sitting diary + honesty marks | **only Sitting 00 - fill it in** |
| `docs/architecture.md` | Drawing + choices + run commands | template, all "fill me in" |
| `docs/algorithm_notes.md` | One note per rule + your numbers | template, all "fill me in" |
| `docs/chaos_log.md` | Every time you broke something, and what happened | template, empty |
| `tests/*.py` | Test ideas written as notes | templates, no checks yet |
| `scripts/load_test.py`, `static/dashboard.html` | the many-kids machine + the window | templates |

---

## 8. One rule to carry forward

When you hit the next wall: **make it break on purpose first**, then bring
the error, the smallest example, the page you read, and the experiment you
ran. PROFESSOR.md Part 3 is the ladder. The robot is rung 5 - for naming
the idea and pointing at the page, never for handing you `src/`.

Grading yourself with the honesty marks every sitting is what turns this
from "a project that runs" into "a project you own".
