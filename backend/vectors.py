"""Chroma is derived data; PostgreSQL remains authoritative."""
import hashlib
import os
from functools import lru_cache
from pathlib import Path
from threading import RLock
from . import db

LOCK = RLock()
MODEL_NAME = 'sentence-transformers/all-MiniLM-L6-v2'


@lru_cache(maxsize=1)
def model():
    from sentence_transformers import SentenceTransformer
    cache = str(db.ROOT / 'data/model_cache')
    try:
        return SentenceTransformer(MODEL_NAME, cache_folder=cache, local_files_only=True)
    except OSError:
        return SentenceTransformer(MODEL_NAME, cache_folder=cache)


@lru_cache(maxsize=1)
def collection():
    import chromadb
    client = chromadb.PersistentClient(path=str(Path(os.environ.get('CHROMA_PATH', db.ROOT / 'data/chroma_v2'))))
    return client.get_or_create_collection('investment_memories_v2', embedding_function=None,
                                         configuration={'hnsw': {'space': 'cosine'}})


def document(row):
    return '\n'.join((row['headline'], row['news_text'], row['reasoning_text']))


def fingerprint(row):
    return hashlib.sha256(document(row).encode()).hexdigest()


def rebuild():
    # Serialize local searches/rebuilds. Run one API worker for the local Chroma store.
    with LOCK:
        records = db.rows('SELECT * FROM memory_details ORDER BY reasoning_id')
        col = collection()
        if records:
            docs = [document(r) for r in records]
            col.upsert(ids=[r['vector_memory_id'] for r in records], documents=docs,
                       embeddings=model().encode(docs, normalize_embeddings=True).tolist(),
                       metadatas=[{'reasoning_id': r['reasoning_id'], 'fingerprint': fingerprint(r),
                                   'model': MODEL_NAME} for r in records])
        stale = set(col.get()['ids']) - {r['vector_memory_id'] for r in records}
        if stale:
            col.delete(ids=list(stale))
        return len(records)


def status():
    with LOCK:
        records = db.rows('SELECT * FROM memory_details')
        indexed = collection().get(include=['metadatas'])
        actual = dict(zip(indexed['ids'], indexed['metadatas']))
        pending = sum(actual.get(r['vector_memory_id'], {}).get('fingerprint') != fingerprint(r) for r in records)
        stale = len(set(actual) - {r['vector_memory_id'] for r in records})
        return {'pending': pending, 'stale': stale, 'indexed': len(actual)}


def search(query, sector=None, decision=None, limit=5):
    with LOCK:
        records = db.rows('SELECT * FROM memory_details WHERE (%s::text IS NULL OR sector=%s) AND (%s::text IS NULL OR decision=%s)',
                          (sector, sector, decision, decision))
        current = {r['vector_memory_id']: r for r in records}
        col = collection()
        if not current or not col.count():
            return []
        # Small academic dataset: fetch all nearest neighbours, then validate source
        # fingerprints and apply authoritative SQL filters before selecting top k.
        result = col.query(query_embeddings=model().encode([query], normalize_embeddings=True).tolist(),
                           n_results=col.count(), include=['metadatas', 'distances'])
        matches = []
        for key, meta, distance in zip(result['ids'][0], result['metadatas'][0], result['distances'][0]):
            row = current.get(key)
            if row and meta.get('fingerprint') == fingerprint(row):
                matches.append({**row, 'similarity': 1-float(distance), 'distance': float(distance)})
        return matches[:limit]
