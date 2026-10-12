# mini-load - Architecture

> Owner: you. This file is not decoration: DO1 says *every command to run every
> phase* is documented here, and M0 says the request-path diagram goes here
> before any code is written.

## 1. The request path (M0)

Draw the path of one request from socket accept to response returned, naming
every function it passes through. ASCII is fine.

```
CLIENT -> LB :8080 -> [ strategy pick | proxy forward | metrics ] -> backend :800x
```

TODO(M0): replace this sketch with your own diagram. You must be able to
redraw it from memory (DO10).

## 2. Component decisions and why

| Decision | Choice | Why (your words) |
| --- | --- | --- |
| FastAPI vs Starlette | | README requirements.txt asks for one sentence |
| httpx AsyncClient vs ASGITransport | | README requirements.txt asks for the M2 write-up |
| hop-by-hop header handling | | RFC 9110/9112 - which ones, and where they are stripped |
| body handling | | streaming, not buffered: say where the bytes live at each hop |
| keep-alive ownership | | which side closes the connection, and why it matters |
| percentile method | | bounded reservoir: which one, why, and what it costs |
| flap damping | | why N consecutive failures is enough (README Part 4) |

## 3. Failure behaviour

- Idempotent methods (GET/HEAD/PUT/DELETE): one retry on a different backend.
- POST: never auto-retried - the first attempt may already have committed
  something (C6). One sentence here, verbatim, is part of DO6.

## 4. Service discovery (Phase 7+)

Say this sentence, in these words, in this file:

> Backends are reached by Docker Compose service name, not by hardcoded
> localhost ports - that is service discovery.

## 5. How to run everything (DO1)

Every command for every phase goes here, from a clean checkout. Nothing may
be documented only in your shell history.

```bash
# TODO(M1) local: three backends
# TODO(M1) local: the LB
# TODO(M2) curl proof that all three backends serve
# TODO(M7) docker compose up -d
# TODO(M6) load test
```
