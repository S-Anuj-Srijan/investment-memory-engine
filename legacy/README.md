# Investment Memory Engine

A small Python DBMS lab project: SQLite stores investment records; ChromaDB stores embeddings of news and manually entered model explanations. All sample news, reasoning and returns are **fictional demonstration data**. There is no trading, external LLM, API key, prediction or model training.

## Is it finished?

The application code, seeded SQLite database, three SQL reports, tests, academic PDF, original diagrams and viva guide are present. SQLite and Streamlit UI checks passed. **End-to-end ChromaDB search has not been verified:** this build environment blocked installation of ChromaDB and Sentence Transformers. Complete the installation and full smoke test below before presenting semantic search as working. The code uses real embeddings; it has no fake-vector fallback.

## Technology stack

| Technology | Purpose |
| --- | --- |
| Python 3.11+ | Application logic and validation |
| SQLite (RDBMS) | Five related tables, constraints, transactions and reports |
| ChromaDB (NoSQL vector database) | Local semantic memory storage and retrieval |
| Sentence Transformers, all-MiniLM-L6-v2 | Convert text into embeddings; no trading model |
| Streamlit | Three simple sidebar pages |

The supplied decisions are predefined simulated examples. Adding a memory means entering another demonstration record manually, not asking an AI to trade.

## Windows PowerShell setup

Open PowerShell in this folder. Use Python 3.11 or newer (3.11/3.12 recommended).

For a single command that installs dependencies, initializes both databases, runs the full smoke and UI checks, and starts the app only if those steps pass:

```powershell
powershell -ExecutionPolicy Bypass -File .\setup_and_run.ps1
```

This applies the script execution policy to that PowerShell process only. If your computer is managed and disallows scripts, use the individual commands below. The script does not reset or delete your saved data.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe init_db.py
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open http://localhost:8501. Directly using the virtual environment's Python avoids PowerShell activation-policy problems.

Keep that PowerShell window open while demonstrating. Press **Ctrl+C** to stop the app. On later runs, you only need the final Streamlit command; your records remain saved.

The first initialization needs internet to download dependencies and the **all-MiniLM-L6-v2** embedding model. Once installed and cached, inference and database operations are local. Keep `data/model_cache/` for offline use. If the download fails, the app gives a setup error; it never uses fake or random vectors.

## Demonstrate the four DBMS requirements (five minutes)

1. **Five related tables:** show `sql/03_schema.sql`: companies, models, news, investments and investment_reasoning. Explain primary/foreign keys. Open Add Investment Memory to show eight saved fictional memories.
2. **RDBMS + NoSQL:** show the SQLite file and Chroma directory under `data/`. Search **Companies benefiting from increased AI infrastructure spending**. Explain how Chroma metadata reasoning_id retrieves the SQL record, company and return.
3. **SQL reports:** open SQL Reports. Expand the actual queries. Explain JOIN with AVG/GROUP BY, JOIN with COUNT/GROUP BY, and ORDER BY/LIMIT. The initial results include NVIDIA average 6%, Technology count 5, and highest fictional return 8%.
4. **Novelty:** add a memory for an existing company with headline, news and explanation. Click Save Investment Memory. Search a related idea and show its context and return. This records *why* a decision was made, not only the amount and date.

The sidebar has exactly three pages. Models are selected from the supplied model table. Choose New company and supply name, ticker and sector to add a company. Return is NULL unless Return is known is checked. Confidence is manually entered. Decisions in the interface are BUY/SELL; the supplied schema's HOLD allowance is preserved.

## Exact presentation script

### Before your professor arrives

1. Install dependencies and initialize the databases while internet is available.
2. Run the full smoke test from the Testing section. It must finish successfully before claiming vector functionality is verified.
3. Start Streamlit, open all three pages, and try the example search once. The first model load may take longer.
4. Keep this README, `sql/03_schema.sql`, `sql/05_reports.sql`, `PROJECT_REPORT.pdf`, and `VIVA_PREPARATION.md` ready.
5. If you want the original eight-row baseline after practice, stop Streamlit and use the explicit reset command below. It deletes added memories.

### 1. Introduce the project (30 seconds)

Say: **"A normal investment database stores what was invested and the return. Our system also preserves the news and the stated reason behind the decision. SQLite stores structured facts, and ChromaDB finds similar past contexts. All decisions and returns in this demonstration are simulated."**

### 2. Explain the five tables (one minute)

Open `sql/03_schema.sql` and the latest handwritten diagram, `diagrams/03_latest_handwritten_reference.png`.

| Table | What it stores | Relationships |
| --- | --- | --- |
| companies | Name, unique ticker and sector | One company has many investments |
| models | Simulated model name and version | One model has many investments |
| news | Headline, content, publication date and source | One news item can support many reasoning rows |
| investments | Company/model references, amount, decision, date and return | One investment can have many reasoning rows |
| investment_reasoning | Investment/news references, explanation, confidence and vector ID | Connects the decision context to ChromaDB |

Say: **"Primary keys identify rows. Foreign keys prevent references to missing parent records. We enable SQLite foreign-key enforcement on every connection. ChromaDB is separate, so its ID link is handled by the application."**

