import time
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.core.config import settings
    from app.core.logging import logger
    from app.schemas.document import DocumentResponse
    from app.schemas.retrieval import (
        DocumentIndexResponse,
        RetrievalResult,
        RetrievalResultItem,
        GroundingStatus,
    )
    from app.services.chunking_service import chunking_service, ChunkingService
    from app.services.embedding_service import embedding_service, BaseEmbeddingService
    from app.services.vector_store import vector_store
    from app.services.base_vector_store import BaseVectorStore
    from app.utils.file_validation import DocumentNotIndexedException
else:
    try:
        from backend.app.core.config import settings
        from backend.app.core.logging import logger
        from backend.app.schemas.document import DocumentResponse
        from backend.app.schemas.retrieval import (
            DocumentIndexResponse,
            RetrievalResult,
            RetrievalResultItem,
            GroundingStatus,
        )
        from backend.app.services.chunking_service import chunking_service, ChunkingService
        from backend.app.services.embedding_service import embedding_service, BaseEmbeddingService
        from backend.app.services.vector_store import vector_store
        from backend.app.services.base_vector_store import BaseVectorStore
        from backend.app.utils.file_validation import DocumentNotIndexedException
    except ImportError:
        from app.core.config import settings
        from app.core.logging import logger
        from app.schemas.document import DocumentResponse
        from app.schemas.retrieval import (
            DocumentIndexResponse,
            RetrievalResult,
            RetrievalResultItem,
            GroundingStatus,
        )
        from app.services.chunking_service import chunking_service, ChunkingService
        from app.services.embedding_service import embedding_service, BaseEmbeddingService
        from app.services.vector_store import vector_store
        from app.services.base_vector_store import BaseVectorStore
        from app.utils.file_validation import DocumentNotIndexedException


class RetrievalService:
    """
    Orchestrates the retrieval foundation:
    - Structurally aware document chunking
    - Batched vector embedding generation
    - Document-scoped vector persistence
    - Similarity threshold filtering and grounding verification
    - Ephemeral vector lifecycle deletion
    """

    def __init__(
        self,
        chunker: Optional[ChunkingService] = None,
        embedder: Optional[BaseEmbeddingService] = None,
        store: Optional[BaseVectorStore] = None,
    ):
        self._chunker = chunker or chunking_service
        self._embedder = embedder or embedding_service
        self._store = store or vector_store

    def set_dependencies(
        self,
        chunker: Optional[ChunkingService] = None,
        embedder: Optional[BaseEmbeddingService] = None,
        store: Optional[BaseVectorStore] = None,
    ) -> None:
        if chunker:
            self._chunker = chunker
        if embedder:
            self._embedder = embedder
        if store:
            self._store = store

    async def index_document(self, document: DocumentResponse) -> DocumentIndexResponse:
        start_time = time.perf_counter()
        doc_id = document.document_id

        logger.info(f"Initiating vector indexing for document id={doc_id}, chars={len(document.extracted_text)}")

        # 1. Structural chunking
        chunks = self._chunker.chunk_document(document)
        if not chunks:
            duration_ms = int((time.perf_counter() - start_time) * 1000)
            return DocumentIndexResponse(
                document_id=doc_id,
                chunk_count=0,
                indexed=True,
                processing_time_ms=duration_ms,
            )

        texts = [c.text for c in chunks]

        # 2. Batched embedding generation with partial cleanup on failure
        try:
            embeddings = await self._embedder.embed_batch(texts, task_type="retrieval_document")
        except Exception as e:
            logger.error(f"Embedding generation failed for document id={doc_id}: {str(e)}")
            # Cleanup any existing vectors for safety
            self._store.delete_document(doc_id)
            raise

        # 3. Add to vector store
        try:
            self._store.add_chunks(doc_id, chunks, embeddings)
        except Exception as e:
            logger.error(f"Vector persistence failed for document id={doc_id}: {str(e)}")
            self._store.delete_document(doc_id)
            raise

        duration_ms = int((time.perf_counter() - start_time) * 1000)
        logger.info(f"Vector indexing completed for document id={doc_id}: chunks={len(chunks)}, duration={duration_ms}ms")

        return DocumentIndexResponse(
            document_id=doc_id,
            chunk_count=len(chunks),
            indexed=True,
            processing_time_ms=duration_ms,
        )

    async def retrieve(
        self, document_id: str, query: str, top_k: int = 5
    ) -> RetrievalResult:
        clean_query = query.strip()
        if not clean_query:
            return RetrievalResult(
                document_id=document_id,
                query=query,
                grounding_status=GroundingStatus.insufficient_evidence,
                results=[],
            )

        # 1. Check if document is indexed
        if not self._store.is_indexed(document_id):
            logger.warning(f"Retrieval attempted on non-indexed document id={document_id}")
            return RetrievalResult(
                document_id=document_id,
                query=query,
                grounding_status=GroundingStatus.document_not_indexed,
                results=[],
            )

        # 2. Embed query
        query_embedding = await self._embedder.embed_text(clean_query, task_type="retrieval_query")

        # 3. Perform document-scoped vector search
        matched_candidates = self._store.search(
            document_id=document_id,
            query_embedding=query_embedding,
            top_k=top_k,
        )

        # 4. Filter by minimum similarity score
        min_threshold = settings.RETRIEVAL_MIN_SCORE
        qualified = [
            (chunk, score) for chunk, score in matched_candidates if score >= min_threshold
        ]

        if not qualified:
            logger.info(
                f"Retrieval query for document id={document_id} returned 0 candidates above score threshold {min_threshold}"
            )
            return RetrievalResult(
                document_id=document_id,
                query=query,
                grounding_status=GroundingStatus.insufficient_evidence,
                results=[],
            )

        results: List[RetrievalResultItem] = [
            RetrievalResultItem(
                chunk_id=chunk.chunk_id,
                text=chunk.text,
                similarity_score=round(score, 4),
                document_id=chunk.document_id,
                section=chunk.section,
                page_start=chunk.page_start,
                page_end=chunk.page_end,
                character_start=chunk.character_start,
                character_end=chunk.character_end,
            )
            for chunk, score in qualified
        ]

        logger.info(f"Retrieval successful for document id={document_id}: returned {len(results)} grounded chunks")
        return RetrievalResult(
            document_id=document_id,
            query=query,
            grounding_status=GroundingStatus.grounded,
            results=results,
        )

    def delete_document_vectors(self, document_id: str) -> bool:
        return self._store.delete_document(document_id)

    def is_document_indexed(self, document_id: str) -> bool:
        return self._store.is_indexed(document_id)


retrieval_service = RetrievalService()
