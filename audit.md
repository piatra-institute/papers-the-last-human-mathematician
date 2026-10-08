# Audit

Dated log of editorial passes and verification runs. Newest first.
See the workspace docs (run `papers docs`): writing-pipeline.md §7 and refresh-pipeline.md.

## 2026-10-08 — initial publication

Scope: first publication of the paper from the origin conversation and dossier (chats/, not committed).
Changes:
  - brief, research log and bibliography (60 references; DOIs resolved through doi.org and 2026 sources read on 2026-10-08)
  - simulation/: frozen corpus data (Google Books Ngram Viewer, OpenAlex; retrieved 2026-10-08), fetch script,
    analysis of "computer", "typewriter" and "mathematician"; 12 internal checks
  - PAPER.md with three figures, three tables and a protocol of three preregistered claims for 2036
Verification:
  - run: verification/model.json PASS (12/12 checks), data files declared as inputs
  - voice: OK (0 errors, 0 warns)
  - refs: 60 cited, 60 entries, PASS
  - claims: 132 bound (60 computation), PASS
  - build: 21 pages, no missing-character warnings

<!--
## YYYY-MM-DD — <pass name>
Scope: <the bounded list of changes>
Changes:
  - ...
Verification:
  - voice: <errors / warns>
  - refs: <missing / unused>
  - claims: <reconciliation result>
  - build: <pages, missing-char warnings>
  - check => PASS/FAIL
-->
