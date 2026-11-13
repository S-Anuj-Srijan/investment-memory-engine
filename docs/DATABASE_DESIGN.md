# Database design and implementation

## Problem-driven database choices

PostgreSQL is the authoritative transactional database. Company/model references, dated decisions, numeric outcomes, ownership, sessions and audits need constraints, joins, aggregation and atomic multi-table updates. Chroma stores a rebuildable semantic index over unstructured news and reasoning. Similar investments can use different words, so an exact SQL text match alone does not address memory reuse.

Next.js sends same-origin requests through its /api proxy to FastAPI. FastAPI authorizes the user and uses parameterized Psycopg statements. It reads PostgreSQL for structured data and verifies Chroma hits against current PostgreSQL rows before returning them.

## ER model

The report uses the supplied diagram `diagrams/erdiagram.png`. The implemented schema and data dictionary below remain the reference for database behavior. The supplied illustration includes a DEPENDENTS entity that is not implemented; audit_log.actor_id references users, rather than sessions as drawn.

- Company 1 to 0..many Investments. Every investment has exactly one company.
- Model 1 to 0..many Investments. Every investment has exactly one reasoning model/version.
- Investment 1 to 0..many InvestmentReasoning. The application creates one reasoning row per new investment; the schema permits multiple evidence links.
- News 1 to 0..many InvestmentReasoning. Seed news may support several investments.
- User 1 to 0..many Investments. Creator is optional for imported/seed records.
- User 1 to 0..many Sessions. Each session has one user and an expiry.
- User 1 to 0..many AuditLog events. Actor can be null for initialization/direct SQL without actor context.
- InvestmentReasoning 1 to 0..1 derived Chroma entry, linked by unique vector_memory_id. This is an application-verified cross-store link, not a SQL FK.
- AuditLog.record_id intentionally has no FK to investments: history must survive deletion. It records the original investment ID.

## Relational schema and data dictionary

| Relation | Attributes and types | Keys and constraints |
|---|---|---|
| users | user_id BIGINT identity; email TEXT; display_name TEXT; password_hash TEXT; role TEXT; created_at TIMESTAMPTZ | PK user_id; UNIQUE lowercase email with shape CHECK; nonblank name; scrypt hash; role admin or analyst |
| sessions | token_hash TEXT; user_id BIGINT; expires_at TIMESTAMPTZ | PK 64-character SHA256 token_hash; FK user_id to users ON DELETE CASCADE; expiry checked during each authenticated request |
| companies | company_id BIGINT identity; company_name TEXT; ticker TEXT; sector TEXT | PK company_id; UNIQUE ticker; nonblank names/sector; uppercase ticker pattern |
| models | model_id BIGINT identity; model_name TEXT; version TEXT | PK model_id; UNIQUE(model_name,version); nonblank strings |
| news | news_id BIGINT identity; headline TEXT; news_text TEXT; published_at DATE; source TEXT | PK news_id; required typed date; bounded nonblank text; synthetic source default |
| investments | investment_id BIGINT identity; company_id BIGINT; model_id BIGINT; investment_amount NUMERIC(16,2); decision TEXT; trade_date DATE; return_percentage NUMERIC(10,4); created_by BIGINT nullable; revision INTEGER | PK investment_id; FK company/model/creator; amount positive and finite through bounded CHECK; BUY/SELL/HOLD; return null or -100..100000; positive revision |
| investment_reasoning | reasoning_id BIGINT identity; investment_id BIGINT; news_id BIGINT; reasoning_text TEXT; confidence NUMERIC(5,4); vector_memory_id TEXT | PK reasoning_id; FK investment ON DELETE CASCADE; FK news; nonblank bounded reasoning; confidence 0..1 NOT NULL; unique nonnull vector ID |
| audit_log | audit_id BIGINT identity; table_name TEXT; record_id BIGINT; operation TEXT; actor_id BIGINT nullable; old_data JSONB; new_data JSONB; occurred_at TIMESTAMPTZ | PK audit_id; FK actor to users; INSERT/UPDATE/DELETE CHECK; no FK on deleted entity identifier |

