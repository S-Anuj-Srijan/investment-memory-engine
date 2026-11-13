HISTORICAL PROTOTYPE DOCUMENT: SQLite/Streamlit only. See README.md and docs/PROJECT_REPORT.md for the current PostgreSQL/Next.js implementation.

# Investment Memory Engine — complete project guide

Prepared from the local source and files on **31 October 2026**.

## 1. What this project does

This is a Python DBMS mini-project for remembering investment decisions and their context. It stores the company, amount, decision, news, manually entered explanation, confidence and optional return. You can add a memory, search past memories by meaning, and display SQL reports.

**Yes, it has a real vector database: ChromaDB.** SQLite holds structured records; ChromaDB holds searchable text embeddings. Both persist locally. There is no external database server to start, API key, live stock feed, trading integration, LLM-generated explanation or model training. All seed news, decisions and returns are fictional.

The two names in the SQL `models` table are descriptive labels for simulated reasoning sources. They are different from the actual pretrained text embedding model, `sentence-transformers/all-MiniLM-L6-v2`.

## 2. How to run it on this Windows computer

Open PowerShell in the project directory:

```powershell
Set-Location 'C:\Users\text2\Desktop\dbms_mini\Codex_Investment_Memory_Engine\Codex_Investment_Memory_Engine'
```

### Quick start with the existing environment

The inspected folder already contains `.venv`, a seeded SQLite database, Chroma files and a model cache. Start the application with:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open **http://localhost:8501**. Keep the terminal open. Stop the server with **Ctrl+C**. Reopening the application preserves saved records. You do not need to activate the virtual environment.

If the search page reports missing or pending vectors, stop the app and run:

```powershell
.\.venv\Scripts\python.exe init_db.py --rebuild-index
.\.venv\Scripts\python.exe -m streamlit run app.py
```

### Full setup on a new machine

Use Python 3.11 or newer; the README recommends 3.11/3.12. The local environment inspected here uses Python 3.13.9.

The automated setup installs requirements, initializes SQLite and Chroma, runs smoke/UI checks, and starts Streamlit only if the preceding steps succeed:

```powershell
powershell -ExecutionPolicy Bypass -File .\setup_and_run.ps1
```

