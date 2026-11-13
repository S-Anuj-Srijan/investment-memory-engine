-- Safe DDL demonstration: temporary objects only, discarded at transaction end.
BEGIN;
CREATE TEMP TABLE ddl_lab (id INTEGER PRIMARY KEY, note TEXT NOT NULL);
ALTER TABLE ddl_lab ADD COLUMN created_at TIMESTAMPTZ DEFAULT now();
INSERT INTO ddl_lab VALUES (1, 'DDL demonstration', now());
UPDATE ddl_lab SET note='Updated demonstration' WHERE id=1;
SELECT * FROM ddl_lab;
DELETE FROM ddl_lab WHERE id=1;
DROP TABLE ddl_lab;
ROLLBACK;

-- HAVING, aggregation, JOIN and ORDER BY: sectors with multiple investments.
SELECT c.sector, COUNT(*) AS investment_count, ROUND(AVG(i.return_percentage),2) AS average_return
FROM investments i JOIN companies c USING(company_id)
GROUP BY c.sector HAVING COUNT(*) >= 2 ORDER BY average_return DESC;

-- Scalar subquery: decisions that beat the overall observed average.
SELECT company_name, decision, return_percentage FROM memory_details
WHERE return_percentage > (SELECT AVG(return_percentage) FROM investments)
ORDER BY return_percentage DESC;

-- Index access can be inspected on larger data; tiny seed tables may use a scan.
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM investments WHERE company_id=1;
SELECT * FROM company_performance;
SELECT * FROM audit_log ORDER BY audit_id DESC LIMIT 20;
