"""Initialize, repair the vector index, or explicitly reset demonstration data."""
import argparse
import database
import vector_store

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rebuild-index", action="store_true", help="Rebuild from SQLite; safe to repeat")
    parser.add_argument("--sql-only", action="store_true", help="Initialize SQLite without embeddings")
    parser.add_argument("--reset", action="store_true", help="Delete ALL stored memories, then reseed")
    parser.add_argument("--yes", action="store_true", help="Confirm destructive reset")
    args = parser.parse_args()
    if args.reset and not args.yes:
        parser.error("Reset deletes added memories. Stop Streamlit, then use --reset --yes to confirm.")
    if args.reset and args.sql_only:
        parser.error("Reset also requires the vector store; omit --sql-only.")
    try:
        database.initialize()
        if args.reset:
            col = vector_store.collection()
            ids = col.get()["ids"]
            if ids:
                col.delete(ids=ids)
            with database.connect() as db:
                for table in ("investment_reasoning", "investments", "news", "models", "companies"):
                    db.execute("DELETE FROM " + table)
            database.initialize()
        print("SQLite ready:", database.DB_PATH)
        print("Memories:", len(database.memories()))
        if not args.sql_only:
            print("Indexed memories:", vector_store.rebuild_index())
    except Exception as exc:
        parser.exit(1, str(exc) + "\nSQLite is preserved. Fix setup and rerun --rebuild-index.\n")

if __name__ == "__main__":
    main()
