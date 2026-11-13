# Investment Memory Engine

A DBMS Level 3 research journal connecting investment decisions, news context, model reasoning, and observed outcomes. The core project remains Investment Memory Engine. The required application now uses **Next.js + FastAPI + PostgreSQL + Chroma**, replacing SQLite/Streamlit as the submission stack.

All seeded news, reasoning and returns are synthetic. No live trading, market feed or generated financial advice is implemented.

## Start on this computer

Official PostgreSQL binaries, the initialized database, and the eight-memory search index are already available locally. Start the required application with:

```powershell
./start_project.ps1
```

On first launch, open http://localhost:3000 to create your administrator account in the browser. Enter your name, email, a 12?128 character password, and confirmation. After creation, sign in on the same page. The one-time setup closes as soon as any account exists; existing accounts are preserved. Database credentials remain in ignored `.env`; application passwords are stored as hashes.

For manual account creation or index repair:

```powershell
.venv/Scripts/python.exe scripts/local_postgres.py
.venv/Scripts/python.exe -m backend.manage create-user --email YOUR_EMAIL --name "Aswin" --role admin
.venv/Scripts/python.exe -m backend.manage rebuild-index
```

Open **http://localhost:3000** and sign in. Use exactly this host: the default CSRF origin is `http://localhost:3000`. Stop the app with Ctrl+C. PostgreSQL remains running and can be stopped with `.deps/pgsql/bin/pg_ctl.exe -D data/postgres stop`.

An administrator can create the second member's analyst account in Administration. Passwords are stored only as salted scrypt hashes. There is no shared default application password.

## Fresh machine setup

Requires Python 3.11-3.13, Node.js 20.9+ and PostgreSQL 16+. Use PostgreSQL directly, or Docker Compose:

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
# Edit .env with your own database URL and password before continuing.
docker compose up -d
.venv/Scripts/python.exe -m backend.manage init
.venv/Scripts/python.exe -m backend.manage create-user --email YOUR_EMAIL --name "Your Name" --role admin
.venv/Scripts/python.exe -m backend.manage rebuild-index
cd web
npm.cmd ci
npm.cmd run build
cd ..
./start_project.ps1
```

If PostgreSQL is already installed, create an empty database named `investment_memory`, set `DATABASE_URL`, and omit Docker. The SQL setup account needs CREATE TABLE/VIEW/FUNCTION privileges. For the portable Windows alternative, obtain the official [EDB binaries](https://www.enterprisedb.com/download-postgresql-binaries), extract `pgsql` into `.deps`, and run `scripts/local_postgres.py` before creating `.env`. That helper refuses to overwrite existing configuration and binds only to loopback port 55432.

The embedding model downloads once from Hugging Face; the existing `data/model_cache` is reused offline. Chroma stores its derived index in `data/chroma_v2`. The model is `sentence-transformers/all-MiniLM-L6-v2`, with 384-dimensional normalized embeddings and cosine distance. Index repair never changes SQL records.

For development, run these in separate terminals:

```powershell
.venv/Scripts/python.exe -m uvicorn backend.api:app --host 127.0.0.1 --port 8000
# Other terminal:
cd web
npm.cmd run dev
```

Next.js proxies `/api/*` to the local API. Optional `API_URL` is server-side configuration in the Next.js process; no database credentials reach the browser. Run one API worker for local Chroma and in-process login throttling. Public deployment requires HTTPS, `COOKIE_SECURE=true`, an exact `APP_ORIGIN`, a restricted database runtime account, and a shared rate limiter if multiple workers are introduced.

## Application workflows

- **Overview:** filter by sector/decision, inspect reasoning, update known or unknown outcomes; admin can delete with a confirmation.
- **Add memory:** atomically insert a new company if needed, news, investment and reasoning. SQL remains usable when vectors are unavailable.
- **Search memories:** retrieve the five most similar current memories, respecting sector/decision filters. Similarity is not a probability or predicted return.
- **SQL reports:** six live reports expose JOIN, GROUP BY, HAVING, ORDER BY, aggregates and a subquery.
- **Administration:** create admin/analyst accounts, repair Chroma, inspect the last 100 audit records.

Analysts may create memories and update their own outcomes. Admins may update any outcome, delete memories, inspect audits, manage accounts and rebuild the index. Seed records have no creator and require admin rights to edit. Text is intentionally preserved as historical evidence; outcome updates use a revision number to reject stale edits.

## Verify

```powershell
.venv/Scripts/python.exe scripts/run_tests.py --vectors
cd web
npm.cmd run build
```

Tests create a uniquely named PostgreSQL schema, use a temporary Chroma directory, and drop only that test schema afterward. The configured database user therefore needs CREATE SCHEMA. `--vectors` exercises the real cached model, not substitute vectors. See [test evidence](docs/TEST_RESULTS.md).

## Submission materials

- [How to showcase every requirement and close remaining gaps](docs/REQUIREMENT_SHOWCASE.md)

- [Requirement-by-requirement checklist](docs/REQUIREMENTS_COMPLIANCE.md)
- [Updated project report source](docs/PROJECT_REPORT.md)
- [Database design and data dictionary](docs/DATABASE_DESIGN.md)
- [Team and contribution record](docs/TEAM.md)
- [Demonstration and screenshot checklist](docs/DEMO_GUIDE.md)
- [Viva preparation](VIVA_PREPARATION.md)
- `sql/03_schema.sql`: PostgreSQL DDL, ALTER migration, indexes, views, audit function/trigger
- `sql/04_demo_data.sql`: the original eight fictional investment memories, adapted to PostgreSQL
- `sql/05_reports.sql` and `sql/06_advanced_demo.sql`: queries and non-destructive CREATE/ALTER/DROP laboratory
- `backend/`: API, password/session security, PostgreSQL transactions and Chroma integration
- `web/`: Next.js App Router application and reproducible npm lockfile

## Submission items requiring the team

Team: S Anuj Srijan (PES1UG24AM234) and Aswin Adhitya (PES1UG24AM213). Confirm instructor approval, title uniqueness within your section and responsibilities. The public repository contains the project and completed template report. Current Next.js screenshots and hands-on demo verification remain team review items. These are explicitly pending, not claimed as passed.

The final template report is edited in [Google Docs](https://docs.google.com/document/d/1nnMdmcUHtnRm94ydNhn5bSt5wBVgeu-sCCit_blN_0M/edit) and exported as [PDF](PROJECT_REPORT.pdf) and [Word](PROJECT_REPORT.docx). The original template is retained. The older report generator produces a different layout; to use it, install optional report tools with `.venv/Scripts/python.exe -m pip install -r requirements-report.txt`, then run `.venv/Scripts/python.exe docs/build_level3_report.py`.

## Earlier prototype

`app.py`, `database.py`, `vector_store.py`, `init_db.py` and `setup_and_run.ps1` are retained only for the old SQLite/Streamlit prototype. Its schema and README are in `legacy/`; existing `data/investments.db` and `data/chroma` were preserved. Do not use the old app, old screenshots, `info.md` or old PDF as evidence for the Next.js/PostgreSQL requirements. The updated documentation above is authoritative. The new PostgreSQL database contains the original supplied seed data; custom SQLite rows are preserved in SQLite and are not automatically imported.

## Design references

Implementation follows the official [Next.js installation guide](https://nextjs.org/docs/app/getting-started/installation), [Psycopg transaction documentation](https://www.psycopg.org/psycopg3/docs/basic/transactions.html), and [FastAPI cookie handling](https://fastapi.tiangolo.com/advanced/response-cookies/). These libraries support the original investment-memory domain model; this is not a copied tutorial application.
