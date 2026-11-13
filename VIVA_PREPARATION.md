# Investment Memory Engine viva preparation

1. **What problem does the system solve?** It preserves the rationale and news behind investment decisions and retrieves related situations to support later review.
2. **Why is this more than CRUD?** It combines semantic retrieval, current-source validation, multi-table atomic writes, reporting, ownership rules, optimistic outcome updates and audited changes.
3. **Why PostgreSQL?** The course requires MySQL or PostgreSQL. PostgreSQL supplies typed values, constraints, foreign keys, views, transactions, indexes and trigger functions. SQLite remains only in the old prototype.
4. **Why Chroma?** News and reasoning are unstructured; semantically related passages need not share exact words. Its HNSW index supports cosine nearest-neighbor retrieval.
5. **What is embedded?** Headline, news text and reasoning. all-MiniLM-L6-v2 produces 384 normalized dimensions. The recorded reasoning-model label is separate from the embedding model.
6. **What does similarity mean?** One minus cosine distance. Higher means closer text meaning, not probability, correctness or expected return.
7. **Explain the ER model.** Companies and models each have many investments. Investments and news each have many reasoning links. Users create investments, own sessions and act in audit events. Chroma links by vector_memory_id, verified in application code.
8. **How is 3NF achieved?** Company, model and news facts are stored in separate relations and referenced by keys. Joined presentation is a view, not duplicated current source data.
9. **Name at least four advanced concepts.** Transactions, views, stored trigger function, audit trigger, indexing and vector similarity search.
10. **What happens if one insert fails?** Psycopg's transaction rolls back the company/news/investment/reasoning and its audit together. Tests deliberately use a nonexistent model to demonstrate this.
11. **What happens if Chroma is unavailable?** SQL remains authoritative. The memory saves successfully and is pending indexing. Admin rebuild repairs the derived store. There is no distributed ACID transaction across both stores.
12. **How do you avoid stale search hits?** Fetch the current SQL row, require the same vector ID and document fingerprint, and ignore deleted/mismatched records.
13. **How are conflicting updates handled?** Lock the row, compare the submitted revision and reject an outdated revision with HTTP 409. Increment the revision on success.
14. **How does authentication work?** Salted scrypt password hashes and random opaque HttpOnly session cookies. Only hashed session tokens are stored in SQL; sessions expire in eight hours.
15. **What are the roles?** Analysts create and search memories and update their own outcomes. Admins additionally manage users, delete, edit all outcomes, rebuild and inspect audits. API checks enforce this independently of the UI.
16. **What queries can you explain?** Average return JOIN/GROUP BY, sector counts, top-five ORDER BY/LIMIT, model averages, sectors with HAVING COUNT>=2 and returns above a scalar AVG subquery.
17. **Why can EXPLAIN choose a sequential scan?** With eight trades a scan can cost less than index traversal. An index is available; the planner chooses the access path.
18. **Why is an unknown return NULL?** Unknown is not zero. AVG ignores NULL, while COUNT(*) counts all records. Report labels distinguish known outcomes.
19. **Is the audit tamper-proof?** No. The app exposes no audit mutation route, but database owners can modify database tables. The project demonstrates accountability, not protection against a malicious DBA.
20. **What remains for submission?** Instructor approval/title uniqueness, team responsibilities, browser walkthrough and genuine Next.js screenshots. Do not claim the old Streamlit images show the new app.

Each member should demonstrate both a database feature and an application feature they actually reviewed or developed. Confirm responsibilities in docs/TEAM.md. Git/GitHub and commit history are outside this task's scope.
