"""
Test Suite: LexGuard PostgreSQL + pgvector Migration & Vector Retrieval.

Verifies:
1. Connection pool and database health checking (zero secret leakage).
2. pgvector extension detection and health checks.
3. DocumentModel entity persistence and schema conformance.
4. DocumentChunkModel chunk persistence and relationships.
5. 3072-dimensional Gemini embedding vector storage.
6. Document-scoped vector search (tenant isolation via SQL).
7. Top-k ranking and candidate selection.
8. Cosine distance to similarity score mapping (1.0 - distance).
9. Retrieval minimum score threshold cutoff (0.55).
10. Re-indexing idempotency (clean atomic replacement).
11. Document vector deletion scoping (deleting doc A does not affect doc B).
12. Cross-document isolation under identical queries.
13. Citation and grounding metadata preservation.
14. Unindexed document handling and status reporting.
15. Transaction rollback on partial insertion failure.
16. Retrieval API contract compatibility (/api/v1/retrieval/search).
17. Concurrent indexing isolation.
18. ChromaDB to PostgreSQL migration dry-run functionality.
"""

import math
import asyncio
from typing import List, Dict, Any, Tuple, Optional
import pytest
from fastapi.testclient import TestClient

try:
    from backend.app.core.config import settings
    from backend.app.db.session import check_database_health
    from backend.app.models.document import DocumentModel, DocumentChunkModel
    from backend.app.schemas.document import DocumentResponse, DocumentMetadata, PageExtraction, SectionOutline
    from backend.app.schemas.retrieval import (
        DocumentChunk,
        ChunkMetadata,
        GroundingStatus,
        RetrievalSearchRequest,
        RetrievalSearchResponse,
    )
    from backend.app.services.chunking_service import ChunkingService
    from backend.app.services.embedding_service import BaseEmbeddingService
    from backend.app.services.pgvector_store import PgVectorStore
    from backend.app.services.retrieval_service import RetrievalService, retrieval_service
    from backend.app.utils.file_validation import (
        VectorStoreException,
        DocumentNotIndexedException,
    )
    from backend.scripts.migrate_chroma_to_postgres import migrate
except ImportError:
    from app.core.config import settings
    from app.db.session import check_database_health
    from app.models.document import DocumentModel, DocumentChunkModel
    from app.schemas.document import DocumentResponse, DocumentMetadata, PageExtraction, SectionOutline
    from app.schemas.retrieval import (
        DocumentChunk,
        ChunkMetadata,
        GroundingStatus,
        RetrievalSearchRequest,
        RetrievalSearchResponse,
    )
    from app.services.chunking_service import ChunkingService
    from app.services.embedding_service import BaseEmbeddingService
    from app.services.pgvector_store import PgVectorStore
    from app.services.retrieval_service import RetrievalService, retrieval_service
    from app.utils.file_validation import (
        VectorStoreException,
        DocumentNotIndexedException,
    )
    from scripts.migrate_chroma_to_postgres import migrate


# ==============================================================================
# In-Memory PgVector Session Test Double
# ==============================================================================

def calc_cosine_distance(v1: List[float], v2: List[float]) -> float:
    dot = sum(a * b for a, b in zip(v1, v2))
    norm1 = math.sqrt(sum(a * a for a in v1))
    norm2 = math.sqrt(sum(b * b for b in v2))
    if norm1 == 0 or norm2 == 0:
        return 1.0
    cos_sim = dot / (norm1 * norm2)
    return max(0.0, 1.0 - cos_sim)


def _extract_doc_id(clause) -> Optional[str]:
    """Helper to safely extract document_id from a SQLAlchemy clause without bool(clause) evaluation."""
    if clause is not None and hasattr(clause, "right"):
        return getattr(clause.right, "value", None)
    return None


class MockResult:
    def __init__(self, rows: Optional[List[Any]] = None, scalar_val: Any = None):
        self._rows = rows or []
        self._scalar_val = scalar_val

    def scalar_one_or_none(self):
        return self._scalar_val

    def scalar(self):
        return self._scalar_val

    def all(self):
        return self._rows


