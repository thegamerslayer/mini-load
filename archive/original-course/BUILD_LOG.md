================================================================================
  BUILD_LOG.md - SESSION LOG
  One row per session. Fill it AS you work, not from memory afterwards.
  The FDI diagnosis (Frozen / Drifting / Ignored) is the point: it tells you
  what you actually own versus what you are carrying. See PROFESSOR.md Part 2.
================================================================================

HOW TO USE
  FROZE ..... I can explain it cold and rebuild it from scratch.
  DRIFTING .. It works, but I cannot yet explain WHY. Needs a rebuild date.
  IGNORED ... Works by luck, or skipped. Needs a milestone assigned to it.

Every DRIFTING gets a rebuild date. Every IGNORED gets a milestone.
Unowned items become bugs you discover during a demo.

--------------------------------------------------------------------------------
SESSION 00 - 2026-09-30 - M0 (setup session, project files created)
--------------------------------------------------------------------------------
DONE
  - Project scaffolded: README_FIRST.md, ROADMAP.md, PROFESSOR.md,
    HOW_TO_SEARCH_DOCS.md, requirements.txt, this log.
  - No code written yet, by design. M0 starts with reading, not typing.

FDI
  FROZE ..... The project shape: client -> LB :8080 -> backends :8001-3.
              The four algorithms by name and what each optimises for.
  DRIFTING  . (none yet - this row stays honest or the log is theatre)
  IGNORED ... Everything. That is what M0-M9 are for.

FIRST ACTION NEXT SESSION
  Start ROADMAP M0: read MDN HTTP overview + RFC 9110 sec 9.2.1, draw the
  request-path diagram in docs/architecture.md, answer the three M0
  questions in writing. No code until that is done.

SOURCES THIS SESSION
  - (paste doc URLs here as you read them - see HOW_TO_SEARCH_DOCS.md
     Part 5: this section becomes your private handbook)

--------------------------------------------------------------------------------
SESSION 01 - (template - copy this block for every new session)
--------------------------------------------------------------------------------
DATE / MILESTONE:
DONE (commits):
  -
FDI
  FROZE ..... :
  DRIFTING  . :           -> rebuild date:
  IGNORED ... :           -> fix in milestone:
FIRST ACTION NEXT SESSION:
SOURCES THIS SESSION:
  -

================================================================================
  RULE: never delete a row. A wrong turn with a written reason is a lesson;
  a deleted row is a lie you will tell yourself in an interview.
================================================================================
