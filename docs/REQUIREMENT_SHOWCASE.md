# Investment Memory Engine requirement showcase

Reviewed on 2 November 2026 against `DBMS Level 3 Project Requirements draft.docx` and the current implementation. Git/GitHub and commit history are excluded at your request. README instructions and actual individual contributions remain relevant independently of Git.

## Is everything else complete?

**The technical implementation is present, but the project is not yet fully verified and submission-complete.**

| Area | Current evidence | What remains |
|---|---|---|
| PostgreSQL, Chroma, schema, SQL, advanced features, API, authentication and roles | Implemented; automated tests passed | Demonstrate the behavior below |
| Next.js interface | Production build and HTTP integration passed | Complete a manual browser walkthrough; visual acceptance is unverified |
| Documentation | Report, design, queries, tests and viva notes exist | Add genuine Next.js screenshots and regenerate the report |
| Required screenshots | Missing; existing screenshots show the old Streamlit app | Capture the seven screens listed below |
| Approved team and unique title within the section | Names recorded | Confirm instructor approval and title uniqueness |
| Both members contribute to database and application development | Proposed responsibilities recorded | Confirm and explain actual work by each member |
| Originality | Domain-specific implementation exists | Understand the code, explain design decisions and acknowledge assistance according to course policy |

The full seven-test suite previously passed with real PostgreSQL, MiniLM and Chroma. The 2 November regression run passed six tests and explicitly skipped the vector test. These results do not prove browser usability, instructor approval or individual authorship.

The course document still includes Git; excluding it here reflects your requested scope, not an instructor-issued waiver.

## 1. Prepare the demonstration

Run from the project root in PowerShell:

```powershell
.\start_project.ps1
```

The launcher starts local PostgreSQL, initializes the schema and prompts for an administrator email, display name and hidden password if no admin exists. Choose your own password of 12–128 characters. It then starts FastAPI and Next.js. Keep the terminal running.

Open **http://localhost:3000**. Use `localhost`, because that is the configured request origin. Do not demonstrate `streamlit run app.py`: `app.py` is the archived prototype.

Sign in as admin. In Administration, create an **analyst** account before presenting. Use an incognito window for the analyst if you want separate sessions. Do not project passwords.

Prepare semantic search before the presentation; cold model loading can take several minutes:

```powershell
.venv/Scripts/python.exe -m backend.manage rebuild-index
```

Wait for completion. The eight supplied memories were indexed previously; newly added memories need another rebuild. Do not reset the database for the demo.

Open these files beforehand:

- `diagrams/04_current_ER.svg`
- `sql/03_schema.sql`, `sql/04_demo_data.sql`, `sql/05_reports.sql`, `sql/06_advanced_demo.sql`
- `docs/DATABASE_DESIGN.md`, `docs/PROJECT_REPORT.md`, `docs/TEAM.md`

Show `.env.example` when discussing configuration. Keep the real `.env`, database passwords, session cookies and password hashes off screen.

## 2. Title, problem, objectives, scope and originality

| Requirement | What to show/do | What to explain |
|---|---|---|
| Unique project title | Show the report title; confirm uniqueness with the instructor | Code cannot prove uniqueness within your section |
| Meaningful real-world problem | Open a memory showing its news, reasoning and return | Ordinary trade records often lose the reason behind a decision |
| Objectives | Report > Objectives | Preserve context, retrieve similar situations, compare outcomes and maintain integrity |
| Scope and functional requirements | Report sections and application navigation | A research journal with manually entered reasoning and synthetic seed data; no live trading or generated financial advice |
| More than basic CRUD | Perform a paraphrased semantic search, inspect an audit event and show a report | Semantic reuse, relational analysis, audited outcomes and search consistency extend record maintenance |
| Originality | Explain your entity choices and implementation decisions | Review the generated work and acknowledge assistance under course policy; do not invent independent authorship |

Suggested opening:

> Investment Memory Engine preserves the news and reasoning behind a decision, alongside its amount and eventual outcome. PostgreSQL protects and reports the structured data. Chroma retrieves related past reasoning even when a new question uses different words.