class InMemoryPgVectorSession:
    """
    Test double implementing the SQLAlchemy session contract used by PgVectorStore.
    Executes native vector cosine distance, document scoping, and atomic rollback.
    """

    def __init__(self, shared_storage: Dict[str, Any]):
        self._storage = shared_storage
        self._pending_docs: Dict[str, DocumentModel] = {}
        self._pending_chunks: List[DocumentChunkModel] = []
        self._deleted_chunk_doc_ids: set = set()
        self._deleted_doc_ids: set = set()
        self._is_active = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rollback()
        self.close()

    def execute(self, stmt):
        stmt_str = str(stmt).lower()

        # 1. Health check queries
        if "select 1" in stmt_str and "pg_extension" not in stmt_str:
            return MockResult(scalar_val=1)
        if "pg_extension" in stmt_str:
            return MockResult(scalar_val="vector")

        # 2. Delete statements
        if hasattr(stmt, "is_delete") and stmt.is_delete:
            where = getattr(stmt, "whereclause", None)
            doc_id = _extract_doc_id(where)
            target_table = str(stmt.table.name) if hasattr(stmt, "table") else ""
            if "document_chunks" in target_table and doc_id:
                self._deleted_chunk_doc_ids.add(doc_id)
            elif "documents" in target_table and doc_id:
                self._deleted_doc_ids.add(doc_id)
            return MockResult()

        # 3. Count query for is_indexed
        if "count" in stmt_str:
            where = getattr(stmt, "whereclause", None)
            doc_id = _extract_doc_id(where)
            # Chunks in storage not deleted + pending chunks
            existing = [
                c for c in self._storage["chunks"]
                if c.document_id == doc_id and doc_id not in self._deleted_chunk_doc_ids
            ]
            pending = [c for c in self._pending_chunks if c.document_id == doc_id]
            total_count = len(existing) + len(pending)
            return MockResult(scalar_val=total_count)

        # 4. Select DocumentModel query
        if "from documents" in stmt_str and "document_chunks" not in stmt_str:
            where = getattr(stmt, "whereclause", None)
            doc_id = _extract_doc_id(where) or ""
            doc = self._pending_docs.get(doc_id) or self._storage["docs"].get(doc_id)
            if doc_id in self._deleted_doc_ids:
                doc = None
            return MockResult(scalar_val=doc)

        # 5. Vector search query on document_chunks
        if "from document_chunks" in stmt_str and "count" not in stmt_str:
            where = getattr(stmt, "whereclause", None)
            doc_id = _extract_doc_id(where)

            # Extract query vector from order_by / dist_expr
            query_vec = None
            if hasattr(stmt, "_order_by_clauses") and stmt._order_by_clauses:
                expr = stmt._order_by_clauses[0]
                if hasattr(expr, "right") and hasattr(expr.right, "value"):
                    query_vec = expr.right.value

            limit = 5
            if hasattr(stmt, "_limit_clause") and stmt._limit_clause is not None:
                limit = stmt._limit_clause.value

            # Filter candidate chunks strictly by document_id
            candidates = [
                c for c in self._storage["chunks"]
                if c.document_id == doc_id and doc_id not in self._deleted_chunk_doc_ids
            ]
            candidates.extend([c for c in self._pending_chunks if c.document_id == doc_id])

            # Calculate cosine distance
            scored = []
            for c in candidates:
                dist = calc_cosine_distance(c.embedding, query_vec) if query_vec else 1.0
                scored.append((c, dist))

            # Order by distance ascending
            scored.sort(key=lambda x: x[1])
            top_results = scored[:limit]
            return MockResult(rows=top_results)

        return MockResult()

    def add(self, instance):
        if isinstance(instance, DocumentModel):
            self._pending_docs[instance.document_id] = instance
        elif isinstance(instance, DocumentChunkModel):
            self._pending_chunks.append(instance)

    def add_all(self, instances):
        for inst in instances:
            self.add(inst)

    def flush(self):
        pass

    def commit(self):
        # Apply deletions
        for doc_id in self._deleted_chunk_doc_ids:
            self._storage["chunks"] = [
                c for c in self._storage["chunks"] if c.document_id != doc_id
            ]
        for doc_id in self._deleted_doc_ids:
            self._storage["docs"].pop(doc_id, None)

        # Apply additions
        self._storage["docs"].update(self._pending_docs)
        self._storage["chunks"].extend(self._pending_chunks)

        self._pending_docs.clear()
        self._pending_chunks.clear()
        self._deleted_chunk_doc_ids.clear()
        self._deleted_doc_ids.clear()

    def rollback(self):
        self._pending_docs.clear()
        self._pending_chunks.clear()
        self._deleted_chunk_doc_ids.clear()
        self._deleted_doc_ids.clear()

    def close(self):
        self._is_active = False