Alternatively, run each step yourself:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe init_db.py
.\.venv\Scripts\python.exe tests/smoke_check.py
.\.venv\Scripts\python.exe tests/ui_check.py
.\.venv\Scripts\python.exe -m streamlit run app.py
```

First setup needs internet for packages and the embedding model. After installation and a complete model download, computation and storage are local. Keep `data/model_cache/` for offline demonstrations. A cache directory alone is not proof that every required model file exists; a successful full smoke test is stronger evidence.

### Installed packages and declared requirements

| Component | Requirement in requirements.txt | Installed when inspected |
| --- | --- | --- |
| Python | README: 3.11+ | 3.13.9 |
| Streamlit | `>=1.50,<2` | 1.66.1 |
| ChromaDB | `>=1.0,<2` | 1.5.9 |
| Sentence Transformers | `>=3.4,<6` | 5.7.0 |
| SQLite interface | Python standard-library `sqlite3` | Included with Python |

The file specifies version ranges, not an exact dependency lock. ReportLab and Playwright are optional report/screenshot tooling, not application requirements.

## 3. A complete demonstration (about 7–10 minutes)

### Prepare before presenting

1. Run the full smoke test and UI check from section 2.
2. Start Streamlit and try semantic search once to warm up the model.
3. Keep `sql/03_schema.sql`, `sql/05_reports.sql`, `diagrams/03_latest_handwritten_reference.png`, `PROJECT_REPORT.pdf`, and `VIVA_PREPARATION.md` ready.
4. Check the saved-memory count. The inspected database contains eight memories. Repeated practice saves will change counts and reports.

### Step 1 — introduce the problem

Say: “A normal investment database records what was invested and the outcome. This project also preserves the news and stated reason behind each decision, so related past contexts can be found using natural language. SQLite stores exact facts and ChromaDB supports semantic retrieval.”

State that the demonstration data is fictional.

### Step 2 — show the relational database

Open **Add Investment Memory** and its saved-memory table. Show the five tables in `sql/03_schema.sql` and explain primary keys, foreign keys and the relationships in section 5.

The initial dataset has five companies, two model labels, six news items, eight investments and eight reasoning rows. Several investments can reuse a company, model or news item.

### Step 3 — show the vector database through semantic search

Select **Search Memories**, enter the following and click **Search Memories**:

> Companies benefiting from increased AI infrastructure spending

Show the returned company, news, explanation, model label, decision, amount, fictional return and cosine similarity. Search returns at most three linked memories. With the seed dataset, the test expects at least one NVIDIA or AMD match; exact ordering is not fixed.

Say: “The same pretrained model embeds both stored text and my query. Chroma finds nearby vectors, and their reasoning IDs retrieve the full relational records from SQLite.”

The similarity score is `1 - cosine distance`; it measures textual similarity, not predicted profit or confidence. The confidence slider is a separate manually entered value.

### Step 4 — add a new memory

Select **Add Investment Memory**. Use these values:

| Form field | Demonstration value |
| --- | --- |
| Company | NVIDIA; select existing company |
| New company name/ticker/sector | Leave blank |
| Investment amount (INR) | 2500 |
| Investment date | 2026-10-31 |
| Decision | BUY |
| Model name | Demo Reasoning Model / v1 |
| News headline | Simulated expansion of AI data centres |
| News content | A fictional cloud provider plans new AI data centres and increased spending on GPU accelerators. |
| News publication date | 2026-10-30 |
| Investment reasoning | Simulated decision: increased AI infrastructure spending could increase demand for NVIDIA accelerators. |
| Confidence | 0.80 |
| Return is known | Check it |
| Return percentage (fictional) | 4.0 |

Click **Save Investment Memory once**. The full success message confirms both SQL saving and Chroma indexing. Starting from eight memories, the saved table should now show nine.

If SQL saved but indexing failed, do not submit the form again: that would create another investment. Repair the index using `init_db.py --rebuild-index`.

Return to **Search Memories** and search:

> GPU demand from new AI data centres

Inspect the results. Similar existing records may rank higher; the saved-memory table independently confirms persistence. The interface does not offer edit/delete controls.

### Step 5 — demonstrate all three SQL reports

Select **SQL Reports** and expand each **View SQL** panel.

| Report | Concepts to explain | Seed result |
| --- | --- | --- |
| Average investment return by company | JOIN, AVG, GROUP BY, ROUND, ORDER BY | NVIDIA 6%; Microsoft 3%; JPMorgan Chase 1.75%; AMD 1.5%; Exxon Mobil -1.5% |
| Total investments by sector | JOIN, COUNT, GROUP BY | Technology 5; Finance 2; Energy 1 |
| Top five investments ranked by return | JOIN, ORDER BY DESC, LIMIT 5 | 8%, 5%, 4%, 3%, 2.5% |

After adding the exact example once, Technology becomes **6**, NVIDIA's average becomes **5.33%**, and the top returns become **8%, 5%, 4%, 4%, 3%**. Ties can appear in either order. This proves reports read current data.

Unknown returns are SQL `NULL` and excluded from average/ranking reports. A known zero is included. Sector counts include investments regardless of whether a return is known.

### Step 6 — finish with architecture and recovery

Explain that SQLite is the source of truth and the vector index can be rebuilt. SQL writes are transactional, but there is no single transaction spanning SQLite and Chroma. The project preserves context; it does not predict future investment performance.

## 4. Architecture and vector database details

```text
User -> Streamlit app.py
          |
          +-> database.py -> SQLite data/investments.db
          |                   companies / models / news
          |                   investments / investment_reasoning
          |
          +-> vector_store.py -> all-MiniLM-L6-v2 -> ChromaDB data/chroma/

Search text -> query embedding -> Chroma top 3
            -> metadata.reasoning_id -> SQLite JOIN -> result cards