## 3. Approved two-member team and responsibilities

Show `docs/TEAM.md` with **Aswin / PES1UG24AM234** and **Aswin / PES1UG24AM213**. Both names were supplied as Aswin. Confirm team approval with the instructor.

The recorded assignments are proposed, not verified contributions. Each member should explain actual work on both database and application development. No commit history is requested here.

| Member | Suggested database demonstration | Suggested application demonstration |
|---|---|---|
| Aswin / PES1UG24AM234 | Constraints, transaction rollback and audit trigger | API validation, sessions and permission enforcement |
| Aswin / PES1UG24AM213 | Embeddings, metadata, cosine retrieval and index repair | Next.js forms, filters, search and visual testing |

Adjust this split to reflect actual work. Knowing a feature is not proof of having developed it.

## 4. SQL plus a second database paradigm

**Open:** `backend/db.py`, `backend/vectors.py`, the ER diagram, a live report and semantic search.

**Explain:** PostgreSQL is authoritative for structured records, references, outcomes, users and audits. Its constraints and transactions enforce consistency. Chroma stores a derived semantic index over unstructured news and reasoning. This is the allowed **SQL + Vector Database** option; MongoDB or Neo4j is not also required.

Show the actual server and row counts with this PowerShell command:

```powershell
@'
from backend import db
print(db.rows('SELECT version() AS server'))
for table in ('companies', 'models', 'news', 'investments', 'investment_reasoning'):
    print(table, db.rows('SELECT COUNT(*) AS count FROM ' + table))
'@ | .venv/Scripts/python.exe -
```

The table names are fixed demonstration constants. An unchanged seed database has 5 companies, 2 models, 6 news rows, 8 investments and 8 reasoning rows. Counts change when you add records.

## 5. ER diagram, relational schema and integrity constraints

Open `diagrams/04_current_ER.svg`, then map its boxes and links to `sql/03_schema.sql`. Use `docs/DATABASE_DESIGN.md` for the full data dictionary and normalization explanation.

| Requirement | Point to | Explanation |
|---|---|---|
| Entities and attributes | companies, models, news, investments, investment_reasoning, users, sessions, audit_log | Each relation represents a distinct domain or security/history concern |
| Primary keys | company_id, investment_id, reasoning_id and other PRIMARY KEY columns | Uniquely identify records; most use generated BIGINT identities |
| Foreign keys | investments.company_id/model_id and reasoning.investment_id/news_id | Referenced records must exist |
| Relationships | Company/Model to Investments; Investment/News to Reasoning | One company/model has many decisions; a news item may support multiple reasoning links |
| UNIQUE | ticker, email, vector_memory_id | Prevent duplicate identifiers |
| CHECK and NOT NULL | Amount, decision, confidence, return and nonblank text | Database independently rejects invalid data |
| Data types | DATE, NUMERIC, TIMESTAMPTZ, JSONB | Deliberate types for dates, financial values, timestamps and audit snapshots |
| Normalization | Separate company/model/news relations and joined view | Core facts are not duplicated in every trade; explain the documented 3NF assumptions |

Explain that an unknown return is **NULL**, not zero. Audit record IDs deliberately have no investment FK so history survives deletion. The Chroma link is checked by application code, not by a cross-database SQL foreign key.

## 6. CREATE, ALTER and DROP

First show real `CREATE TABLE`, `CREATE INDEX`, `CREATE VIEW`, `CREATE FUNCTION` and `CREATE TRIGGER` statements in `sql/03_schema.sql`. Show `ALTER TABLE` adding creator ownership and revision tracking. Initialization executes this schema.

Then open `sql/06_advanced_demo.sql`. Its first transaction creates a **temporary** table, adds a column, inserts/updates/selects/deletes a row, drops the temporary table and rolls back. It does not drop application tables.

Execute the laboratory and display all result sets:

