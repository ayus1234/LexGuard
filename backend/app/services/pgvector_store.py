"""
PostgreSQL + pgvector implementation of the BaseVectorStore interface.
Provides document-scoped vector storage and cosine distance similarity search
using SQLAlchemy and pgvector.
"""

from typing import List, Tuple, Optional, Dict, Any, TYPE_CHECKING
from sqlalchemy import create_engine, select, delete, func, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects import postgresql

if TYPE_CHECKING:
    from app.core.config import settings
    from app.core.logging import logger
    from app.schemas.retrieval import DocumentChunk, ChunkMetadata
    from app.models.document import DocumentModel, DocumentChunkModel
    from app.services.base_vector_store import BaseVectorStore
    from app.utils.file_validation import VectorStoreException
else:
    try:
        from backend.app.core.config import settings
        from backend.app.core.logging import logger
        from backend.app.schemas.retrieval import DocumentChunk, ChunkMetadata
        from backend.app.models.document import DocumentModel, DocumentChunkModel
        from backend.app.services.base_vector_store import BaseVectorStore
        from backend.app.utils.file_validation import VectorStoreException
    except ImportError:
        from app.core.config import settings
        from app.core.logging import logger
        from app.schemas.retrieval import DocumentChunk, ChunkMetadata
        from app.models.document import DocumentModel, DocumentChunkModel
        from app.services.base_vector_store import BaseVectorStore
        from app.utils.file_validation import VectorStoreException


