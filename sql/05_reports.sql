-- Report 1: average simulated return by company
SELECT c.company_name, ROUND(AVG(i.return_percentage),2) AS avg_return_pct
FROM investments i JOIN companies c ON i.company_id=c.company_id
WHERE i.return_percentage IS NOT NULL
GROUP BY c.company_id,c.company_name ORDER BY avg_return_pct DESC;

-- Report 2: investments per sector
SELECT c.sector,COUNT(*) AS total_investments
FROM investments i JOIN companies c ON i.company_id=c.company_id
GROUP BY c.sector ORDER BY total_investments DESC;

-- Report 3: top five simulated trades by return
SELECT c.company_name,i.investment_amount,i.return_percentage
FROM investments i JOIN companies c ON i.company_id=c.company_id
WHERE i.return_percentage IS NOT NULL
ORDER BY i.return_percentage DESC LIMIT 5;

-- Optional report 4: return by model
SELECT m.model_name,COUNT(*) AS investment_count,
ROUND(AVG(i.return_percentage),2) AS average_return_pct
FROM investments i JOIN models m ON i.model_id=m.model_id
WHERE i.return_percentage IS NOT NULL
GROUP BY m.model_id,m.model_name;