```powershell
@'
from backend import db
with db.connect() as conn:
    cursor = conn.execute((db.ROOT / 'sql/06_advanced_demo.sql').read_text())
    while True:
        print(cursor.statusmessage)
        if cursor.description:
            for row in cursor.fetchall():
                print(row)
        if not cursor.nextset():
            break
'@ | .venv/Scripts/python.exe -
```

Expected: DDL/DML status messages, the updated temporary row, report results and an EXPLAIN plan. Explain why DROP is demonstrated on disposable data rather than destroying the project schema.

## 7. INSERT, SELECT, UPDATE and DELETE through the application

### Insert and select

As admin, open **Add memory** and enter:

| Field | Fictional demonstration value |
|---|---|
| Company | Existing NVIDIA company |
| Reasoning model | Demo Reasoning Model / v1 |
| Amount | 2500 |
| Decision | BUY |
| Investment date / news date | 2026-11-02 / 2026-11-01 |
| Confidence | 0.80 |
| Return percentage | Leave blank |
| Headline | SHOWCASE ONLY - AI accelerator demand |
| News content | Fictional cloud providers are expanding AI data-center capacity. |
| Reasoning | Increased AI infrastructure spending could support GPU demand, subject to competition. |

Save and open Overview. Expected: the memory appears with an unknown return. Explain the related news/investment/reasoning INSERTs and the joined SELECT used to display them. Do not resubmit a successful save because its vector is still pending.

### Update

On the SHOWCASE ONLY memory, choose **Edit outcome**, enter **4.5** and save. Expected: its return changes. Explain `UPDATE investments`, revision increments and why the original reasoning is preserved.

### Audit and delete

Open Administration > **Load latest 100 events**. Find the memory's INSERT/UPDATE entries and compare operation, actor, timestamp and old/new values.

Delete only this disposable memory and confirm. Expected: it disappears and a DELETE audit remains. Shared news is retained if another reasoning row still references it. Original seed records should remain intact. This proves meaningful DELETE behavior, not just a deletion statement in a script.

## 8. JOIN, GROUP BY, HAVING, ORDER BY, aggregates and subqueries

Open **SQL reports** and expand **Inspect SQL query** for each report.

| Report | Concepts to explain | Expected on unchanged seed data |
|---|---|---|
| Average return by company | JOIN, AVG, GROUP BY, ORDER BY | NVIDIA 6.00%; AMD 1.50% |
| Investments by sector | JOIN, COUNT, GROUP BY, ORDER BY | Technology 5; Finance 2; Energy 1 |
| Top five outcomes | JOIN, ORDER BY DESC, LIMIT | 8.0, 5.0, 4.0, 3.0, 2.5 |
| Return by model | JOIN, COUNT, AVG, GROUP BY | Results grouped by the two model labels |
| Sectors with multiple memories | GROUP BY, HAVING COUNT(*) >= 2 | Technology and Finance qualify |
| Above-average outcomes | Scalar AVG subquery, WHERE, ORDER BY | Returns above the seeded overall average of 2.5% |

These values change with your data. Explain the query rather than forcing the result to match an old screenshot. Unknown outcomes are excluded from averages and rankings.

## 9. At least four advanced concepts

| Concept | Exact demonstration | What proves it |
|---|---|---|
| Transactions | Show create_memory in backend/api.py and test_03_transaction_constraints | A missing model FK rolls back all related company/news/investment inserts |
| Views | Show memory_details and company_performance; run the command below | Joined/aggregated results come from normalized base relations |
| Indexing | Show CREATE INDEX and EXPLAIN output from the laboratory | Index definitions exist; explain the chosen query plan |
| Vector similarity search | Search a paraphrased AI spending idea after rebuilding | Real MiniLM embeddings and Chroma retrieve related text |
| Stored function | Show audit_investment_change() | PL/pgSQL function builds the audit entry within PostgreSQL |
| Trigger | Update the disposable outcome and inspect audit_log | AFTER INSERT/UPDATE/DELETE automatically records the change |

Transactions, views, indexing and vector search already provide four distinct concepts. The stored function and trigger add evidence. Full-text search, NoSQL aggregation and a separate stored procedure are examples in the rubric, not individually mandatory features.

