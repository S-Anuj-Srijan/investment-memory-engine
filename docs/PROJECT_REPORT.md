# Investment Memory Engine

DBMS Experiential Learning Level 3 project report

Team: S Anuj Srijan (PES1UG24AM234) and Aswin Adhitya (PES1UG24AM213)

Implementation review date: 1 November 2026

## Problem statement

Investment records often retain a company, amount and outcome while losing the news and reasoning behind the decision. Without this context, later researchers cannot reliably compare a new situation with an earlier thesis. Investment Memory Engine preserves the decision, its evidence, the reasoning model and the observed outcome, then retrieves related past decisions by semantic meaning.

## Objectives

Maintain consistent structured investment records with relational constraints. Preserve unstructured news and reasoning alongside each decision. Retrieve semantically related memories using real embeddings. Evaluate fictional outcomes through SQL reports. Support two user roles, ownership-aware outcome updates and an auditable change history. Demonstrate the relationship between database design, advanced database concepts and a Next.js interface.

## Scope

This is a local academic research journal using synthetic data. It records BUY, SELL and HOLD decisions but does not execute trades. News and model explanations are entered manually. Returns are recorded observations, not predictions, and may remain unknown. The demonstration includes five companies, two reasoning-model labels, six news articles and eight seeded investment memories. These labels describe the source of recorded reasoning; MiniLM is the separate embedding model used for retrieval.

## Functional requirements

Users authenticate with a hashed password and an expiring server-side session. Analysts create investment memories, search/filter shared research and update their own outcomes. Administrators additionally create accounts, update any outcome, delete memories, view the audit trail and rebuild the vector index. Users view six live SQL reports and inspect the underlying queries. Validation rejects invalid values at both API and PostgreSQL levels. SQL data survives vector-index failures.

## Architecture

The browser renders a Next.js App Router client. Same-origin /api requests are proxied by Next.js to a loopback FastAPI server. FastAPI checks the session, origin and permissions, then executes parameterized PostgreSQL queries through Psycopg. Chroma stores the derived MiniLM index. Search results are joined back to current SQL records and checked for stale text before display. Environment variables supply database credentials and paths.

## Database design

The design contains users, sessions, companies, models, news, investments, investment_reasoning and audit_log. The core investment entities remain the same as the original project. Users, sessions and audits extend the model to meet authentication and accountability requirements. The current ER diagram and complete data dictionary are in docs/DATABASE_DESIGN.md and diagrams/erdiagram.png. Core entity relations follow 3NF; reporting views reconstruct joined data without duplicating current source facts.

PostgreSQL was selected for typed data, foreign keys, transactions, views, aggregation and PL/pgSQL triggers. Chroma was selected because unstructured investment reasoning benefits from semantic retrieval that is independent of literal keyword overlap. Both databases serve a domain need rather than merely adding technology.

## Implementation and advanced concepts

DDL creates the relational tables, primary/foreign keys, CHECK and UNIQUE constraints and indexes. An additive ALTER migration adds creator ownership and revision tracking. A separate temporary-table lab demonstrates CREATE, ALTER and DROP without deleting project data.

Six advanced concepts are implemented: transactions, views, a stored trigger function, an audit trigger, indexing and vector similarity search. Multi-table creation and deletion are atomic. The audit trigger captures before/after investment values and the acting user. Revision checking prevents conflicting outcome edits. SQL reports use JOIN, GROUP BY, HAVING, ORDER BY, AVG, COUNT and a scalar subquery. Indexes support reference lookups; EXPLAIN ANALYZE demonstrates the chosen query plan, which may legitimately scan tiny demo tables.

## Semantic memory implementation

Headline, news content and investment reasoning are concatenated and embedded using sentence-transformers/all-MiniLM-L6-v2. Each normalized vector has 384 dimensions. Chroma stores document text, vector, reasoning ID, model identity and a document fingerprint. Cosine similarity is one minus cosine distance. The first five valid matches are returned after SQL filtering and source validation. Similarity describes text meaning, not financial merit.

New SQL memories are explicitly marked as needing index repair in the UI. Admin rebuild upserts the source rows and removes orphan entries. Deleted memories never appear in search even before physical vector cleanup. Edited source text cannot match using an outdated vector because its fingerprint differs. The system does not pretend that PostgreSQL and Chroma share an atomic distributed transaction.

## Validation and security

The API uses typed validation and length/range checks. PostgreSQL independently enforces nonblank text, legal decisions, nonnegative/finite monetary bounds, confidence ranges, valid dates, unique tickers and foreign keys. Unknown return values use NULL. Role checks are enforced by the server, not just hidden controls.

Password hashes use scrypt with random salts. Opaque session tokens are stored hashed and expire after eight hours. Cookies are HttpOnly and SameSite=Strict; HTTPS deployments must also enable Secure. Origin validation protects mutations. Parameterized SQL prevents user input from becoming executable SQL. Login throttling limits repeated attempts. Secrets remain in ignored environment configuration; neither passwords nor database URLs are embedded in source code.

## Testing results

Seven backend test groups passed against real PostgreSQL 16.15, including real MiniLM and Chroma retrieval. Tests covered seed idempotency, reports and DDL; authentication, role enforcement and CSRF; direct database constraints and transaction rollback; CRUD, ownership, audit and revision conflicts; filtering, account uniqueness and expired sessions; real embeddings and stale/deleted index handling; salted password hashing.

The Next.js 16.4.3 production build passed. A production HTTP check verified the rendered entry page and the full Next.js-to-FastAPI proxy path for login, HttpOnly session cookies, authenticated profile, eight seed memories, six reports, logout and rejected access after logout. Isolated test schemas and temporary vector directories protected user data. See docs/TEST_RESULTS.md for reproducible commands and limitations.

## Interface evidence

The implemented screens are sign-in, Overview, Add memory, Search memories, SQL reports and Administration. Browser visual verification and new screenshots are still pending because computer-use approval timed out. Earlier Streamlit screenshots are retained as historical material only and are not presented as evidence for this interface. docs/DEMO_GUIDE.md provides a capture and walkthrough checklist. No screenshot success is fabricated in this report.

## Team responsibilities

Both team identities are supplied by the user. docs/TEAM.md records a proposed split in which each member works on database and application code. Instructor approval and confirmation of responsibilities remain with the team. The project repository is https://github.com/S-Anuj-Srijan/investment-memory-engine. Individual contribution evidence remains for team review. The team should review and explain all generated code and acknowledge assistance according to course rules.

## Conclusion

Investment Memory Engine now connects a normalized PostgreSQL model, a meaningful Chroma semantic index and a Next.js application while preserving the original project concept. The automated evidence supports transactional integrity, authorization, audit behavior, report queries and semantic consistency. Submission readiness still requires the team's approval/contribution evidence and genuine screenshots of the new interface.

## Future enhancements

Add chunked long-document embeddings, asynchronous indexing with a durable outbox, pagination and vector-side filters for larger datasets, model-version migrations, HTTPS deployment, restricted database roles, a shared rate limiter and optional source-document attachments. Real market data ingestion would require clear provenance and validation and is outside the current scope.
