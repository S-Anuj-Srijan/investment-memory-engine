# Demonstration and screenshot guide

## Before presenting

Confirm both student names and USNs in docs/TEAM.md, instructor approval, title uniqueness, demonstration responsibilities. Run start_project.ps1 and open http://localhost:3000. On first visit, create your administrator account in the browser setup form, then sign in. Rebuild the semantic index if needed.

## Suggested ten-minute demonstration

1. Explain the missing-context problem and why semantic memory reuse goes beyond CRUD.
2. Show the current ER diagram, keys, cardinalities, relational schema and 3NF explanation.
3. Explain PostgreSQL for integrity and Chroma for semantic similarity; identify which data is authoritative.
4. Sign in as admin. Show Overview, filter Finance/BUY, and inspect the saved reasoning.
5. Add a fictional investment to an existing company. Leave return unknown. Observe the new SQL row and pending vector count. Rebuild the index in Administration.
6. Search for "Companies benefiting from increased AI infrastructure spending". Explain MiniLM, 384 dimensions, cosine distance and why similarity is not a prediction.
7. Update the outcome. Load the audit history and show INSERT/UPDATE with actor and old/new values. Use disposable demo records to demonstrate confirmed deletion and DELETE audit history.
8. Show six SQL reports, including the HAVING and above-average subquery examples. Run sql/06_advanced_demo.sql using PostgreSQL to demonstrate temporary CREATE/ALTER/DROP and EXPLAIN.
9. Sign in as analyst and demonstrate that admin controls are absent and seeded memories cannot be edited. Create an analyst-owned memory and update its outcome. The API tests also prove server-side restrictions.
10. Run scripts/run_tests.py --vectors. Each member explains their actual database and application contributions.

## Required genuine screenshots

Capture these from the running Next.js application, using the browser or Windows screenshot tool. Save under docs/screenshots/ with these names and avoid password fields, session values, database URLs and browser personal tabs:

- nextjs_01_login.png: sign-in page with empty password field.
- nextjs_02_overview.png: eight seeded decisions, dashboard totals and filters.
- nextjs_03_add.png: investment form with fictional values.
- nextjs_04_search.png: actual semantic results and similarity values.
- nextjs_05_reports.png: a report plus its expanded SQL.
- nextjs_06_admin.png: index status and a real audit event.
- nextjs_07_analyst.png: analyst navigation and permitted controls.

These captures are pending. Automated computer access timed out during verification; the old 01_add.png/02_reports.png/03_search_setup.png are Streamlit captures and must not substitute for the new interface. After capturing, regenerate the PDF with docs/build_level3_report.py to include nextjs_*.png automatically.

## Useful commands

```powershell
.venv/Scripts/python.exe scripts/run_tests.py --vectors
.venv/Scripts/python.exe -m backend.manage rebuild-index
.venv/Scripts/python.exe docs/build_level3_report.py
```

Use a SQL client connected with your .env configuration for schema/EXPLAIN demonstrations. Never put credentials on presentation slides. If model download is unavailable, use the cached data/model_cache; do not substitute random embeddings or claim a keyword search is semantic search.
