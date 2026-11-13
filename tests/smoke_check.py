"""Run against a disposable database; never change the user's demonstration data."""
import os
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest

# Chroma can keep native file handles open until process exit on Windows.
sandbox = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
os.environ["IME_DATA_DIR"] = sandbox.name
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import database
import vector_store

FULL = "--sql-only" not in sys.argv
if not FULL:
    sys.argv.remove("--sql-only")

def example(**changes):
    values = dict(company_id=None, company_name="Lab Test", ticker="LAB", sector="Technology",
        model_id=1, headline="AI infrastructure expands", news_text="New data centres need AI chips.",
        reasoning_text="More AI infrastructure spending may support accelerator demand.",
        amount=2500.0, decision="BUY", trade_date="2026-10-26", published_at="2026-10-25",
        confidence=0.8, return_percentage=None)
    values.update(changes)
    return values

class DatabaseTests(unittest.TestCase):
    def setUp(self):
        database.initialize()

    def test_01_schema_seed_and_reinitialize(self):
        tables = database.rows("SELECT name FROM sqlite_master WHERE type='table'")
        self.assertEqual({r["name"] for r in tables},
                         {"companies", "models", "news", "investments", "investment_reasoning"})
        self.assertEqual(len(database.memories()), 8)
        database.initialize()
        self.assertEqual(len(database.memories()), 8)
        with database.connect() as db:
            self.assertEqual(db.execute("PRAGMA foreign_keys").fetchone()[0], 1)
            self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(), [])
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute("INSERT INTO investments VALUES (99,999,1,100,'BUY','2026-10-26',NULL)")
        self.assertEqual(len(database.memories()), 8)

    def test_02_reports(self):
        results = database.reports()
        averages = {r["company_name"]:r["avg_return_pct"] for r in results[0][1]}
        self.assertEqual(averages, {"NVIDIA":6.0, "AMD":1.5, "Microsoft":3.0,
                                   "JPMorgan Chase":1.75, "Exxon Mobil":-1.5})
        self.assertEqual({r["sector"]:r["total_investments"] for r in results[1][1]},
                         {"Technology":5, "Finance":2, "Energy":1})
        self.assertEqual([r["return_percentage"] for r in results[2][1]], [8.0,5.0,4.0,3.0,2.5])

    def test_03_validation_and_transaction_rollback(self):
        for change in ({"amount":0}, {"amount":float("nan")}, {"headline":" "},
                       {"confidence":1.1}, {"decision":"INVALID"}, {"trade_date":"bad"}):
            with self.assertRaises(ValueError):
                database.save_memory(**example(**change))
        with self.assertRaises(sqlite3.IntegrityError):
            database.save_memory(**example(model_id=999))
        self.assertEqual(len(database.rows("SELECT * FROM companies")), 5)
        self.assertEqual(len(database.rows("SELECT * FROM news")), 6)

    @unittest.skipUnless(FULL, "Vector dependencies/model not requested in --sql-only mode")
    def test_04_vector_seed_search_and_repair(self):
        self.assertEqual(vector_store.rebuild_index(), 8)
        vector_store.rebuild_index()
        col = vector_store.collection()
        self.assertEqual(col.count(), 8)
        stored = col.get(include=["metadatas", "documents", "embeddings"])
        for idx, meta, doc in zip(stored["ids"], stored["metadatas"], stored["documents"]):
            row = database.memory(meta["reasoning_id"])
            self.assertEqual(row["vector_memory_id"], idx)
            self.assertEqual(doc, vector_store.document(row))
        self.assertEqual(len(stored["embeddings"][0]), 384)
        hits = vector_store.search("Companies benefiting from increased AI infrastructure spending")
        self.assertTrue(hits)
        self.assertTrue(
            any(r["ticker"] in {"NVDA", "AMD"} for r in hits),
            "The seeded AI infrastructure query should retrieve a relevant NVIDIA or AMD memory."
        )
        for row in hits:
            self.assertAlmostEqual(row["similarity"], 1-row["distance"])
        col.delete(ids=["memory_1"])
        self.assertEqual(vector_store.pending_count(), 1)
        vector_store.rebuild_index()
        self.assertEqual(vector_store.pending_count(), 0)
        with self.assertRaises(ValueError):
            vector_store.search(" ")

    def test_05_add_memory_and_preserve_on_reinitialize(self):
        rid = database.save_memory(**example())
        row = database.memory(rid)
        self.assertEqual(row["ticker"], "LAB")
        self.assertEqual(row["vector_memory_id"], "memory_9")
        self.assertIsNone(row["return_percentage"])
        database.initialize()
        self.assertEqual(len(database.memories()), 9)
        if FULL:
            vector_store.index_memories([row])
            vector_store.index_memories([row])
            self.assertEqual(vector_store.collection().count(), 9)
            stored = vector_store.collection().get(ids=["memory_9"])
            self.assertEqual(stored["metadatas"][0]["reasoning_id"], rid)

if __name__ == "__main__":
    unittest.main(verbosity=2)