```powershell
@'
from backend import db
print('View results:', db.rows('SELECT * FROM company_performance ORDER BY company_name'))
print('Views:', db.rows("SELECT table_name FROM information_schema.views WHERE table_schema=current_schema()"))
print('Indexes:', db.rows("SELECT tablename,indexname,indexdef FROM pg_indexes WHERE schemaname=current_schema() ORDER BY tablename,indexname"))
'@ | .venv/Scripts/python.exe -
```

PostgreSQL may choose a sequential scan for eight investments. That is a legitimate optimizer choice for a small table, not evidence that indexing is missing. Do not claim a performance improvement you have not measured.

## 10. Vector data model, embeddings and retrieval

Open `backend/vectors.py` and the vector section of `docs/DATABASE_DESIGN.md`.

| Requirement | Point to / demonstrate | Explanation |
|---|---|---|
| Embedded data | document(row) | Headline + news_text + reasoning_text |
| Embedding model | MODEL_NAME and encode() | sentence-transformers/all-MiniLM-L6-v2; normalized 384-dimensional vectors |
| Collection/documents | collection() and rebuild() | Persistent investment_memories_v2 collection; one document/vector per reasoning row |
| Metadata | Upsert mapping | reasoning_id, document fingerprint and model name |
| Index and metric | HNSW cosine configuration | Cosine similarity = 1 - cosine distance |
| Retrieval | search() | Embed query, rank neighbors, validate current SQL IDs/fingerprints, apply filters, return at most five valid matches |
| Repair/consistency | Add memory, observe pending status, rebuild | SQL is authoritative; indexing is an explicit derived-data operation |

Search for **Companies benefiting from increased AI infrastructure spending**. Expected: relevant AI memories such as NVIDIA or AMD with their news, reasoning and similarity. Try the paraphrase **Businesses likely to gain from expanding data-center demand** and use sector/decision filters.

Explain actual results; do not invent a fixed ordering or score. Similarity is not a probability, recommendation or predicted return. The reasoning-model labels in PostgreSQL are separate from the MiniLM embedding model. Long source text may be truncated; chunking is future work.

To demonstrate stale-vector handling, index the disposable memory before deleting it. Delete it, search and show that it is excluded even before the orphan vector is removed. Rebuild to remove the orphan. The vector test also verifies stale text-fingerprint exclusion and repeatable repair.

## 11. Next.js interface, API integration and environment variables

| Requirement | What to do/show | Expected evidence |
|---|---|---|
| Next.js interface | web/package.json, web/app/page.js, browser at localhost:3000 | The required application uses Next.js, not Streamlit |
| Forms/tables/dashboard/filtering | Overview, Add memory, Finance/BUY filter | Relevant components display and modify actual database records |
| Backend/API layer | Browser developer tools > Network; refresh or save a memory | Same-origin /api requests and successful responses |
| Database integration | web/next.config.mjs, backend/api.py, backend/db.py | Browser -> Next.js proxy -> FastAPI -> PostgreSQL |
| Vector integration | Perform search and inspect /api/search | API uses the encoder/Chroma and validates hits against SQL |
| Environment configuration | .env.example and load_dotenv/os.environ usage | Real configuration is server-side, not hardcoded in browser code |
| Architecture | Report > Architecture | Explain each layer and which store owns the authoritative data |

Manually finish add, view, edit, delete, filter, report, search, login and logout before marking UI verification complete. A production build alone does not establish this. Do not expose session-cookie values in developer tools screenshots.

## 12. Authentication, roles, validation, integrity and security

### Authentication and authorization

1. Open the app in an incognito window: expect a sign-in page.
2. Try an incorrect password once: expect generic invalid-credentials feedback.
3. Sign in as admin: expect Administration and administrator controls.
4. Sign in as analyst in a separate session: expect no Administration or delete controls.
5. As analyst, create a disposable memory and edit its outcome: expect success.
6. Inspect a seed memory or another user's memory: the analyst cannot edit its outcome. Automated tests additionally prove direct unauthorized API updates return HTTP 403.
7. Sign out and refresh: protected information requires sign-in again; the stored session is invalidated.