```

| Vector property | Implementation |
| --- | --- |
| Database | Embedded, persistent ChromaDB via `PersistentClient` |
| Storage | `data/chroma/` by default |
| Collection | `investment_memories` |
| Embedding model | `sentence-transformers/all-MiniLM-L6-v2` |
| Vector length | 384 numbers; checked by the full smoke test |
| Embedded document | Headline + newline + news text + newline + reasoning text |
| Unit of indexing | One vector per `investment_reasoning` row |
| Vector ID | SQL `vector_memory_id`, such as `memory_1` |
| Metadata | Integer `reasoning_id` |
| Similarity index configuration | HNSW with cosine distance |
| Embedding normalization | `normalize_embeddings=True` |
| Result count | `min(3, collection.count())` |
| Updating | Upsert with stable IDs avoids duplicate vector entries |
| Model loading | First attempts local cache, then download if needed |

Chroma's `chroma.sqlite3` is part of Chroma's internal persistence. It is separate from the application's relational `investments.db`. Binary files inside the UUID-named directory hold vector-index data; do not edit them manually.

### Save flow

1. Validate required text, positive finite amount, BUY/SELL decision, confidence range, finite optional return and ISO dates.
2. In one SQLite transaction, optionally add a company and insert the news, investment and reasoning rows.
3. Set the stable vector ID to `memory_<reasoning_id>` and commit SQL.
4. Generate the embedding and upsert it into Chroma.
5. Report full success, or preserve SQL and show an indexing-repair warning.

### Search and rebuild flow

Search embeds the query, asks Chroma for nearby vectors, and resolves each metadata reasoning ID through a five-table SQL JOIN. It verifies that the returned vector ID matches the SQL record before displaying it.

A rebuild reads all SQL memories, re-embeds/upserts them and deletes stale Chroma IDs. `pending_count()` detects SQL IDs missing from Chroma; it does not verify that existing embeddings reflect the latest text. Rebuild if data has been edited outside the application.

## 5. Complete relational schema

| Table | Columns and constraints | Purpose |
| --- | --- | --- |
| `companies` | `company_id INTEGER PRIMARY KEY`; `company_name TEXT NOT NULL`; `ticker TEXT NOT NULL UNIQUE`; `sector TEXT NOT NULL` | Company identity and sector |
| `models` | `model_id INTEGER PRIMARY KEY`; `model_name TEXT NOT NULL`; `version TEXT NOT NULL` | Simulated reasoning-source labels |
| `news` | `news_id INTEGER PRIMARY KEY`; `headline`, `news_text`, `published_at` all TEXT NOT NULL; `source TEXT NOT NULL DEFAULT 'Demo / simulated'` | News context |
| `investments` | `investment_id INTEGER PRIMARY KEY`; required `company_id`, `model_id`; positive `investment_amount REAL`; `decision TEXT` restricted to BUY/SELL/HOLD; `trade_date TEXT NOT NULL`; nullable `return_percentage REAL` | Decision and outcome |
| `investment_reasoning` | `reasoning_id INTEGER PRIMARY KEY`; required `investment_id`, `news_id`, `reasoning_text`; nullable `confidence REAL` constrained to 0–1; `vector_memory_id TEXT UNIQUE` | Explanation and vector link |

Relationships:

- `investments.company_id` references `companies.company_id` (one company to many investments).
- `investments.model_id` references `models.model_id` (one model label to many investments).
- `investment_reasoning.investment_id` references `investments.investment_id` (one investment to many reasoning rows).
- `investment_reasoning.news_id` references `news.news_id` (one news item to many reasoning rows).

The current form creates one news item and one reasoning row per investment. SQLite foreign-key enforcement is enabled on every application connection. Indexes `idx_investments_company` and `idx_reasoning_investment` support relational lookups. Cross-store links to Chroma are managed in Python, not SQL foreign keys.

The schema allows HOLD and nullable confidence, but the form/save function accepts BUY/SELL and requires numeric confidence. Dates are stored as text; Python validates dates on the save path. Monetary amounts and returns use REAL, appropriate for this lab demonstration rather than exact financial accounting.

## 6. Entire project folder and content map

Generated dependency/cache subtrees are grouped below rather than listing every installed library or model blob. All application source, SQL, documentation and supporting artifact categories are included.

```text
Codex_Investment_Memory_Engine/
|-- info.md                         This complete guide
|-- README.md                       Existing setup, demo and recovery guide
|-- app.py                          Streamlit application
|-- database.py                     Relational database operations
|-- vector_store.py                 Embeddings and Chroma operations
|-- init_db.py                      Initialization/rebuild/reset CLI
|-- setup_and_run.ps1                Windows install/test/start workflow
|-- requirements.txt                Three direct runtime dependencies
|-- .gitignore                      Generated/local-file exclusions
|-- .streamlit/config.toml          Disables source watching to avoid optional vision imports
|-- CODEX_PROMPT.txt                 Original project-build requirements
|-- VIVA_PREPARATION.md              Oral-exam questions and answers
|-- PROJECT_REPORT.pdf              Generated academic report
|-- sql/
|   |-- 03_schema.sql               Five tables, constraints and indexes
|   |-- 04_demo_data.sql            Fictional seed dataset
|   `-- 05_reports.sql              Three UI reports + optional fourth report
|-- data/
|   |-- investments.db              Application SQLite database
|   |-- chroma/
|   |   |-- chroma.sqlite3          Chroma internal persistent database
|   |   `-- <UUID>/                 HNSW index directory
|   |       |-- data_level0.bin
|   |       |-- header.bin
|   |       |-- length.bin
|   |       `-- link_lists.bin
|   `-- model_cache/
|       |-- CACHEDIR.TAG
|       |-- blobs/                  Download/cache blobs and references
|       `-- models--sentence-transformers--all-MiniLM-L6-v2/
|           `-- ...                 Model blobs, revision refs and cached files
|-- tests/
|   |-- smoke_check.py              Relational and vector integration tests
|   |-- ui_check.py                 Streamlit AppTest checks
|   `-- __pycache__/                Generated bytecode
|-- diagrams/
|   |-- 01_handdrawn_ER_diagram.png
|   |-- 02_handdrawn_architecture.png
|   `-- 03_latest_handwritten_reference.png
|-- docs/
|   |-- build_report.py             ReportLab academic-report generator
|   |-- 06_project_deliverables.pdf  Preserved original draft/deliverables
|   |-- TEST_RESULTS.md             Historical verification record
|   |-- full_smoke_output.txt       Historical smoke-test failure log
|   |-- screenshots/
|   |   |-- 01_add.png
|   |   |-- 02_reports.png
|   |   `-- 03_search_setup.png
|   `-- __pycache__/                Generated bytecode
|-- tmp/
|   |-- capture.py                  Optional browser screenshot helper
|   `-- pdf/                        Report rendering/review artifacts
|       |-- page_1.png ... page_14.png
|       |-- contact_0.png ... contact_3.png
|       |-- confirmed_srn.png
|       `-- query_update.png
|-- .venv/                          Local Python interpreter and packages
`-- __pycache__/                    Generated application bytecode
```

