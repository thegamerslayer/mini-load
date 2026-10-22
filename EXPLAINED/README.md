# 🎨 mini-load — every line, explained

> A guided tour of **all the code in this project, line by line.**
> Written so you can point at any line and say *why* it is there.

---

## 👀 How to read this (get the colors!)

These are normal text files, but they are written to look good when **rendered**:

- **In VS Code:** open a file, then press **`Ctrl + Shift + V`** → you get a live preview
  with colored headings, boxes and tables. (This is the "colorful" view.)
- **On GitHub / any Markdown viewer:** it just works.

👉 Start with this page, then read the numbered files **in order**.

---

## 🧠 The one big picture (memorize this)

```
        a kid (browser / curl / load tester)
                     │
                     ▼
        ┌─────────────────────────────┐
        │      THE DOOR  :8080        │   ← src/main.py + src/app.py
        │  1. catch the ask           │
        │  2. pick a helper           │   ← src/strategies.py
        │  3. carry the ask over      │   ← src/proxy.py
        │  4. carry the answer back   │
        └───────────┬─────────────────┘
                    │  (httpx)
      ┌─────────────┼─────────────┐
      ▼             ▼             ▼
  ┌───────┐    ┌───────┐    ┌───────┐
  │Sunny  │    │Buddy  │    │Rosie  │      ← backends/server.py
  │ :8001 │    │ :8002 │    │ :8003 │        (ONE file, run 3 times)
  └───────┘    └───────┘    └───────┘
```

**The golden rule of this design:** the helpers are *dumb* (they only answer
`/`, `/health`, `/work`). **All the smart stuff lives in the Door.**

---

## 🗺️ The map — what each file does, and is it done?

| # | File | Lines | Status | What it is |
|---|------|------:|--------|------------|
| — | `run.py` | 5 | 🟢 works | starts **one** backend |
| 02 | `backends/server.py` | 59 | 🟢 mostly | the dumb helper (3 endpoints) |
| 03 | `src/config.py` | 19 | 🟢 works | reads settings from `.env` |
| 04 | `src/pool.py` | 22 | 🟢 works | `Backend` + `Pool` (the group) |
| 05 | `src/strategies.py` | 85 | 🟡 mostly | the **four choosers** |
| 06 | `src/proxy.py` | 22 | 🔴 **has a bug** | carries the ask (missing `await`) |
| 07 | `src/app.py` | 21 | 🟢 parses | the door itself (catch-all) |
| 08 | `src/main.py` | 23 | 🟢 works | the door's start button |
| 09 | `tests/test_strategies.py` | 98 | 🟢 5 tests run | tests for the choosers |
| 10 | `src/health.py` | 3 | ⬜ empty | knock-knock loop *(TODO M5)* |
| 10 | `src/metrics.py` | 3 | ⬜ empty | the tally board *(TODO M6)* |
| 10 | `src/dashboard.py` | 3 | ⬜ empty | `/stats` page *(TODO M6)* |
| 10 | `tests/test_proxy.py` | 14 | ⬜ doc only | proxy tests *(TODO M4)* |
| 10 | `tests/test_health.py` | 14 | ⬜ doc only | health tests *(TODO M5)* |
| 10 | `scripts/load_test.py` | 13 | ⬜ doc only | Locust rig *(TODO M6)* |
| 10 | `static/dashboard.html` | 15 | ⬜ skeleton | the big window *(TODO M6)* |

**Legend:** 🟢 real code that works · 🟡 works but imperfect · 🔴 has a real bug · ⬜ not written yet

---

## 📚 The files in this folder

| File | Explains |
|------|----------|
| `01-run.md` | `run.py` — how a single backend starts |
| `02-backend-server.md` | `backends/server.py` — the dumb helper |
| `03-config.md` | `src/config.py` — where settings come from |
| `04-pool.md` | `src/pool.py` — `Backend` and `Pool` |
| `05-strategies.md` | `src/strategies.py` — all four choosers |
| `06-proxy.md` | `src/proxy.py` — carrying the ask (＋ the bug) |
| `07-app.md` | `src/app.py` — the catch-all door |
| `08-main.md` | `src/main.py` — the start button |
| `09-tests.md` | `tests/test_strategies.py` — your 5 tests |
| `10-not-written-yet.md` | every file that is still empty/TODO |
| `11-bugs-and-notes.md` | 🐛 the bug list, ⚠️ warnings, 💡 wins |

---

## 🧭 What "done" looks like for the request path

When you ask the door for something, this is the chain of your own functions it walks:

```
app.catch_all()        ← src/app.py      "a kid knocked, what did they bring?"
  └─ proxy.forward()   ← src/proxy.py    "carry it to a helper"
       └─ balancer.choose()  ← src/strategies.py   "which helper?"
            └─ httpx  →  backend  →  answer comes back the same way
```

If you can narrate that chain from memory, you understand the project. 🎯