Show `current_user`, `admin` and ownership checks in `backend/api.py`. Button hiding alone is not security. Seed records have no creator, so only an admin may edit their outcomes.

### Database-level validation

Try an empty required headline and invalid amount/confidence in the form. Browser controls may stop submission first; this does not by itself prove database enforcement. Show the schema constraints, then run this direct database test:

```powershell
@'
import psycopg
from backend import db
try:
    with db.connect() as conn:
        conn.execute('UPDATE investments SET investment_amount=-1 WHERE investment_id=1')
        raise RuntimeError('Constraint did not reject the value; rolling back this test.')
except psycopg.errors.CheckViolation:
    print('PASS: PostgreSQL rejected the negative amount; the transaction rolled back.')
print(db.rows('SELECT investment_id,investment_amount FROM investments WHERE investment_id=1'))
'@ | .venv/Scripts/python.exe -
```

Expected: rejection and an unchanged positive amount. The fallback RuntimeError also rolls back if the constraint unexpectedly fails to reject the value. The automated tests additionally cover invalid FKs, blank strings, NaN and ranges, plus full rollback of a failed multi-table save.

### Password and session security

Show `backend/security.py`: random salts, scrypt password hashing, constant-time comparison and SHA256 session-token hashes. Show cookie settings, session expiry, origin checks and parameterized queries in the API. Demonstrate storage without exposing hashes:

```powershell
@'
from backend import db
print(db.rows("SELECT display_name,role,password_hash LIKE 'scrypt$%' AS uses_password_hash FROM users ORDER BY user_id"))
print(db.rows('SELECT COUNT(*) AS stored_sessions,BOOL_AND(length(token_hash)=64) AS hashed_token_shape FROM sessions'))
'@ | .venv/Scripts/python.exe -
```

Sign in first if you want an active session row. With no sessions, BOOL_AND is NULL. Shape checks support the code explanation; they are not cryptographic proofs alone.

Explain HttpOnly, SameSite=Strict, eight-hour expiry, origin validation and login throttling. Local HTTP uses COOKIE_SECURE=false; HTTPS deployment requires true. Application passwords are hashed in SQL. Database credentials reside in local environment configuration; do not claim `.env` is encrypted or that this lab is a fully hardened production deployment.

### Consistency and conflicting edits

Show the row lock and revision comparison in update_outcome. The automated test sends an old revision after an update and expects HTTP 409. Explain that this prevents a stale client from silently overwriting an outcome. Audit and investment changes share one SQL transaction. PostgreSQL and Chroma do not share a distributed ACID transaction.

## 13. Required documentation and screenshots

| Requirement | File or evidence |
|---|---|
| Problem, objectives, scope, functional requirements | docs/PROJECT_REPORT.md |
| ER diagram | diagrams/04_current_ER.svg; also included in PROJECT_REPORT.pdf |
| Relational schema and data dictionary | sql/03_schema.sql and docs/DATABASE_DESIGN.md |
| Database choice/justification | docs/DATABASE_DESIGN.md > Problem-driven database choices |
| SQL/vector implementation | sql/ files and backend/ modules |
| Important queries | SQL reports page, sql/05_reports.sql, sql/06_advanced_demo.sql |
| System architecture | docs/PROJECT_REPORT.md > Architecture |
| Testing results | docs/TEST_RESULTS.md and actual terminal output |
| Conclusion and future enhancements | docs/PROJECT_REPORT.md and PROJECT_REPORT.pdf |
| Setup and execution instructions | README.md and start_project.ps1 |
| Application screenshots | Genuine Next.js captures below; still missing |

Save these under `docs/screenshots/`:

| Filename | Required capture |
|---|---|
| nextjs_01_login.png | Sign-in screen with empty password field |
| nextjs_02_overview.png | Dashboard, table and filters |
| nextjs_03_add.png | Add memory form with fictional input |
| nextjs_04_search.png | Actual search results and similarity |
| nextjs_05_reports.png | Report table and expanded SQL |
| nextjs_06_admin.png | Index status and a real audit event |
| nextjs_07_analyst.png | Analyst navigation and permitted controls |

The existing 01_add.png, 02_reports.png and 03_search_setup.png are Streamlit captures. They do not provide Next.js evidence. Browser/computer access was unavailable, so the new screenshots and visual walkthrough have not been completed by the assistant.

After a successful walkthrough, update the pending UI/screenshot statements in the source Markdown to reflect actual evidence. Then regenerate the report:

```powershell
.venv/Scripts/python.exe -m pip install -r requirements-report.txt
.venv/Scripts/python.exe docs/build_level3_report.py
```

The builder includes `nextjs_*.png` automatically. It does not automatically change pending-status prose. Open the resulting PDF and verify readable screenshots and unclipped text.

## 14. Show testing results

With PostgreSQL running, use a second terminal:

```powershell
.venv/Scripts/python.exe scripts/run_tests.py --vectors
```

Expected full coverage: **10 tests, OK, no skipped tests** (including three first-account setup tests). Tests use a unique disposable SQL schema and temporary Chroma directory, preserving presentation data. The configured user must have permission to create schemas.

| Test | Evidence to explain |
|---|---|
| test_01_seed_reports_and_ddl | Initialization, report values and actual DDL execution |
| test_02_authentication_authorization_and_csrf | Session protection, roles, origin checks, logout, throttling |
| test_03_transaction_constraints | Multi-table rollback, API validation, direct database rejection |
| test_04_crud_audit_and_concurrent_update | CRUD, ownership, audits, stale revision rejection |
| test_05_filters_users_and_sessions | Filters, injection-shaped input, duplicate users, expired sessions |
| test_06_real_vector_search_and_staleness | Real embeddings, relevant matches, pending/stale detection and repair |
| test_salted_hashes | Salt uniqueness, correct/incorrect passwords, weak-password rejection |

Without `--vectors`, one test is deliberately skipped. Do not present that as full vector verification. Prepare full test output before presenting because cold model loading may take time.

Show the production build before starting the presentation server:

```powershell
cd web
npm.cmd run build
cd ..
```

Expected: successful compilation and route output. Stop/restart the app around a rebuild; do not replace production build files while relying on the running presentation server.

## 15. Suggested twelve-minute presentation

| Time | Demonstration |
|---|---|
| 0:00–1:00 | Title, team, problem, objectives and scope |
| 1:00–3:00 | ER, schema, keys, normalization and database choices |
| 3:00–5:00 | Admin login, Overview, add and update disposable memory |
| 5:00–6:30 | Audit trigger, advanced concepts and safe DDL lab |
| 6:30–8:00 | Reports, HAVING and subquery |
| 8:00–9:30 | Semantic search, model, metric and repair |
| 9:30–11:00 | Analyst restrictions, validation, security and rollback tests |
| 11:00–12:00 | Test results, screenshots, actual contributions and future work |

Delete only disposable demonstration records. Keep schema, report and previous real test output ready if model loading would interrupt the presentation; explain any unavailable live feature honestly.

## 16. Final readiness checklist excluding Git

- [ ] Instructor confirms team approval and a section-unique title.
- [ ] Both members confirm actual database/application contributions and can explain them.
- [ ] Admin and analyst accounts exist and both can sign in.
- [ ] Manual Next.js walkthrough passes: add, read, update, delete, filter, reports, search and logout.
- [ ] Seven genuine Next.js screenshots are captured and included in the report.
- [ ] Full ten-test run passes with `--vectors` and no skips.
- [ ] Production build and normal launcher work.
- [ ] Report status matches actual evidence; screenshots are legible.
- [ ] Team can explain original design decisions and acknowledge assistance according to course policy.

The implementation and previous automated evidence cover the technical features. Complete the outstanding verification, screenshots and instructor/team items before declaring the whole project finished.