### Source-level responsibilities

| File | Important content |
| --- | --- |
| `app.py` | Initializes SQL on startup; displays exactly three sidebar pages; saves form inputs, invokes indexing, displays search cards and report tables; catches setup/save errors. |
| `database.py` | `ROOT`, `DATA`, `DB_PATH` locate storage; `connect()` enables foreign keys and manages commit/rollback/close; `initialize()` creates schema and seeds only when all five tables are empty under a write lock; `rows()` executes SQL with parameters; `MEMORY_SQL` joins all five tables; `memories()`/`memory()` fetch joined records; `reports()` runs the first three SQL statements; `save_memory()` validates and inserts related records. |
| `vector_store.py` | `model()` and `collection()` are cached loaders; `document()` joins source text; `index_memories()` embeds and upserts; `rebuild_index()` reconciles SQL and Chroma; `pending_count()` finds missing IDs; `search()` returns linked top-three results with distance/similarity. |
| `init_db.py` | Supports `--sql-only`, `--rebuild-index`, `--reset`, `--yes`; normal initialization already rebuilds the index, so `--rebuild-index` makes the maintenance intent explicit rather than selecting a different indexing algorithm. Reset requires confirmation flag and cannot be combined with SQL-only mode. |
| `setup_and_run.ps1` | Works from its own directory, creates `.venv` if absent, installs requirements, initializes databases, runs both checks, then launches Streamlit; aborts on failed steps. |
| `sql/03_schema.sql` | Authoritative table definitions, constraints, foreign keys and two indexes. |
| `sql/04_demo_data.sql` | Five companies: NVIDIA, AMD, Microsoft, JPMorgan Chase and Exxon Mobil; two model labels; six news items; eight investments/reasoning rows. |
| `sql/05_reports.sql` | Average return by company, investments by sector, top-five returns; an additional return-by-model query exists but is not displayed by the app. |
| `tests/smoke_check.py` | Uses temporary storage via `IME_DATA_DIR`; checks schema, seed idempotency, constraints, report values, validation/rollback, vector dimensions/documents/metadata, semantic relevance, repair, and saving/indexing a ninth memory. `--sql-only` skips vector checks. |
| `tests/ui_check.py` | Uses isolated SQL/Chroma storage and Streamlit's test runner; checks all three pages, eight initial rows, three report tables, blank search rejection and invalid-save rejection. It does not automate a successful browser search or valid UI save. |
| `docs/build_report.py` | Generates `PROJECT_REPORT.pdf` using ReportLab, original diagrams, SQL and screenshots. It is not needed to run the app. |
| `tmp/capture.py` | Optional Playwright helper; expects Chrome at a hardcoded Windows path and Streamlit on port 8502; captures the three pages. Its output wording describes the historical missing-dependency state. |