All nonnullable columns are explicitly declared NOT NULL. PostgreSQL's typed DATE rejects invalid dates. Numeric CHECK bounds reject NaN and infinities as well as out-of-range values. Unknown outcomes are NULL, never a fictional zero. Primary/unique keys create indexes automatically. Additional indexes cover company/model FKs, reasoning investment/news FKs, company sector and session expiry.

## Normalization

The core relations separate companies, model versions, news, decisions and reasoning. Company and model facts depend on their own keys, not investment IDs; repeated news is stored once and referenced. This prevents repeating company names, sector data and model versions in every trade. Each core entity is in 3NF under the domain dependencies above. `memory_details` reconstructs the read model with joins; no redundant joined copy is stored in PostgreSQL. Audit JSON intentionally stores historical snapshots rather than normalized current facts.

## Views, function and trigger

`memory_details` joins reasoning, investments, companies, models and news. `company_performance` LEFT JOINs companies to investments, counting decisions and aggregating amounts and known outcomes.

`audit_investment_change()` is a PL/pgSQL trigger function. `investment_audit` runs AFTER INSERT/UPDATE/DELETE on investments. It stores old and new JSON values, operation, timestamp and `app.actor_id`, set transaction-locally by the backend. Seed activity has a null actor. Audit records participate in the same transaction, so a rolled-back write does not leave a false successful audit entry.

## Transactions and concurrent access

Creation inserts the optional company, news, investment, reasoning and audit in one transaction. Any exception rolls everything back. Outcome updates lock the investment and compare its revision to the client's version; conflicts return HTTP 409 instead of silently overwriting another edit. Deletion locks reasoning, deletes it, removes an investment only if no reasoning remains, and removes news only if no remaining reasoning refers to it. Shared news is preserved. SQL initialization uses an advisory transaction lock and seeds only an empty company dataset.

## Vector model and retrieval

Collection: `investment_memories_v2`. Persistent location: CHROMA_PATH, default `data/chroma_v2`. Document text is headline + news_text + reasoning_text separated by newlines. One document corresponds to one reasoning row. The text excludes passwords, sessions and user account data.

Encoder: sentence-transformers/all-MiniLM-L6-v2; 384 floating-point coordinates, normalized by the encoder. Long texts are subject to the model's tokenizer limit and may be truncated; chunked evidence is future work. Metadata contains reasoning_id, model name and a SHA256 fingerprint of the document. The HNSW index uses cosine distance. Similarity is 1 - distance, nominally -1 to 1, and is not a probability or prediction.

The query is embedded using the same model. For this small dataset all nearest neighbors are retrieved, current SQL sector/decision filters and document fingerprints are checked, and the first five valid results are returned. This favors correctness and simplicity over large-scale performance. Missing/pending embeddings produce no false hit. Deleted SQL rows are immediately excluded even if their vectors remain. Fingerprint mismatches are excluded until repaired.

Rebuild upserts current SQL records and removes orphan vector IDs. It is repeatable. No distributed transaction across PostgreSQL and Chroma is claimed: SQL commits first, indexing is an explicit admin operation. A single worker and local lock serialize index/search operations; durable background jobs and multiworker coordination are future enhancements.

## Security boundaries

Passwords use scrypt with a fresh random salt; session cookies contain random opaque tokens and PostgreSQL stores only SHA256 hashes of those tokens. Cookies are HttpOnly, SameSite=Strict and expire after eight hours. Secure cookies must be enabled for HTTPS deployment. Mutations require the configured Origin. SQL parameters carry all user input; no raw SQL endpoint is exposed. UI role hiding is convenience; the API independently enforces authorization and ownership. Login attempts are throttled to ten per five minutes per API-visible client address. Behind the local Next.js proxy this can be shared by local users; multiuser deployment needs trusted proxy handling and a durable limiter.

The local lab uses an owner account to initialize and demonstrate DDL. This is not a production least-privilege deployment: a hosted installation should separate migration ownership from a restricted application role. Admins cannot change or erase audit history through the API, but a PostgreSQL owner can; the audit is not tamper-proof against database administrators.
