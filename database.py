"""SQLite is the source of truth; the vector index can be rebuilt."""
import math
import os
import sqlite3
from contextlib import contextmanager
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = Path(os.environ.get("IME_DATA_DIR", ROOT / "data"))
DB_PATH = DATA / "investments.db"

@contextmanager
def connect():
    DATA.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_PATH, timeout=20)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    try:
        with db:
            yield db
    finally:
        db.close()

def initialize():
    with connect() as db:
        db.executescript((ROOT / "legacy/sql/03_schema.sql").read_text())
        db.execute("BEGIN IMMEDIATE")
        tables = ("companies", "models", "news", "investments", "investment_reasoning")
        # Table names are fixed internal constants, never user input.
        if not any(db.execute("SELECT 1 FROM " + t + " LIMIT 1").fetchone() for t in tables):
            for statement in (ROOT / "legacy/sql/04_demo_data.sql").read_text().split(";"):
                if statement.strip():
                    db.execute(statement)

def rows(sql, parameters=()):
    with connect() as db:
        return [dict(r) for r in db.execute(sql, parameters)]

MEMORY_SQL = """SELECT r.*, i.investment_amount, i.decision, i.trade_date,
 i.return_percentage, c.company_name, c.ticker, c.sector,
 m.model_name, m.version, n.headline, n.news_text, n.published_at, n.source
 FROM investment_reasoning r
 JOIN investments i ON r.investment_id=i.investment_id
 JOIN companies c ON i.company_id=c.company_id
 JOIN models m ON i.model_id=m.model_id
 JOIN news n ON r.news_id=n.news_id"""

def memories():
    return rows(MEMORY_SQL + " ORDER BY r.reasoning_id")

def memory(reasoning_id):
    result = rows(MEMORY_SQL + " WHERE r.reasoning_id=?", (reasoning_id,))
    return result[0] if result else None

def reports():
    queries = (ROOT / "sql/05_reports.sql").read_text().split(";")[:3]
    return [(q.strip() + ";", rows(q)) for q in queries]

def save_memory(*, company_id, company_name, ticker, sector, model_id,
                headline, news_text, reasoning_text, amount, decision,
                trade_date, published_at, confidence, return_percentage):
    headline, news_text, reasoning_text = (v.strip() for v in (headline, news_text, reasoning_text))
    if not all((headline, news_text, reasoning_text)):
        raise ValueError("Headline, news content and investment reasoning are required.")
    if not math.isfinite(amount) or amount <= 0:
        raise ValueError("Investment amount must be positive and finite.")
    if decision not in ("BUY", "SELL"):
        raise ValueError("Choose BUY or SELL.")
    if not math.isfinite(confidence) or not 0 <= confidence <= 1:
        raise ValueError("Confidence must be between 0 and 1.")
    if return_percentage is not None and not math.isfinite(return_percentage):
        raise ValueError("Return must be a finite number, or left unknown.")
    date.fromisoformat(str(trade_date))
    date.fromisoformat(str(published_at))
    with connect() as db:
        if company_id is None:
            company_name, ticker, sector = company_name.strip(), ticker.strip().upper(), sector.strip()
            if not all((company_name, ticker, sector)):
                raise ValueError("A new company needs a name, unique ticker and sector.")
            company_id = db.execute("INSERT INTO companies(company_name,ticker,sector) VALUES (?,?,?)",
                                    (company_name, ticker, sector)).lastrowid
        news_id = db.execute("INSERT INTO news(headline,news_text,published_at,source) VALUES (?,?,?,?)",
                             (headline, news_text, str(published_at), "Demo / simulated")).lastrowid
        investment_id = db.execute("""INSERT INTO investments
            (company_id,model_id,investment_amount,decision,trade_date,return_percentage)
            VALUES (?,?,?,?,?,?)""",
            (company_id, model_id, amount, decision, str(trade_date), return_percentage)).lastrowid
        reasoning_id = db.execute("""INSERT INTO investment_reasoning
            (investment_id,news_id,reasoning_text,confidence) VALUES (?,?,?,?)""",
            (investment_id, news_id, reasoning_text, confidence)).lastrowid
        db.execute("UPDATE investment_reasoning SET vector_memory_id=? WHERE reasoning_id=?",
                   ("memory_" + str(reasoning_id), reasoning_id))
    return reasoning_id
