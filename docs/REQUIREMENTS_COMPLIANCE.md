# DBMS Level 3 requirements checklist

Source: `DBMS Level 3 Project Requirements draft.docx`, supplied in the project root. Checked on 1 November 2026. The Investment Memory Engine concept is retained. Technical implementation is complete subject to the visual verification and student-owned submission evidence identified below.

| Requirement | Implementation or evidence | Status |
|---|---|---|
| Unique title and meaningful real-world problem | Investment Memory Engine preserves reasons, context and outcomes; semantic reuse goes beyond CRUD | Implemented; section uniqueness needs instructor confirmation |
| Approved two-member team | S Anuj Srijan PES1UG24AM234 and Aswin Adhitya PES1UG24AM213; docs/TEAM.md | Identities provided; approval pending |
| Both members contribute to database and app | Proposed responsibility split in docs/TEAM.md | Actual contributions pending |
| Mandatory MySQL or PostgreSQL | backend/db.py, sql/03_schema.sql; real PostgreSQL 16.15 tested | Implemented and tested |
| Second database paradigm | Chroma vector collection with real MiniLM embeddings | Implemented and tested |
| ER diagram to relational schema; attributes, PK, FK, relationships, constraints | docs/DATABASE_DESIGN.md and diagrams/04_current_ER.svg | Documented |
| Vector data model, collection, index, embeddings, metadata, retrieval | docs/DATABASE_DESIGN.md and backend/vectors.py | Documented and tested |
| DDL CREATE, ALTER, DROP | sql/03_schema.sql; safe temporary table lab sql/06_advanced_demo.sql | Executed in integration test |
| PK, FK, constraints, indexes, views | PostgreSQL schema and direct SQL rejection tests | Implemented and tested |
| INSERT, UPDATE, DELETE, SELECT | Memory creation, outcome update, admin deletion, reports and retrieval | Implemented and tested |
| JOIN, GROUP BY, HAVING, ORDER BY, aggregates, subqueries | Six API reports; sql/05_reports.sql and sql/06_advanced_demo.sql | Implemented and tested |
| At least four advanced concepts | Transactions, views, stored trigger function, trigger, indexing, vector similarity search (six) | Implemented; behavior tested |
| Explain embedded data, model, metric and retrieval | MiniLM 384 dimensions, news plus reasoning, cosine, top five current matches | Documented and tested |
| Functional Next.js web interface | web/app/page.js; production build and HTTP integration checks | Built and HTTP-tested; browser visual QA pending |
| Backend/API integration | Next.js /api proxy to FastAPI to PostgreSQL/Chroma | HTTP integration passed |
| Environment configuration; no hardcoded credentials | .env.example, backend/db.py, Next.js server-side API_URL | Implemented |
| Relevant authentication and minimum two roles | Admin and analyst; opaque sessions; server-enforced ownership and role checks | Implemented and tested |
| Database-level validation and consistency | NOT NULL, CHECK, UNIQUE, FK, typed DATE/NUMERIC, atomic multi-table writes, optimistic revision | Tested directly and through API |
| Basic web/database security; no plaintext password storage | scrypt hashes, hashed session tokens, HttpOnly/SameSite cookies, origin checks, parameterized SQL, throttling | Implemented and tested |
| Problem, objectives, scope, functional requirements | docs/PROJECT_REPORT.md | Documented |
| Database choice, dictionary, implementation, queries, architecture | docs/DATABASE_DESIGN.md, report, SQL and backend | Documented |
| Application screenshots | Old Streamlit captures are historical only; docs/DEMO_GUIDE.md lists required Next.js captures | Pending: computer-use approval timed out |
| Testing results | docs/TEST_RESULTS.md; tests/test_backend.py | Seven real test groups passed; Next.js build and proxy HTTP check passed |
| Conclusion and future enhancements | docs/PROJECT_REPORT.md | Documented |
| Git/GitHub and individual commit contributions | Public repository created; individual contribution history not fabricated | Team review of contributions pending |
| README setup and execution | README.md, start_project.ps1, compose.yaml, .env.example | Provided; local stack tested |
| Final demo contents | docs/DEMO_GUIDE.md; VIVA_PREPARATION.md | Script prepared; student presentation pending |
| Originality and beyond CRUD | Evidence/context/outcome model, semantic reuse, audited outcomes and index repair | Implemented; team must review and acknowledge assistance |

## Advanced concept evidence

1. Transactions: one PostgreSQL transaction creates company/news/investment/reasoning; invalid model FK rolls back all inserted rows.
2. Views: `memory_details` joins the normalized relations; `company_performance` aggregates company outcomes.
3. Stored function: `audit_investment_change()` executes inside PostgreSQL.
4. Triggers: `investment_audit` stores before/after values and actor identity for inserts, updates and deletes.
5. Indexing: unique/primary indexes and explicit FK/sector/session indexes; inspect with EXPLAIN ANALYZE.
6. Vector similarity search: HNSW cosine retrieval over MiniLM embeddings, revalidated against authoritative SQL data.

No requirement is declared satisfied by a renamed SQLite database, a Streamlit screenshot, a mock vector, or fabricated student history.