### Documentation, binaries and generated files

- `README.md` contains detailed presentation text and commands, but its old dependency-blocked status predates this inspection.
- `VIVA_PREPARATION.md` explains DBMS concepts, embeddings, similarity, transactions, relationships and limitations.
- `CODEX_PROMPT.txt` records the original build specification; the current code is authoritative for implemented behavior.
- `PROJECT_REPORT.pdf` is the generated academic deliverable; `docs/06_project_deliverables.pdf` preserves the original draft. PDF contents were not re-rendered or re-reviewed during this documentation task.
- `diagrams/` preserves three supplied image references. Consult SQL for exact column names and constraints.
- `docs/TEST_RESULTS.md`, `docs/full_smoke_output.txt` and the existing screenshots are historical evidence, not fresh verification. In particular, the search screenshot records a setup warning, not successful retrieval.
- `tmp/pdf/` contains previously generated page images, contact sheets and review crops; it is not runtime input.
- `.venv/` contains installed third-party packages. Recreate it from requirements on another machine instead of treating it as portable application source.
- `__pycache__/` directories contain generated Python bytecode and are not authored source.
- `.gitignore` excludes `.venv/`, `.deps/`, `__pycache__/`, `.pytest_cache/`, `data/` and `tmp/`. Therefore a Git checkout may not include the saved databases or model cache; initialization recreates the seed database and index.

## 7. Inspect the databases during the presentation

Run these from a second PowerShell window in the project folder:

```powershell
# Application tables:
.\.venv\Scripts\python.exe -c "import database; print(database.rows('SELECT name FROM sqlite_master WHERE type=?', ('table',)))"

# Existing foreign-key violations: expected []
.\.venv\Scripts\python.exe -c "import database; print(database.rows('PRAGMA foreign_key_check'))"

# Saved relational memories:
.\.venv\Scripts\python.exe -c "import database; print(len(database.memories()))"

# Chroma collection name and vector count:
.\.venv\Scripts\python.exe -c "import vector_store; c=vector_store.collection(); print(c.name, c.count())"

# Inspect one vector's document, metadata and dimensionality:
.\.venv\Scripts\python.exe -c "import vector_store; r=vector_store.collection().get(ids=['memory_1'], include=['documents','metadatas','embeddings']); print(r['ids']); print(r['metadatas']); print(r['documents']); print('Dimensions:',len(r['embeddings'][0]))"

# Search directly without Streamlit:
.\.venv\Scripts\python.exe -c "import vector_store; print([(r['ticker'],round(r['similarity'],4)) for r in vector_store.search('Companies benefiting from increased AI infrastructure spending')])"
```

The application functions can create missing storage on first use, so use them after setup. Do not alter or delete internal Chroma files while demonstrating.

## 8. Maintenance, backup and troubleshooting

Stop Streamlit before maintenance. To back up saved content, copy the complete `data/` directory while the app is stopped. SQLite is the authoritative record; the model cache avoids downloads and Chroma can be rebuilt from SQL.