class PgVectorStore(BaseVectorStore):
    """
    Authoritative production vector store utilizing PostgreSQL with pgvector.
    Enforces document-scoped tenant isolation via SQL WHERE filtering,
    atomic transactional reindexing, and exact cosine similarity score mapping.
    """

    def __init__(self, db_url: Optional[str] = None, session_factory: Optional[Any] = None):
        self._db_url = db_url or settings.DATABASE_URL
        # Ensure psycopg driver prefix is present
        if self._db_url.startswith("postgresql://"):
            self._db_url = self._db_url.replace("postgresql://", "postgresql+psycopg://", 1)

        self._engine = None
        self._session_factory = session_factory

    def _get_session_factory(self) -> Any:
        if self._session_factory is None:
            try:
                self._engine = create_engine(
                    self._db_url,
                    pool_size=settings.DATABASE_POOL_SIZE,
                    max_overflow=settings.DATABASE_MAX_OVERFLOW,
                    pool_timeout=settings.DATABASE_POOL_TIMEOUT,
                    pool_pre_ping=True,
                )
                self._session_factory = sessionmaker(
                    bind=self._engine,
                    autoflush=False,
                    autocommit=False,
                    expire_on_commit=False,
                )
            except Exception as e:
                logger.error(f"Failed to initialize PostgreSQL vector store engine: {type(e).__name__}")
                raise VectorStoreException(f"Failed to initialize vector database engine: {str(e)}")
        return self._session_factory

    def add_chunks(
        self, document_id: str, chunks: List[DocumentChunk], embeddings: List[List[float]]
    ) -> None:
        if not chunks:
            return

        if len(chunks) != len(embeddings):
            raise VectorStoreException(
                f"Mismatch between chunks count ({len(chunks)}) and embeddings count ({len(embeddings)})"
            )

        factory = self._get_session_factory()
        session = factory()

        try:
            # 1. Idempotency: delete previous chunks for this document_id within transaction
            session.execute(
                delete(DocumentChunkModel).where(DocumentChunkModel.document_id == document_id)
            )

            # 2. Ensure parent Document record exists
            doc_stmt = select(DocumentModel).where(DocumentModel.document_id == document_id)
            doc_row = session.execute(doc_stmt).scalar_one_or_none()
            if not doc_row:
                # Create stub document record if not pre-inserted
                first_chunk = chunks[0]
                doc_row = DocumentModel(
                    document_id=document_id,
                    filename=getattr(first_chunk, "filename", f"{document_id}.txt"),
                    document_type="txt",
                    source_type="upload",
                    mime_type="text/plain",
                    word_count=sum(c.token_estimate for c in chunks),
                    character_count=sum(len(c.text) for c in chunks),
                    page_count=max(c.page_end for c in chunks),
                    content_hash=f"hash_{document_id}",
                    processing_status="indexed",
                )
                session.add(doc_row)
                session.flush()
            else:
                doc_row.processing_status = "indexed"

            # 3. Insert chunks with embeddings
            chunk_models = []
            target_dim = settings.EMBEDDING_DIMENSION
            for c, emb in zip(chunks, embeddings):
                if len(emb) < target_dim:
                    emb = emb + [0.0] * (target_dim - len(emb))
                elif len(emb) > target_dim:
                    emb = emb[:target_dim]

                meta_dict = {
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
                model = DocumentChunkModel(
                    document_id=document_id,
                    chunk_id=c.chunk_id,
                    content=c.text,
                    embedding=emb,
                    page_start=c.page_start,
                    page_end=c.page_end,
                    char_start=c.character_start,
                    char_end=c.character_end,
                    section=c.section,
                    heading=c.section,
                    chunk_index=c.chunk_index,
                    token_estimate=c.token_estimate,
                    chunk_metadata=meta_dict,
                )
                chunk_models.append(model)

            session.add_all(chunk_models)
            session.commit()
            logger.info(f"Indexed {len(chunks)} chunks in PostgreSQL pgvector for document id={document_id}")

        except Exception as e:
            session.rollback()
            logger.error(f"Failed to persist chunks into pgvector: {type(e).__name__}")
            raise VectorStoreException(f"Error persisting document vectors in PostgreSQL: {str(e)}")
        finally:
            session.close()

    def search(
        self, document_id: str, query_embedding: List[float], top_k: int = 5
    ) -> List[Tuple[DocumentChunk, float]]:
        factory = self._get_session_factory()
        session = factory()

        target_dim = settings.EMBEDDING_DIMENSION
        if len(query_embedding) < target_dim:
            query_embedding = query_embedding + [0.0] * (target_dim - len(query_embedding))
        elif len(query_embedding) > target_dim:
            query_embedding = query_embedding[:target_dim]

        try:
            # Cosine distance operator <=> in pgvector
            dist_expr = DocumentChunkModel.embedding.cosine_distance(query_embedding)

            # Query scoped strictly to document_id
            stmt = (
                select(DocumentChunkModel, dist_expr.label("distance"))
                .where(DocumentChunkModel.document_id == document_id)
                .order_by(dist_expr)
                .limit(top_k)
            )

            rows = session.execute(stmt).all()

            matched_chunks: List[Tuple[DocumentChunk, float]] = []
            for row in rows:
                chunk_model: DocumentChunkModel = row[0]
                distance: float = float(row[1]) if row[1] is not None else 1.0

                # Cosine distance in [0, 2]; similarity score in [0.0, 1.0]
                similarity = max(0.0, min(1.0, 1.0 - distance))

                meta = ChunkMetadata(
                    document_id=chunk_model.document_id,
                    chunk_id=chunk_model.chunk_id,
                    section=chunk_model.section,
                    page_start=chunk_model.page_start,
                    page_end=chunk_model.page_end,
                    character_start=chunk_model.char_start,
                    character_end=chunk_model.char_end,
                )

                chunk = DocumentChunk(
                    chunk_id=chunk_model.chunk_id,
                    document_id=chunk_model.document_id,
                    chunk_index=chunk_model.chunk_index,
                    text=chunk_model.content,
                    section=chunk_model.section,
                    page_start=chunk_model.page_start,
                    page_end=chunk_model.page_end,
                    character_start=chunk_model.char_start,
                    character_end=chunk_model.char_end,
                    token_estimate=chunk_model.token_estimate,
                    metadata=meta,
                )
                matched_chunks.append((chunk, similarity))

            # Sort descending by similarity score
            matched_chunks.sort(key=lambda x: x[1], reverse=True)
            return matched_chunks

        except Exception as e:
            logger.error(f"PostgreSQL pgvector search query failed: {type(e).__name__}")
            raise VectorStoreException(f"Vector search failed: {str(e)}")
        finally:
            session.close()

    def delete_document(self, document_id: str) -> bool:
        factory = self._get_session_factory()
        session = factory()
        try:
            session.execute(
                delete(DocumentChunkModel).where(DocumentChunkModel.document_id == document_id)
            )
            # Mark document status as deleted
            doc_stmt = select(DocumentModel).where(DocumentModel.document_id == document_id)
            doc_row = session.execute(doc_stmt).scalar_one_or_none()
            if doc_row:
                doc_row.processing_status = "deleted"

            session.commit()
            logger.info(f"Deleted pgvector entries for document id={document_id}")
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to delete document vectors from PostgreSQL: {type(e).__name__}")
            return False
        finally:
            session.close()

    def is_indexed(self, document_id: str) -> bool:
        factory = self._get_session_factory()
        session = factory()
        try:
            count_stmt = (
                select(func.count(DocumentChunkModel.id))
                .where(DocumentChunkModel.document_id == document_id)
            )
            count = session.execute(count_stmt).scalar() or 0
            return count > 0
        except Exception as e:
            logger.error(f"Failed to check document indexing status in PostgreSQL: {type(e).__name__}")
            return False
        finally:
            session.close()

    def health_check(self) -> bool:
        try:
            factory = self._get_session_factory()
            with factory() as session:
                session.execute(text("SELECT 1"))
                ext_check = session.execute(
                    text("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
                ).scalar()
                return ext_check is not None
        except Exception:
            return False


pgvector_store = PgVectorStore()

