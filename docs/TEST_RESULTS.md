# Test results

Run date: 1 November 2026. Stack: PostgreSQL 16.15; Next.js 16.4.3 production build; Python 3.13; Psycopg 3.3.6; FastAPI 0.162.0; real Chroma and sentence-transformers/all-MiniLM-L6-v2.

## Executed evidence

| Check | Result |
|---|---|
| Seed initialization repeatability, expected averages, six reports, safe DDL laboratory | PASS |
| Unauthenticated access, analyst restrictions, origin validation, logout, login throttling | PASS |
| Atomic rollback after invalid FK; invalid API fields; direct database CHECK/FK rejection including NaN | PASS |
| Create/update/delete, ownership, revision conflict HTTP 409, INSERT/UPDATE/DELETE audit events | PASS |
| Sector/decision filters, injection-shaped input treated as data, duplicate accounts, expired sessions | PASS |
| Real MiniLM embeddings and Chroma retrieval, pending count, deletion exclusion, stale-text exclusion, rebuild cleanup | PASS |
| Randomly salted scrypt hashes, valid/invalid password verification, weak-password rejection | PASS |
| Next.js production build (App Router / and /_not-found) | PASS |
| Production HTTP through Next.js: HTML, login cookie, me, eight memories, six reports, logout, unauthorized after logout | PASS |
| Visual browser inspection and screenshots | NOT COMPLETED: browser host unavailable; native computer-use approval timed out |

The backend unittest run reported 7 tests, OK, with no skips when TEST_VECTORS=1. The initial vector run used the existing model cache after blocked network retries; the loader was then improved to try local_files_only first. Tests use a generated disposable PostgreSQL schema and temporary Chroma directory, not mocks for database or vector behavior. The old SQLite/Streamlit test evidence is retained in legacy/TEST_RESULTS.md and does not establish compliance for this version.

## Reproduce

```powershell
.venv/Scripts/python.exe scripts/run_tests.py --vectors
cd web
npm.cmd run build
```

Without --vectors, the real vector test is explicitly skipped. Missing TEST_DATABASE_URL in a direct unittest invocation also skips PostgreSQL integration, so a green skipped run must not be reported as full coverage. The scripts/run_tests.py wrapper uses DATABASE_URL from .env and requires a working server. Model files must be cached or available for download.

## Coverage limits

No claim of browser visual/accessibility acceptance, large-dataset performance, multiworker Chroma consistency, production penetration testing or financial model accuracy is made. First-time setup on every operating system has not been tested. The local lab uses a database owner account; hosted deployment needs a restricted runtime role and HTTPS. Students must perform the documented UI walkthrough and capture real screenshots before final submission.

## Browser account setup update ? 2 November 2026

First administrator creation now uses the Next.js setup form rather than terminal prompts. Three new PostgreSQL tests passed: successful setup/login and subsequent closure, invalid input/origin rejection, and simultaneous setup requests producing exactly one admin (201/409). The setup endpoint is available only while the users table is empty; the role is fixed by the server.

Regression result: 10 tests run, 9 passed, 1 vector test deliberately skipped. Real vector behavior passed in the earlier full run and was unchanged by this update. The optional CLI password-length error was also checked to return a clean validation message without a traceback. Browser visual testing remains pending.