```powershell
# Initialize SQL only: does not enable semantic search
.\.venv\Scripts\python.exe init_db.py --sql-only

# Rebuild/repair vector index while preserving SQL records
.\.venv\Scripts\python.exe init_db.py --rebuild-index

# DESTRUCTIVE: discard added records and restore the original seed dataset
# Run only if you deliberately want to erase your practice additions.
.\.venv\Scripts\python.exe init_db.py --reset --yes
```

`IME_DATA_DIR` can override the directory containing SQL and Chroma files; tests use it for isolation. The embedding cache still uses the project's `data/model_cache/`. Leave this variable unset for the normal demonstration.

| Symptom | Remedy |
| --- | --- |
| Python not found | Install Python with PATH enabled and reopen PowerShell. |
| Missing module | Install requirements using `.venv\Scripts\python.exe`; run with that same interpreter. |
| Model download/setup failure | Complete setup with internet access; rerun initialization. No fake vectors are substituted. |
| SQL saved but vector indexing failed | Do not save again; fix setup and rebuild the index. |
| No indexed or pending memories | Run the rebuild command, then restart the app. |
| Duplicate ticker error | Select the existing company or use a genuinely new unique ticker. |
| Unexpected report values | Added demonstration records change aggregates; inspect the saved table. |
| Port 8501 occupied | Append `--server.port 8502` to the Streamlit command and visit `http://localhost:8502`. |
| Old PDF/screenshot says dependencies are missing | That artifact records an earlier environment; use the current checks below. |
| Repeated `Examining the path of transformers...` / missing `torchvision` traces | Streamlit's source watcher is inspecting optional vision modules. `.streamlit/config.toml` disables source watching. Stop and restart Streamlit from the project folder. This text model does not require torchvision. Restart after source edits; normal form/search interactions still work. |

To regenerate the academic PDF when desired:

```powershell
.\.venv\Scripts\python.exe -m pip install reportlab
.\.venv\Scripts\python.exe docs/build_report.py
```

This rewrites the generated report; it does not automatically refresh screenshots. The report was not regenerated as part of preparing this guide.

## 9. Verification for this guide

Read-only inspection of the saved SQLite database found **5 companies, 2 models, 6 news rows, 8 investments and 8 reasoning rows**, with **no foreign-key violations**. Installed dependency versions are recorded in section 2.

Fresh checks on **31 October 2026**:

| Check | Result |
| --- | --- |
| `.venv\Scripts\python.exe tests/smoke_check.py` | PASS: all five tests, including real 384-dimensional embeddings, eight indexed records, semantic relevance, index repair and a ninth saved/indexed memory; approximately 115 seconds. |
| `.venv\Scripts\python.exe tests/ui_check.py` | PASS: all three pages, seed table, report tables, blank search and invalid save. |
| Existing saved Chroma collection | `investment_memories`: 8 vectors, 0 pending SQL memories. |
| Search against saved data | The AI infrastructure example returned NVDA (0.7599), AMD (0.7391), MSFT (0.6551). These are observed cosine similarities, not fixed expected outputs. |

These tests use disposable databases and preserve your demonstration records. They reuse the project's model cache. The full vector workflow is now verified in this environment; the older dependency-blocked notes in README and `docs/TEST_RESULTS.md` are historical. UI checks use Streamlit AppTest, not a manual browser walkthrough. Run the presentation steps yourself once before presenting.

## 10. Scope and viva points

- This is a hybrid relational/vector storage demonstration, not a trading advisor.
- SQL gives exact filtering, constraints, joins and aggregates. Embeddings retrieve similar language/context.
- Embeddings are numerical representations, not attention weights or verified internal model reasoning.
- Semantic similarity is approximate; unrelated queries can still return nearest records because no minimum similarity threshold is implemented.
- Long text can be truncated by the embedding model. Keep demo explanations concise.
- There is no authentication, user separation, live market data, automatic news collection or UI update/delete feature.
- SQL transactions protect related SQL inserts, but indexing happens after commit and can require recovery.
- A successful retrieval demonstrates a related historical context, not causation or a profitable future action.
