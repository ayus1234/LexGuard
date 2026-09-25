"""
One-time migration script: ChromaDB -> PostgreSQL + pgvector.

Reads existing ChromaDB collections, extracts chunks, embeddings, and metadata,
and transactionally inserts them into PostgreSQL with pgvector.
"""

import sys
from pathlib import Path

# Ensure backend root is on sys.path
backend_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_root))

try:
    from backend.app.core.config import settings
    from backend.app.core.logging import logger
    from backend.app.schemas.retrieval import DocumentChunk, ChunkMetadata
    from backend.app.services.pgvector_store import PgVectorStore
except ImportError:
    from app.core.config import settings
    from app.core.logging import logger
    from app.schemas.retrieval import DocumentChunk, ChunkMetadata
    from app.services.pgvector_store import PgVectorStore


def migrate(chroma_dir: str = "./chroma_db", dry_run: bool = False):
    print("=" * 60)
    print("LEXGUARD CHROMADB -> POSTGRESQL + PGVECTOR MIGRATION")
    print("=" * 60)

    chroma_path = Path(chroma_dir)
    if not chroma_path.exists():
        print(f"ChromaDB directory not found at: {chroma_dir}")
        print("Nothing to migrate. Existing data is development-only.")
        return

    try:
        import chromadb
    except ImportError:
        print("ChromaDB is not installed. Skipping ChromaDB extraction.")
        return

    print(f"Connecting to ChromaDB at: {chroma_dir}...")
    client = chromadb.PersistentClient(path=str(chroma_path))
    collections = client.list_collections()

    if not collections:
        print("No ChromaDB collections found.")
        return

    pg_store = PgVectorStore()
    total_migrated = 0

    for col in collections:
        count = col.count()
        print(f"\nProcessing collection: '{col.name}' ({count} records)...")
        if count == 0:
            print("Collection is empty. Skipping.")
            continue

        data = col.get(include=["documents", "metadatas", "embeddings"])
        ids = data.get("ids", [])
        texts = data.get("documents", [])
        metadatas = data.get("metadatas", [])
        embeddings = data.get("embeddings", [])

        if not ids:
            print("No records retrieved from collection.")
            continue

        # Group by document_id
        doc_chunks_map = {}
        for i, chunk_id in enumerate(ids):
            meta = metadatas[i] if metadatas and i < len(metadatas) else {}
            doc_id = meta.get("document_id", "default_doc")
            text = texts[i] if texts and i < len(texts) else ""
            emb = embeddings[i] if embeddings and i < len(embeddings) else []

            chunk_meta = ChunkMetadata(
                document_id=doc_id,
                chunk_id=chunk_id,
                section=meta.get("section") or None,
                page_start=int(meta.get("page_start", 1)),
                page_end=int(meta.get("page_end", 1)),
                character_start=int(meta.get("character_start", 0)),
                character_end=int(meta.get("character_end", 0)),
            )

            chunk = DocumentChunk(
                chunk_id=chunk_id,
                document_id=doc_id,
                chunk_index=int(meta.get("chunk_index", 0)),
                text=text,
                section=meta.get("section") or None,
                page_start=int(meta.get("page_start", 1)),
                page_end=int(meta.get("page_end", 1)),
                character_start=int(meta.get("character_start", 0)),
                character_end=int(meta.get("character_end", 0)),
                token_estimate=int(meta.get("token_estimate", len(text) // 4)),
                metadata=chunk_meta,
            )

            if doc_id not in doc_chunks_map:
                doc_chunks_map[doc_id] = {"chunks": [], "embeddings": []}

            doc_chunks_map[doc_id]["chunks"].append(chunk)
            doc_chunks_map[doc_id]["embeddings"].append(emb)

        for doc_id, payload in doc_chunks_map.items():
            chunks = payload["chunks"]
            embs = payload["embeddings"]
            print(f"  -> Document '{doc_id}': {len(chunks)} chunks, embedding dims: {len(embs[0]) if embs and embs[0] else 0}")
            if not dry_run:
                pg_store.add_chunks(doc_id, chunks, embs)
                print(f"     Successfully migrated document '{doc_id}' into PostgreSQL.")
            total_migrated += len(chunks)

    print("\n" + "=" * 60)
    print(f"MIGRATION COMPLETE: {total_migrated} total chunks processed (dry_run={dry_run}).")
    print("=" * 60)


if __name__ == "__main__":
    is_dry = "--dry-run" in sys.argv
    path_arg = "./chroma_db"
    for arg in sys.argv[1:]:
        if not arg.startswith("--"):
            path_arg = arg
    migrate(chroma_dir=path_arg, dry_run=is_dry)