### 3. Demonstrate semantic retrieval (one minute)

Open **Search Memories**, enter this exact query, and click **Search Memories**:

> Companies benefiting from increased AI infrastructure spending

With the supplied sample data, expect at least one relevant NVIDIA or AMD memory. Do not promise an exact ordering or that both companies must appear. Results are ranked by stored text meaning, not a hardcoded company list.

Point out the company, news, explanation, decision, amount, fictional return and score. Say: **"The query is embedded with the same model used for our stored texts. Chroma returns nearby vectors. Their reasoning_id metadata lets us retrieve the corresponding SQL record using JOINs."**

Explain that **cosine similarity = 1 - cosine distance**. Higher means more similar text, not a higher probability of profit. The entered confidence and search similarity are different values.

If the page shows a setup/indexing error, fix it using Troubleshooting below. Do not describe that warning screen as a successful search.

### 4. Add one simulated memory (one minute)

Open **Add Investment Memory** and use this prepared fictional example:

| Field | Value |
| --- | --- |
| Company | NVIDIA (existing company; leave new-company fields blank) |
| Investment amount | 2500 |
| Investment date | 2026-10-26 |
| Decision | BUY |
| Model name | Demo Reasoning Model / v1 |
| News headline | Simulated expansion of AI data centres |
| News content | A fictional cloud provider plans new AI data centres and increased spending on GPU accelerators. |
| News publication date | 2026-10-25 |
| Investment reasoning | Simulated decision: increased AI infrastructure spending could increase demand for NVIDIA accelerators. |
| Confidence | 0.80 |
| Return is known | Checked |
| Return percentage | 4.0 (fictional, chosen solely for the demo) |

Click **Save Investment Memory once**. A complete success message confirms both SQL saving and vector indexing. The saved-memories table should now contain nine rows if you started with the untouched seed.

Search for **GPU demand from new AI data centres**. Inspect the retrieved explanations. Similarity ranking can vary; the saved-memories table confirms persistence even when another similar memory ranks higher.

Say: **"All related SQL inserts form one transaction. After SQL commits, we create and upsert the vector. If that second step fails, we preserve the SQL record and rebuild the index instead of saving a duplicate."**

### 5. Show the SQL reports (one minute)

Open **SQL Reports** and expand each **View SQL** section.

| Report | SQL concept | Expected result before adding records |
| --- | --- | --- |
| Average return by company | JOIN, AVG, GROUP BY, ORDER BY | NVIDIA 6%; Microsoft 3%; JPMorgan Chase 1.75%; AMD 1.5%; Exxon Mobil -1.5% |
| Investments by sector | JOIN, COUNT, GROUP BY | Technology 5; Finance 2; Energy 1 |
| Top five returns | JOIN, ORDER BY DESC, LIMIT 5 | 8%, 5%, 4%, 3%, 2.5% |

After adding the exact example above once, Technology becomes **6** and NVIDIA's average becomes **5.33%**. The top five returns become **8%, 5%, 4%, 4%, 3%**. These changing values demonstrate that reports query the database rather than display fixed results. Tied returns may appear in either order.

Unknown returns are NULL and excluded from averages and rankings; a known zero return is included.

### 6. Close the presentation (20 seconds)

Say: **"Our novelty is preserving and searching the context behind investment decisions. Relational storage gives us constraints and exact reports; vector storage gives us semantic retrieval. This is a database integration demonstration, not a predictive trading system."**

## Optional live database inspection

Run these in a second PowerShell window from the project folder. They do not change records.

```powershell
# List the five application tables:
.\.venv\Scripts\python.exe -c "import database; print(database.rows('SELECT name FROM sqlite_master WHERE type=?', ('table',)))"

# Check for foreign-key violations (expected: []):
.\.venv\Scripts\python.exe -c "import database; print(database.rows('PRAGMA foreign_key_check'))"

# Count saved SQL memories:
.\.venv\Scripts\python.exe -c "import database; print(len(database.memories()))"

# Count indexed Chroma memories after successful setup:
.\.venv\Scripts\python.exe -c "import vector_store; print(vector_store.collection().count())"
```

The foreign-key check reports existing violations; the smoke test also proves that an invalid insert is rejected.

## Data and recovery

- `data/investments.db`: persistent SQLite database, created from the unchanged supplied SQL.
- `data/chroma/`: one persistent collection, `investment_memories`.
- One vector per investment_reasoning row. IDs are memory_1, memory_2, etc. Documents combine headline, news text and reasoning. Metadata contains integer reasoning_id.
- SQLite foreign keys are enabled on every connection. Related inserts form one transaction. Initialization checks all five tables inside a write lock; it seeds only an empty database.
- SQLite is the source of truth. After SQL commits, Chroma is updated. These are separate databases, so there is no shared atomic transaction. If indexing fails, the interface says the record is saved but pending; **do not save it again**. Rebuild the index. Search warns about missing indexed records.
- Rebuilding upserts all SQL memories and removes stale vector IDs. Stop the app before maintenance; this is a single-user lab project.