class InMemoryPgVectorSessionFactory:
    def __init__(self):
        self.storage = {"docs": {}, "chunks": []}

    def __call__(self):
        return InMemoryPgVectorSession(self.storage)


# ==============================================================================
# Deterministic 3072-Dimensional Embedding Service Test Double
# ==============================================================================

class Deterministic3072EmbeddingService(BaseEmbeddingService):
    """Generates deterministic 3072-dimensional unit vectors."""

    KEYWORD_INDICES = {
        "termination": 0,
        "notice": 0,
        "liability": 100,
        "indemnification": 200,
        "confidential": 300,
        "intellectual": 400,
        "arbitration": 500,
    }

    async def embed_text(self, text: str, task_type: str = "retrieval_document") -> List[float]:
        dim = settings.EMBEDDING_DIMENSION  # 3072
        vec = [0.01] * dim
        lower = text.lower()
        for kw, idx in self.KEYWORD_INDICES.items():
            if kw in lower and idx < dim:
                vec[idx] += 2.0

        norm = math.sqrt(sum(x * x for x in vec))
        return [x / norm for x in vec]

    async def embed_batch(
        self, texts: List[str], task_type: str = "retrieval_document"
    ) -> List[List[float]]:
        return [await self.embed_text(t, task_type) for t in texts]


# ==============================================================================
# Fixtures
# ==============================================================================

@pytest.fixture
def mock_session_factory() -> InMemoryPgVectorSessionFactory:
    return InMemoryPgVectorSessionFactory()


@pytest.fixture
def pg_store(mock_session_factory: InMemoryPgVectorSessionFactory) -> PgVectorStore:
    return PgVectorStore(session_factory=mock_session_factory)


@pytest.fixture
def embedder_3072() -> BaseEmbeddingService:
    return Deterministic3072EmbeddingService()


@pytest.fixture
def legal_document_response() -> DocumentResponse:
    return DocumentResponse(
        document_id="doc_pg_test_001",
        filename="master_services_agreement.txt",
        file_type="txt",
        source_type="upload",
        page_count=2,
        word_count=120,
        character_count=700,
        extracted_text=(
            "ARTICLE 8: TERMINATION FOR CONVENIENCE\n"
            "Either party may terminate this Agreement upon ninety (90) days written notice.\n\n"
            "§ 12.4 INDEMNIFICATION OBLIGATIONS\n"
            "Provider shall defend, indemnify, and hold harmless Customer against third-party claims.\n\n"
            "ARTICLE 15: LIMITATION OF LIABILITY\n"
            "In no event shall aggregate liability exceed the total fees paid under this Agreement."
        ),
        pages=[
            PageExtraction(
                page_number=1,
                text="ARTICLE 8: TERMINATION FOR CONVENIENCE\nEither party may terminate this Agreement upon ninety (90) days written notice.",
                character_start=0,
                character_end=116,
                word_count=19,
            ),
            PageExtraction(
                page_number=2,
                text="§ 12.4 INDEMNIFICATION OBLIGATIONS\nProvider shall defend, indemnify, and hold harmless Customer against third-party claims.\n\nARTICLE 15: LIMITATION OF LIABILITY\nIn no event shall aggregate liability exceed the total fees paid under this Agreement.",
                character_start=118,
                character_end=348,
                word_count=35,
            ),
        ],
        sections=[
            SectionOutline(title="ARTICLE 8: TERMINATION FOR CONVENIENCE", page_number=1, character_offset=0),
            SectionOutline(title="§ 12.4 INDEMNIFICATION OBLIGATIONS", page_number=2, character_offset=118),
            SectionOutline(title="ARTICLE 15: LIMITATION OF LIABILITY", page_number=2, character_offset=235),
        ],
        metadata=DocumentMetadata(
            original_filename="master_services_agreement.txt",
            file_size_bytes=700,
            mime_type="text/plain",
            sha256_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            extraction_engine="raw_text",
        ),
    )


