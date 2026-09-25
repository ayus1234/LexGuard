from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Dict, Any, cast, TYPE_CHECKING
from pathlib import Path

if TYPE_CHECKING:
    from app.core.config import settings
    from app.core.logging import logger
    from app.schemas.retrieval import DocumentChunk, ChunkMetadata
    from app.services.base_vector_store import BaseVectorStore
    from app.utils.file_validation import VectorStoreException
else:
    try:
        from backend.app.core.config import settings
        from backend.app.core.logging import logger
        from backend.app.schemas.retrieval import DocumentChunk, ChunkMetadata
        from backend.app.services.base_vector_store import BaseVectorStore
        from backend.app.utils.file_validation import VectorStoreException
    except ImportError:
        from app.core.config import settings
        from app.core.logging import logger
        from app.schemas.retrieval import DocumentChunk, ChunkMetadata
        from app.services.base_vector_store import BaseVectorStore
        from app.utils.file_validation import VectorStoreException


def _to_int(val: Any, default: int = 0) -> int:
    try:
        return int(val)
    except (ValueError, TypeError):
        return default


class ChromaVectorStore(BaseVectorStore):
    """
    Persistent ChromaDB vector store implementation.
    Enforces document-scoped similarity search and clean primitive metadata mapping.
    """

    COLLECTION_NAME = "lexguard_documents"

    def __init__(self, persist_directory: Optional[str] = None):
        self._persist_dir = persist_directory or str(settings.chroma_persist_dir)
        self._client = None
        self._collection = None

    def _get_collection(self):
        if self._collection is None:
            try:
                import chromadb
                self._client = chromadb.PersistentClient(path=self._persist_dir)
                # Use cosine distance space
                self._collection = self._client.get_or_create_collection(
                    name=self.COLLECTION_NAME,
                    metadata={"hnsw:space": "cosine"},
                )
            except Exception as e:
                logger.error(f"Failed to initialize ChromaDB collection: {str(e)}")
                raise VectorStoreException(f"Failed to initialize vector database: {str(e)}")
        return self._collection

    def add_chunks(
        self, document_id: str, chunks: List[DocumentChunk], embeddings: List[List[float]]
    ) -> None:
        if not chunks:
            return

        collection = self._get_collection()

        # Idempotency: remove existing vectors for this document before re-indexing
        self.delete_document(document_id)

        ids = [c.chunk_id for c in chunks]
        texts = [c.text for c in chunks]
        metadatas = [
            {
                "document_id": document_id,
                "chunk_id": c.chunk_id,
                "chunk_index": c.chunk_index,
                "section": c.section or "",
                "page_start": c.page_start,
                "page_end": c.page_end,
                "character_start": c.character_start,
                "character_end": c.character_end,
                "token_estimate": c.token_estimate,
            }
            for c in chunks
        ]

        try:
            collection.add(
                ids=ids,
                embeddings=cast(Any, embeddings),
                documents=texts,
                metadatas=cast(Any, metadatas),
            )
            logger.info(f"Indexed {len(chunks)} chunks in vector store for document id={document_id}")
        except Exception as e:
            logger.error(f"Failed to store vectors in ChromaDB: {str(e)}")
            raise VectorStoreException(f"Error persisting document vectors: {str(e)}")

    def search(
        self, document_id: str, query_embedding: List[float], top_k: int = 5
    ) -> List[Tuple[DocumentChunk, float]]:
        collection = self._get_collection()

        try:
            # Query scoped strictly to document_id to prevent cross-tenant/cross-doc leakage
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where={"document_id": document_id},
                include=["documents", "metadatas", "distances"],
            )
        except Exception as e:
            logger.error(f"ChromaDB search query failed: {str(e)}")
            raise VectorStoreException(f"Vector search failed: {str(e)}")

        matched_chunks: List[Tuple[DocumentChunk, float]] = []

        ids_raw = results.get("ids") or [[]]
        docs_raw = results.get("documents") or [[]]
        metas_raw = results.get("metadatas") or [[]]
        dists_raw = results.get("distances") or [[]]

        ids_list = ids_raw[0] if ids_raw else []
        docs_list = docs_raw[0] if docs_raw else []
        metas_list = metas_raw[0] if metas_raw else []
        dists_list = dists_raw[0] if dists_raw else []

        for i in range(len(ids_list)):
            meta = metas_list[i] if i < len(metas_list) and isinstance(metas_list[i], dict) else {}
            dist = dists_list[i] if dists_list and i < len(dists_list) else 1.0
            # For cosine distance, similarity is 1.0 - distance
            similarity = max(0.0, min(1.0, 1.0 - float(dist)))

            section_raw = meta.get("section")
            section_val = str(section_raw) if section_raw else None
            doc_id_val = str(meta.get("document_id") or document_id)
            chunk_id_val = str(meta.get("chunk_id") or ids_list[i])
            text_val = str(docs_list[i]) if i < len(docs_list) else ""

            chunk_meta = ChunkMetadata(
                document_id=doc_id_val,
                chunk_id=chunk_id_val,
                section=section_val,
                page_start=_to_int(meta.get("page_start"), 1),
                page_end=_to_int(meta.get("page_end"), 1),
                character_start=_to_int(meta.get("character_start"), 0),
                character_end=_to_int(meta.get("character_end"), 0),
            )

            chunk = DocumentChunk(
                chunk_id=chunk_id_val,
                document_id=doc_id_val,
                chunk_index=_to_int(meta.get("chunk_index"), 0),
                text=text_val,
                section=section_val,
                page_start=_to_int(meta.get("page_start"), 1),
                page_end=_to_int(meta.get("page_end"), 1),
                character_start=_to_int(meta.get("character_start"), 0),
                character_end=_to_int(meta.get("character_end"), 0),
                token_estimate=_to_int(meta.get("token_estimate"), len(text_val) // 4),
                metadata=chunk_meta,
            )
            matched_chunks.append((chunk, similarity))

        # Sort by similarity score descending
        matched_chunks.sort(key=lambda x: x[1], reverse=True)
        return matched_chunks

    def delete_document(self, document_id: str) -> bool:
        collection = self._get_collection()
        try:
            collection.delete(where={"document_id": document_id})
            logger.info(f"Deleted vector entries for document id={document_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete document vectors from ChromaDB: {str(e)}")
            return False

    def is_indexed(self, document_id: str) -> bool:
        collection = self._get_collection()
        try:
            records = collection.get(where={"document_id": document_id}, limit=1)
            return len(records.get("ids", [])) > 0
        except Exception as e:
            logger.error(f"Failed to check document indexing status in ChromaDB: {str(e)}")
            return False

    def health_check(self) -> bool:
        try:
            self._get_collection()
            return True
        except Exception:
            return False


try:
    from backend.app.services.pgvector_store import PgVectorStore
except ImportError:
    from app.services.pgvector_store import PgVectorStore

vector_store: BaseVectorStore = PgVectorStore()