```powershell
# Safe to repeat; also repairs failed indexing:
.\.venv\Scripts\python.exe init_db.py --rebuild-index

# SQLite setup only, useful when the model download is unavailable:
.\.venv\Scripts\python.exe init_db.py --sql-only

# DESTRUCTIVE: deletes added records and restores exactly eight seed memories:
.\.venv\Scripts\python.exe init_db.py --reset --yes
```

## Testing

```powershell
.\.venv\Scripts\python.exe tests/smoke_check.py
# Relational checks without Chroma/model:
.\.venv\Scripts\python.exe tests/smoke_check.py --sql-only
.\.venv\Scripts\python.exe tests/ui_check.py
```

Tests use disposable databases and do not change your saved demonstration data. Full smoke tests cover eight vectors, linked metadata/documents, semantic retrieval, idempotent indexing, index repair and a ninth saved memory. A similarity test checks relevance without requiring an exact top-ranked result.

Tests reuse the model already downloaded into `data/model_cache/`; their SQLite and Chroma files are isolated in a temporary directory. Windows may retain temporary Chroma files until its native handles close; this does not affect the saved demonstration data.

**Verification in this build environment:** SQLite and UI tests passed. The full smoke suite was attempted and errored in its vector checks because dependencies were missing. ChromaDB and Sentence Transformers could not be installed because package downloads were blocked by network socket restrictions. See `docs/TEST_RESULTS.md` and `docs/full_smoke_output.txt`. Do not interpret SQL-only success as proof of semantic-search success.

## Troubleshooting

The project config `.streamlit/config.toml` disables source-file watching because inspecting Transformers' lazy modules can trigger repeated missing-`torchvision` tracebacks. The text embedding model does not need torchvision. Restart Streamlit after source edits; normal UI interactions still rerun. Start from this project directory so its configuration is loaded.

| Problem | What to do |
| --- | --- |
| `python` is not recognized | Install Python 3.11+ with PATH enabled, reopen PowerShell, and retry. |
| Missing module or outdated Tornado error | Use the new `.venv` and its Python executable for both installation and startup, rather than the system/Anaconda environment. |
| Model cannot download | Connect to the internet for initial setup and rerun `init_db.py`. Keep the downloaded `data/model_cache/` folder afterward. |
| SQL saved, but indexing failed | Do not click Save again. Stop the app, fix dependency/model setup, run `init_db.py --rebuild-index`, then restart. |
| No indexed memories or pending memories | Run `init_db.py --rebuild-index`. This is safe to repeat. |
| Ticker already exists | Select the existing company instead of creating another company with the same ticker. |
| Report values differ from the baseline | Added records change aggregates. Inspect saved memories or explicitly reset if you want to discard additions. |
| Port 8501 is already used | Stop the other Streamlit process or append `--server.port 8502` to the startup command and open port 8502. |
| Need to work offline | Install packages and download the model first. SQL-only mode cannot demonstrate vector search. |

The reset and rebuild commands are in Data and recovery above. Use a second terminal or stop the app with Ctrl+C before running maintenance.

## Files

- `app.py`: three Streamlit pages.
- `database.py`: SQLite validation, transactions, joins and reports.
- `vector_store.py`: MiniLM embeddings, Chroma upserts and cosine search.
- `init_db.py`: initialization, repair and reset.
- `sql/`: original schema, fictional data and report queries.
- `diagrams/`: all original PNGs preserved. The latest handwritten reference is preferred visually; SQL names/values remain authoritative.
- `docs/06_project_deliverables.pdf`: preserved original draft.
- `PROJECT_REPORT.pdf`: generated academic report.
- `VIVA_PREPARATION.md`: short viva answers.

## Search interpretation and limitations

The collection explicitly uses cosine distance. **Similarity = 1 - distance** (normally -1 to 1; small floating-point deviations are possible). A larger score means closer text meaning, not investment confidence, profit probability or causal proof. MiniLM truncates long input; keep explanations concise. Embeddings are not transformer attention weights. Stored explanations are supplied text, not verified internal AI reasoning.

SQLite and Chroma integration follows the official [Chroma collection documentation](https://cookbook.chromadb.dev/core/collections/); embedding generation follows [Sentence Transformers documentation](https://www.sbert.net/docs/package_reference/sentence_transformer/SentenceTransformer.html).

## Report

Student details: S Anuj Srijan - PES1UG24AM234; Aswin Adhitya - PES1UG24AM213 (confirmed by the user). To rebuild the report after adding real screenshots to `docs/screenshots/`:

```powershell
.\.venv\Scripts\python.exe -m pip install reportlab
.\.venv\Scripts\python.exe docs/build_report.py
```

ReportLab is needed only for report generation, not to run the application.

For the example query **Companies benefiting from increased AI infrastructure spending**, the supplied AI-chip/data-center memories should retrieve a relevant NVIDIA or AMD investment. Companies are not hardcoded into search: Chroma ranks stored news and reasoning by semantic similarity, and SQLite supplies the linked company and return. The full smoke test checks for at least one NVIDIA/AMD match without prescribing its rank. This acceptance check remains unverified until the embedding dependencies are installed.