# ==============================================================================
# 18 Test Cases
# ==============================================================================

# 1. Database Connection & Health Verification
@pytest.mark.anyio
async def test_database_connection():
    """Verify check_database_health() executes safely and redacts credentials."""
    health = await check_database_health()
    assert "connected" in health
    assert "vector_extension" in health
    assert "status" in health
    # Ensure zero password or URI leakage
    for key, value in health.items():
        assert "password" not in str(key).lower()
        assert "password" not in str(value).lower()
        assert "postgres://" not in str(value).lower()


# 2. pgvector Extension Check
def test_pgvector_extension_available(pg_store: PgVectorStore):
    """Verify health_check queries pg_extension for vector."""
    is_healthy = pg_store.health_check()
    assert is_healthy is True


# 3. DocumentModel Entity Insertion
def test_document_insertion(mock_session_factory: InMemoryPgVectorSessionFactory):
    """Verify DocumentModel attributes, persistence, and status tracking."""
    session = mock_session_factory()
    doc = DocumentModel(
        document_id="doc_ins_01",
        filename="contract.pdf",
        document_type="pdf",
        source_type="upload",
        mime_type="application/pdf",
        word_count=500,
        character_count=3000,
        page_count=3,
        content_hash="abc123hash",
        processing_status="uploaded",
    )
    session.add(doc)
    session.commit()

    saved_doc = mock_session_factory.storage["docs"].get("doc_ins_01")
    assert saved_doc is not None
    assert saved_doc.filename == "contract.pdf"
    assert saved_doc.page_count == 3
    assert saved_doc.processing_status == "uploaded"


# 4. DocumentChunkModel Chunk Insertion
def test_chunks_insertion(pg_store: PgVectorStore, mock_session_factory: InMemoryPgVectorSessionFactory):
    """Verify DocumentChunkModel attributes and metadata serialization."""
    chunks = [
        DocumentChunk(
            chunk_id="chk_01",
            document_id="doc_chunks_01",
            chunk_index=0,
            text="Clause 1: Confidentiality obligation.",
            section="ARTICLE 1",
            page_start=1,
            page_end=1,
            character_start=0,
            character_end=37,
            token_estimate=8,
            metadata=ChunkMetadata(
                document_id="doc_chunks_01",
                chunk_id="chk_01",
                section="ARTICLE 1",
                page_start=1,
                page_end=1,
                character_start=0,
                character_end=37,
            ),
        )
    ]
    embeddings = [[0.1] * settings.EMBEDDING_DIMENSION]

    pg_store.add_chunks("doc_chunks_01", chunks, embeddings)

    stored_chunks = mock_session_factory.storage["chunks"]
    assert len(stored_chunks) == 1
    assert stored_chunks[0].chunk_id == "chk_01"
    assert stored_chunks[0].document_id == "doc_chunks_01"
    assert stored_chunks[0].content == "Clause 1: Confidentiality obligation."
    assert stored_chunks[0].section == "ARTICLE 1"


# 5. 3072-Dimensional Vector Embedding Storage
def test_3072_embedding_storage(pg_store: PgVectorStore, mock_session_factory: InMemoryPgVectorSessionFactory):
    """Verify exact 3072-dimensional vector embedding storage."""
    dim = settings.EMBEDDING_DIMENSION
    assert dim == 3072

    vec_3072 = [0.005] * dim
    vec_3072[42] = 0.99  # Distinctive marker

    chunk = DocumentChunk(
        chunk_id="chk_dim_3072",
        document_id="doc_dim_test",
        chunk_index=0,
        text="Dimensionality test chunk.",
        page_start=1,
        page_end=1,
        character_start=0,
        character_end=26,
        token_estimate=5,
        metadata=ChunkMetadata(
            document_id="doc_dim_test",
            chunk_id="chk_dim_3072",
            page_start=1,
            page_end=1,
            character_start=0,
            character_end=26,
        ),
    )

    pg_store.add_chunks("doc_dim_test", [chunk], [vec_3072])
    stored_vec = mock_session_factory.storage["chunks"][0].embedding
    assert len(stored_vec) == 3072
    assert stored_vec[42] == 0.99


