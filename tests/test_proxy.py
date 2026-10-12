"""
Proxy tests against running backends (M4).

Needs real backend processes (or an ASGI transport you have justified) because
the behaviours under test are the wire-level ones:

  - method, path, query string, headers and body arrive intact at the backend
  - hop-by-hop headers are stripped, X-Forwarded-* / X-Request-ID are handled
  - the response reports which backend served it
  - a dead backend gets one retry on another backend for GET/HEAD/PUT/DELETE
  - a POST is NEVER retried (C6) and both halves of that rule have a test

TODO(M4): write these (DO6 in README_FIRST Part 6 depends on them).
"""
