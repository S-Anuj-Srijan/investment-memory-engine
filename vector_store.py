"""One local Chroma collection, one MiniLM vector per reasoning row."""
from functools import lru_cache
import database

@lru_cache(maxsize=1)
def model():
    try:
        from sentence_transformers import SentenceTransformer
        name = "sentence-transformers/all-MiniLM-L6-v2"
        # Tests isolate database files but reuse the downloaded model for offline runs.
        cache = str(database.ROOT / "data" / "model_cache")
        try:
            return SentenceTransformer(name, cache_folder=cache, local_files_only=True)
        except OSError:
            return SentenceTransformer(name, cache_folder=cache)
    except Exception as exc:
        raise RuntimeError("Embedding model unavailable. Install requirements, then run "
                           "python init_db.py with internet once to download all-MiniLM-L6-v2. "
                           "Keep data/model_cache for offline use. No substitute vectors are used.") from exc

@lru_cache(maxsize=1)
def collection():
    try:
        import chromadb
        client = chromadb.PersistentClient(path=str(database.DATA / "chroma"))
        return client.get_or_create_collection("investment_memories", embedding_function=None,
                    configuration={"hnsw": {"space": "cosine"}})
    except Exception as exc:
        raise RuntimeError("ChromaDB unavailable. Install requirements and run python init_db.py --rebuild-index.") from exc

def document(row):
    return "\n".join((row["headline"], row["news_text"], row["reasoning_text"]))

def index_memories(records):
    if not records:
        return
    documents = [document(r) for r in records]
    embeddings = model().encode(documents, normalize_embeddings=True).tolist()
    collection().upsert(ids=[r["vector_memory_id"] for r in records], documents=documents,
                        embeddings=embeddings,
                        metadatas=[{"reasoning_id": int(r["reasoning_id"])} for r in records])

def rebuild_index():
    records = database.memories()
    index_memories(records)
    expected = {r["vector_memory_id"] for r in records}
    stale = set(collection().get()["ids"]) - expected
    if stale:
        collection().delete(ids=list(stale))
    return len(records)

def pending_count():
    expected = {r["vector_memory_id"] for r in database.memories()}
    return len(expected - set(collection().get()["ids"]))

def search(query):
    if not query.strip():
        raise ValueError("Enter a search idea.")
    col = collection()
    if col.count() == 0:
        raise RuntimeError("No indexed memories. Run python init_db.py --rebuild-index.")
    vector = model().encode([query.strip()], normalize_embeddings=True).tolist()
    results = col.query(query_embeddings=vector, n_results=min(3, col.count()),
                        include=["metadatas", "distances"])
    matches = []
    for metadata, distance, vector_id in zip(results["metadatas"][0], results["distances"][0], results["ids"][0]):
        row = database.memory(int(metadata["reasoning_id"]))
        if row and row["vector_memory_id"] == vector_id:
            row.update(distance=float(distance), similarity=1.0-float(distance))
            matches.append(row)
    return matches