# 6. Document-Scoped Vector Search (Tenant Isolation)
def test_document_scoped_vector_search(pg_store: PgVectorStore):
    """Verify vector search is strictly isolated to the specified document_id."""
    # Add chunks for Document A
    chunk_a = DocumentChunk(
        chunk_id="chk_a",
        document_id="doc_A",
        chunk_index=0,
        text="Doc A termination clause.",
        page_start=1,
        page_end=1,
        character_start=0,
        character_end=25,
        token_estimate=5,
        metadata=ChunkMetadata(document_id="doc_A", chunk_id="chk_a", page_start=1, page_end=1, character_start=0, character_end=25),
    )
    vec_a = [1.0] + [0.0] * 3071

    # Add chunks for Document B
    chunk_b = DocumentChunk(
        chunk_id="chk_b",
        document_id="doc_B",
        chunk_index=0,
        text="Doc B termination clause.",
        page_start=1,
        page_end=1,
        character_start=0,
        character_end=25,
        token_estimate=5,
        metadata=ChunkMetadata(document_id="doc_B", chunk_id="chk_b", page_start=1, page_end=1, character_start=0, character_end=25),
    )
    vec_b = [1.0] + [0.0] * 3071

    pg_store.add_chunks("doc_A", [chunk_a], [vec_a])
    pg_store.add_chunks("doc_B", [chunk_b], [vec_b])

    # Search with doc_A scoping
    query_vec = [1.0] + [0.0] * 3071
    results = pg_store.search("doc_A", query_vec, top_k=5)

    assert len(results) == 1
    found_chunk, score = results[0]
    assert found_chunk.document_id == "doc_A"
    assert found_chunk.chunk_id == "chk_a"


# 7. Top-k Retrieval Ranking
def test_top_k_retrieval(pg_store: PgVectorStore):
    """Verify top-k parameter limits results and preserves descending similarity."""
    dim = 3072
    chunks = []
    embeddings = []
    # Seed 6 chunks with increasing distance
    for i in range(6):
        c = DocumentChunk(
            chunk_id=f"chk_rank_{i}",
            document_id="doc_rank",
            chunk_index=i,
            text=f"Rank chunk {i}",
            page_start=1,
            page_end=1,
            character_start=i * 20,
            character_end=(i + 1) * 20,
            token_estimate=4,
            metadata=ChunkMetadata(document_id="doc_rank", chunk_id=f"chk_rank_{i}", page_start=1, page_end=1, character_start=i * 20, character_end=(i + 1) * 20),
        )
        vec = [0.0] * dim
        vec[0] = 1.0 - (i * 0.1)
        vec[i + 1] = 0.5
        norm = math.sqrt(sum(x * x for x in vec))
        vec = [x / norm for x in vec]
        chunks.append(c)
        embeddings.append(vec)

    pg_store.add_chunks("doc_rank", chunks, embeddings)

    query_vec = [1.0] + [0.0] * (dim - 1)
    results = pg_store.search("doc_rank", query_vec, top_k=3)

    assert len(results) == 3
    scores = [score for _, score in results]
    assert scores == sorted(scores, reverse=True)


# 8. Cosine Distance to Similarity Score Mapping
def test_similarity_score_mapping(pg_store: PgVectorStore):
    """Verify identical vectors yield similarity 1.0 and orthogonal vectors yield ~0.0."""
    dim = 3072
    v_target = [1.0] + [0.0] * (dim - 1)
    v_ortho = [0.0, 1.0] + [0.0] * (dim - 2)

    chunk_target = DocumentChunk(
        chunk_id="chk_sim_1",
        document_id="doc_sim",
        chunk_index=0,
        text="Target vector chunk",
        page_start=1,
        page_end=1,
        character_start=0,
        character_end=20,
        token_estimate=4,
        metadata=ChunkMetadata(document_id="doc_sim", chunk_id="chk_sim_1", page_start=1, page_end=1, character_start=0, character_end=20),
    )
    chunk_ortho = DocumentChunk(
        chunk_id="chk_sim_2",
        document_id="doc_sim",
        chunk_index=1,
        text="Orthogonal vector chunk",
        page_start=1,
        page_end=1,
        character_start=21,
        character_end=45,
        token_estimate=4,
        metadata=ChunkMetadata(document_id="doc_sim", chunk_id="chk_sim_2", page_start=1, page_end=1, character_start=21, character_end=45),
    )

    pg_store.add_chunks("doc_sim", [chunk_target, chunk_ortho], [v_target, v_ortho])

    results = pg_store.search("doc_sim", v_target, top_k=2)
    assert len(results) == 2

    # First match is target (identical)
    assert results[0][0].chunk_id == "chk_sim_1"
    assert pytest.approx(results[0][1], rel=1e-3) == 1.0

    # Second match is orthogonal
    assert results[1][0].chunk_id == "chk_sim_2"
    assert pytest.approx(results[1][1], abs=0.05) == 0.0


