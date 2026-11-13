-- SQLite schema for Investment Memory Engine
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS companies (
 company_id INTEGER PRIMARY KEY,
 company_name TEXT NOT NULL,
 ticker TEXT NOT NULL UNIQUE,
 sector TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS models (
 model_id INTEGER PRIMARY KEY,
 model_name TEXT NOT NULL,
 version TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS news (
 news_id INTEGER PRIMARY KEY,
 headline TEXT NOT NULL,
 news_text TEXT NOT NULL,
 published_at TEXT NOT NULL,
 source TEXT NOT NULL DEFAULT 'Demo / simulated'
);
CREATE TABLE IF NOT EXISTS investments (
 investment_id INTEGER PRIMARY KEY,
 company_id INTEGER NOT NULL,
 model_id INTEGER NOT NULL,
 investment_amount REAL NOT NULL CHECK(investment_amount > 0),
 decision TEXT NOT NULL CHECK(decision IN ('BUY','SELL','HOLD')),
 trade_date TEXT NOT NULL,
 return_percentage REAL,
 FOREIGN KEY(company_id) REFERENCES companies(company_id),
 FOREIGN KEY(model_id) REFERENCES models(model_id)
);
CREATE TABLE IF NOT EXISTS investment_reasoning (
 reasoning_id INTEGER PRIMARY KEY,
 investment_id INTEGER NOT NULL,
 news_id INTEGER NOT NULL,
 reasoning_text TEXT NOT NULL,
 confidence REAL CHECK(confidence IS NULL OR confidence BETWEEN 0 AND 1),
 vector_memory_id TEXT UNIQUE,
 FOREIGN KEY(investment_id) REFERENCES investments(investment_id),
 FOREIGN KEY(news_id) REFERENCES news(news_id)
);
CREATE INDEX IF NOT EXISTS idx_investments_company ON investments(company_id);
CREATE INDEX IF NOT EXISTS idx_reasoning_investment ON investment_reasoning(investment_id);
