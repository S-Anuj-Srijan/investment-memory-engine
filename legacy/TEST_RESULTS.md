# Verification results - 26 October 2026

## Passed

- SQLite initialized at data/investments.db with exactly five supplied tables and eight fictional memories.
- SQL-only smoke suite: four tests passed; one vector test explicitly skipped.
- Foreign-key rejection and PRAGMA foreign_key_check.
- Exact seeded report averages, sector counts and top-five ranking.
- Repeated initialization preserves counts.
- Input validation, invalid-reference transaction rollback and saving a ninth memory in a disposable database.
- Streamlit AppTest: all three pages, eight-row display, three report tables, blank search and invalid save.
- Running browser captures saved in docs/screenshots/.
- PROJECT_REPORT.pdf generated, all 14 pages rendered and visually inspected. Original diagrams and draft PDF retained.

## Blocked / not passed

Full smoke suite was executed: three tests passed, two tests errored due to missing sentence_transformers. See full_smoke_output.txt. ChromaDB is also missing. pip installation failed with WinError 10013 (network socket access blocked). Thus embedding generation, semantic relevance, eight Chroma records and complete cross-store writes have NOT been verified.

The search screenshot shows the real setup warning, not working search results.

The system Python has an outdated Tornado package. UI preview used the compatible cached Tornado 6.5.2 package without modifying system packages. Use a fresh virtual environment and install requirements for your demonstration.

## Complete verification on your machine

Latest completion attempt: created `.venv` successfully. Installation was retried there and a direct PyPI connectivity check confirmed the same `WinError 10013` socket restriction. SQL-only tests passed in this new environment; UI checks passed using the existing system Streamlit installation. The model cache is now shared between the app and isolated tests so full tests can reuse the downloaded model offline. `setup_and_run.ps1` was added and its PowerShell syntax checked; its complete install-and-test path remains blocked by network access in this session.

Run the PowerShell setup in README.md, then:
```powershell
.\.venv\Scripts\python.exe init_db.py
.\.venv\Scripts\python.exe tests/smoke_check.py
.\.venv\Scripts\python.exe tests/ui_check.py
.\.venv\Scripts\python.exe -m streamlit run app.py
```

After the full tests pass, search "Companies benefiting from increased AI infrastructure spending", save a new fictional memory and verify it is searchable. Capture that real result before treating semantic retrieval as demonstrated.