# 9. Minimum Score Filtering & Insufficient Evidence
@pytest.mark.anyio
async def test_retrieval_min_score_cutoff(
    pg_store: PgVectorStore, embedder_3072: BaseEmbeddingService, legal_document_response: DocumentResponse
):
    """Verify chunks with similarity < RETRIEVAL_MIN_SCORE (0.55) are filtered out."""
    service = RetrievalService(
        chunker=ChunkingService(target_tokens=40, min_tokens=10),
        embedder=embedder_3072,
        store=pg_store,
    )
    await service.index_document(legal_document_response)

    # Irrelevant query having almost zero similarity to legal contract
    result = await service.retrieve(
        legal_document_response.document_id,
        "underwater basket weaving techniques in ancient mesopotamia",
    )
    assert result.grounding_status == GroundingStatus.insufficient_evidence
    assert len(result.results) == 0


# 10. Re-indexing Idempotency
def test_reindexing_idempotency(pg_store: PgVectorStore, mock_session_factory: InMemoryPgVectorSessionFactory):
    """Verify re-indexing replaces chunks cleanly without duplicate key conflicts."""
    dim = 3072
    chunk_v1 = DocumentChunk(
        chunk_id="chk_v1",
        document_id="doc_idemp",
        chunk_index=0,
        text="Version 1 text.",
        page_start=1,
        page_end=1,
        character_start=0,
        character_end=15,
        token_estimate=3,
        metadata=ChunkMetadata(document_id="doc_idemp", chunk_id="chk_v1", page_start=1, page_end=1, character_start=0, character_end=15),
    )
    pg_store.add_chunks("doc_idemp", [chunk_v1], [[0.1] * dim])
    assert len(mock_session_factory.storage["chunks"]) == 1

    # Re-index with Version 2 chunk
    chunk_v2 = DocumentChunk(
        chunk_id="chk_v2",
        document_id="doc_idemp",
        chunk_index=0,
        text="Version 2 replaced text.",
        page_start=1,
        page_end=1,
        character_start=0,
        character_end=24,
        token_estimate=5,
        metadata=ChunkMetadata(document_id="doc_idemp", chunk_id="chk_v2", page_start=1, page_end=1, character_start=0, character_end=24),
    )
    pg_store.add_chunks("doc_idemp", [chunk_v2], [[0.2] * dim])

    assert len(mock_session_factory.storage["chunks"]) == 1
    assert mock_session_factory.storage["chunks"][0].chunk_id == "chk_v2"
    assert mock_session_factory.storage["chunks"][0].content == "Version 2 replaced text."


# 11. Delete Vectors Scoping
def test_delete_vectors_scoping(pg_store: PgVectorStore, mock_session_factory: InMemoryPgVectorSessionFactory):
    """Verify deleting vectors for doc_A removes its chunks while leaving doc_B intact."""
    dim = 3072
    chunk_a = DocumentChunk(
        chunk_id="chk_del_a",
        document_id="doc_del_A",
        chunk_index=0,
        text="Doc A chunk",
        page_start=1,
        page_end=1,
        character_start=0,
        character_end=11,
        token_estimate=3,
        metadata=ChunkMetadata(document_id="doc_del_A", chunk_id="chk_del_a", page_start=1, page_end=1, character_start=0, character_end=11),
    )
    chunk_b = DocumentChunk(
        chunk_id="chk_del_b",
        document_id="doc_del_B",
        chunk_index=0,
        text="Doc B chunk",
        page_start=1,
        page_end=1,
        character_start=0,
        character_end=11,
        token_estimate=3,
        metadata=ChunkMetadata(document_id="doc_del_B", chunk_id="chk_del_b", page_start=1, page_end=1, character_start=0, character_end=11),
    )

    pg_store.add_chunks("doc_del_A", [chunk_a], [[0.1] * dim])
    pg_store.add_chunks("doc_del_B", [chunk_b], [[0.1] * dim])

    assert pg_store.is_indexed("doc_del_A") is True
    assert pg_store.is_indexed("doc_del_B") is True

    # Delete doc_del_A
    deleted = pg_store.delete_document("doc_del_A")
    assert deleted is True

    assert pg_store.is_indexed("doc_del_A") is False
    assert pg_store.is_indexed("doc_del_B") is True
    remaining_chunks = mock_session_factory.storage["chunks"]
    assert len(remaining_chunks) == 1
    assert remaining_chunks[0].document_id == "doc_del_B"


# 12. Cross-Document Isolation Under Identical Query
def test_cross_document_isolation(pg_store: PgVectorStore):
    """Verify identical queries return only chunks belonging to the targeted document."""
    dim = 3072
    target_vec = [1.0] + [0.0] * (dim - 1)

    chunk_secret = DocumentChunk(
        chunk_id="chk_confidential_tenant",
        document_id="tenant_X",
        chunk_index=0,
        text="Secret offshore financial routing numbers: 994-118-204.",
        page_start=1,
        page_end=1,
        character_start=0,
        character_end=56,
        token_estimate=12,
        metadata=ChunkMetadata(document_id="tenant_X", chunk_id="chk_confidential_tenant", page_start=1, page_end=1, character_start=0, character_end=56),
    )
    pg_store.add_chunks("tenant_X", [chunk_secret], [target_vec])

    # Search against tenant_Y with the exact vector that matches tenant_X chunk
    results = pg_store.search("tenant_Y", target_vec, top_k=5)
    assert len(results) == 0


# 13. Metadata & Citation Preservation
@pytest.mark.anyio
async def test_metadata_citation_preservation(
    pg_store: PgVectorStore, embedder_3072: BaseEmbeddingService, legal_document_response: DocumentResponse
):
    """Verify section headings, page numbers, and character bounds survive retrieval intact."""
    service = RetrievalService(
        chunker=ChunkingService(target_tokens=40, min_tokens=10),
        embedder=embedder_3072,
        store=pg_store,
    )
    await service.index_document(legal_document_response)

    result = await service.retrieve(legal_document_response.document_id, "indemnification obligations")
    assert result.grounding_status == GroundingStatus.grounded
    assert len(result.results) >= 1

    top_item = result.results[0]
    assert top_item.page_start >= 1
    assert top_item.character_end > top_item.character_start
    assert top_item.section is not None
    assert "INDEMNIFICATION" in top_item.section.upper()


# 14. Unindexed Document Handling
@pytest.mark.anyio
async def test_unindexed_document_reports_status(pg_store: PgVectorStore, embedder_3072: BaseEmbeddingService):
    """Verify searching an unindexed document ID returns document_not_indexed grounding status."""
    service = RetrievalService(
        chunker=ChunkingService(),
        embedder=embedder_3072,
        store=pg_store,
    )

    result = await service.retrieve("non_existent_doc_id", "any query")
    assert result.grounding_status == GroundingStatus.document_not_indexed
    assert len(result.results) == 0


# 15. Transaction Rollback on Failure
def test_transaction_rollback_on_failure(mock_session_factory: InMemoryPgVectorSessionFactory):
    """Verify exception during insertion rolls back transaction with zero orphaned chunks."""
    class FailingSession(InMemoryPgVectorSession):
        def add_all(self, instances):
            raise RuntimeError("Database disk full error")

    failing_factory = lambda: FailingSession(mock_session_factory.storage)
    store = PgVectorStore(session_factory=failing_factory)

    chunk = DocumentChunk(
        chunk_id="chk_fail",
        document_id="doc_rollback",
        chunk_index=0,
        text="Rollback candidate",
        page_start=1,
        page_end=1,
        character_start=0,
        character_end=18,
        token_estimate=3,
        metadata=ChunkMetadata(document_id="doc_rollback", chunk_id="chk_fail", page_start=1, page_end=1, character_start=0, character_end=18),
    )

    with pytest.raises(VectorStoreException):
        store.add_chunks("doc_rollback", [chunk], [[0.1] * 3072])

    # Assert nothing was added to permanent storage
    assert len(mock_session_factory.storage["chunks"]) == 0
    assert "doc_rollback" not in mock_session_factory.storage["docs"]


# 16. Retrieval API Contract Compatibility
def test_retrieval_api_contract_compatibility(
    client: TestClient, pg_store: PgVectorStore, embedder_3072: BaseEmbeddingService
):
    """Verify /api/v1/retrieval/search response adheres strictly to the API schema."""
    retrieval_service.set_dependencies(
        embedder=embedder_3072,
        store=pg_store,
    )

    # Seed document
    dim = 3072
    chunk = DocumentChunk(
        chunk_id="chk_api_01",
        document_id="doc_api_compat",
        chunk_index=0,
        text="Customer may terminate for convenience with 30 days notice.",
        section="ARTICLE 8",
        page_start=1,
        page_end=1,
        character_start=0,
        character_end=58,
        token_estimate=12,
        metadata=ChunkMetadata(
            document_id="doc_api_compat",
            chunk_id="chk_api_01",
            section="ARTICLE 8",
            page_start=1,
            page_end=1,
            character_start=0,
            character_end=58,
        ),
    )
    pg_store.add_chunks("doc_api_compat", [chunk], [[0.5] * dim])

    payload = {
        "document_id": "doc_api_compat",
        "query": "termination notice",
        "top_k": 3,
    }
    response = client.post("/api/v1/retrieval/search", json=payload)
    assert response.status_code == 200
    data = response.json()

    # Validate schema fields
    assert data["document_id"] == "doc_api_compat"
    assert data["query"] == "termination notice"
    assert "grounding_status" in data
    assert "results" in data
    assert isinstance(data["results"], list)


# 17. Concurrent Indexing Isolation
@pytest.mark.anyio
async def test_concurrent_indexing_isolation(
    pg_store: PgVectorStore, embedder_3072: BaseEmbeddingService
):
    """Verify simultaneous indexing operations on different documents execute safely."""
    service = RetrievalService(
        chunker=ChunkingService(target_tokens=30, min_tokens=10),
        embedder=embedder_3072,
        store=pg_store,
    )

    async def create_and_index(doc_idx: int):
        doc = DocumentResponse(
            document_id=f"doc_conc_{doc_idx}",
            filename=f"doc_{doc_idx}.txt",
            file_type="txt",
            source_type="upload",
            page_count=1,
            word_count=20,
            character_count=100,
            extracted_text=f"Document {doc_idx} provides unique agreement terms for tenant {doc_idx}.",
            pages=[
                PageExtraction(
                    page_number=1,
                    text=f"Document {doc_idx} provides unique agreement terms for tenant {doc_idx}.",
                    character_start=0,
                    character_end=70,
                    word_count=10,
                )
            ],
            sections=[],
            metadata=DocumentMetadata(
                original_filename=f"doc_{doc_idx}.txt",
                file_size_bytes=100,
                mime_type="text/plain",
                sha256_hash=f"hash_{doc_idx}",
                extraction_engine="raw_text",
            ),
        )
        return await service.index_document(doc)

    # Launch 5 concurrent index operations
    results = await asyncio.gather(*(create_and_index(i) for i in range(5)))
    assert len(results) == 5
    for i, res in enumerate(results):
        assert res.document_id == f"doc_conc_{i}"
        assert res.indexed is True
        assert pg_store.is_indexed(f"doc_conc_{i}") is True


# 18. ChromaDB to PostgreSQL Migration Dry-Run
def test_chroma_to_postgres_migration_dry_run(tmp_path, capsys):
    """Verify migrate_chroma_to_postgres runs safely with dry_run=True."""
    dummy_path = tmp_path / "empty_chroma"
    migrate(chroma_dir=str(dummy_path), dry_run=True)
    out = capsys.readouterr().out
    assert "MIGRATION" in out
    assert ("Nothing to migrate" in out) or ("dry_run=True" in out)
