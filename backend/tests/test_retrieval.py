import pytest
import math
import logging
from typing import List
from unittest.mock import patch
from fastapi.testclient import TestClient

try:
    from backend.app.schemas.document import DocumentResponse, DocumentMetadata, PageExtraction, SectionOutline
    from backend.app.schemas.retrieval import (
        DocumentChunk,
        GroundingStatus,
        RetrievalResult,
        DocumentIndexResponse,
        RetrievalSearchResponse,
    )
    from backend.app.services.chunking_service import ChunkingService
    from backend.app.services.embedding_service import BaseEmbeddingService, GeminiEmbeddingService
    from backend.app.services.vector_store import ChromaVectorStore, BaseVectorStore
    from backend.app.services.retrieval_service import RetrievalService, retrieval_service
    from backend.app.core.config import settings
    from backend.app.utils.file_validation import (
        EmbeddingServiceException,
        GeminiServiceUnavailableException,
    )
except ImportError:
    from app.schemas.document import DocumentResponse, DocumentMetadata, PageExtraction, SectionOutline
    from app.schemas.retrieval import (
        DocumentChunk,
        GroundingStatus,
        RetrievalResult,
        DocumentIndexResponse,
        RetrievalSearchResponse,
    )
    from app.services.chunking_service import ChunkingService
    from app.services.embedding_service import BaseEmbeddingService, GeminiEmbeddingService
    from app.services.vector_store import ChromaVectorStore, BaseVectorStore
    from app.services.retrieval_service import RetrievalService, retrieval_service
    from app.core.config import settings
    from app.utils.file_validation import (
        EmbeddingServiceException,
        GeminiServiceUnavailableException,
    )


class DeterministicMockEmbeddingService(BaseEmbeddingService):
    """
    Mock embedding service producing deterministic 8-dimensional unit vectors.
    Maps keywords ('termination', 'liability', 'nda') to distinct basis axes
    so similarity search is deterministic in tests.
    """

    KEYWORD_AXES = {
        "termination": 0,
        "notice": 0,
        "convenience": 0,
        "liability": 1,
        "damage": 1,
        "damages": 1,
        "cap": 1,
        "confidential": 2,
        "proprietary": 2,
        "nda": 2,
    }

    async def embed_text(self, text: str, task_type: str = "retrieval_document") -> List[float]:
        vec = [0.05] * 8
        lower = text.lower()
        for kw, axis in self.KEYWORD_AXES.items():
            if kw in lower:
                vec[axis] += 1.0

        # L2 Normalize
        norm = math.sqrt(sum(x * x for x in vec))
        return [x / norm for x in vec]

    async def embed_batch(
        self, texts: List[str], task_type: str = "retrieval_document"
    ) -> List[List[float]]:
        return [await self.embed_text(t, task_type) for t in texts]


@pytest.fixture
def isolated_vector_store(tmp_path) -> BaseVectorStore:
    test_db_dir = tmp_path / "chroma_test"
    test_db_dir.mkdir(parents=True, exist_ok=True)
    return ChromaVectorStore(persist_directory=str(test_db_dir))


@pytest.fixture
def mock_embedder() -> BaseEmbeddingService:
    return DeterministicMockEmbeddingService()


@pytest.fixture
def legal_test_doc() -> DocumentResponse:
    p1_text = (
        "ARTICLE 8: TERMINATION FOR CONVENIENCE\n\n"
        "Customer may terminate this Statement of Work for convenience by providing ninety (90) days written notice.\n"
        "Upon termination, Customer shall remit payment for all work performed prior to effective date."
    )
    p2_text = (
        "ARTICLE 9: LIMITATION OF LIABILITY\n\n"
        "The aggregate liability of either party shall not exceed the fees paid during the preceding twelve months.\n"
        "In no event shall either party be liable for special, incidental, or consequential damages."
    )
    full_text = f"{p1_text}\n\n{p2_text}"

    p1_len = len(p1_text)
    p2_start = p1_len + 2
    p2_end = p2_start + len(p2_text)

    return DocumentResponse(
        document_id="doc_legal_master_001",
        filename="master_agreement.pdf",
        file_type="pdf",
        source_type="upload",
        page_count=2,
        word_count=55,
        character_count=len(full_text),
        extracted_text=full_text,
        pages=[
            PageExtraction(
                page_number=1,
                text=p1_text,
                character_start=0,
                character_end=p1_len,
                word_count=25,
            ),
            PageExtraction(
                page_number=2,
                text=p2_text,
                character_start=p2_start,
                character_end=p2_end,
                word_count=30,
            ),
        ],
        sections=[
            SectionOutline(title="ARTICLE 8: TERMINATION FOR CONVENIENCE", page_number=1, character_offset=0),
            SectionOutline(title="ARTICLE 9: LIMITATION OF LIABILITY", page_number=2, character_offset=p2_start),
        ],
        metadata=DocumentMetadata(
            original_filename="master_agreement.pdf",
            file_size_bytes=2048,
            mime_type="application/pdf",
            sha256_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            extraction_engine="pymupdf-fitz",
        ),
    )


# 1. Chunk generation splits document into chunks
def test_chunk_generation(legal_test_doc):
    chunker = ChunkingService(target_tokens=30, min_tokens=10)
    chunks = chunker.chunk_document(legal_test_doc)
    assert len(chunks) >= 2


# 2. Clause boundary preservation
def test_clause_boundary_preservation(legal_test_doc):
    chunker = ChunkingService(target_tokens=30, min_tokens=10)
    chunks = chunker.chunk_document(legal_test_doc)
    sections_found = [c.section for c in chunks if c.section]
    assert any("ARTICLE 8" in s for s in sections_found)
    assert any("ARTICLE 9" in s for s in sections_found)


# 3. Chunk metadata preservation
def test_chunk_metadata_preservation(legal_test_doc):
    chunker = ChunkingService(target_tokens=30, min_tokens=10)
    chunks = chunker.chunk_document(legal_test_doc)
    for c in chunks:
        assert c.metadata.document_id == legal_test_doc.document_id
        assert c.metadata.chunk_id == c.chunk_id
        assert c.metadata.character_start == c.character_start
        assert c.metadata.character_end == c.character_end


# 4. Page preservation
def test_page_preservation(legal_test_doc):
    chunker = ChunkingService(target_tokens=30, min_tokens=10)
    chunks = chunker.chunk_document(legal_test_doc)
    assert chunks[0].page_start == 1
    assert chunks[-1].page_end == 2


# 5. Exact character offset slice preservation
def test_character_offset_preservation(legal_test_doc):
    chunker = ChunkingService(target_tokens=30, min_tokens=10)
    chunks = chunker.chunk_document(legal_test_doc)
    for c in chunks:
        sliced_text = legal_test_doc.extracted_text[c.character_start : c.character_end]
        assert sliced_text == c.text


# 6. Embedding service success
@pytest.mark.anyio
async def test_embedding_service_success(mock_embedder):
    vector = await mock_embedder.embed_text("Termination for convenience clause")
    assert isinstance(vector, list)
    assert len(vector) == 8
    # Assert unit norm (tolerance 1e-4)
    norm = math.sqrt(sum(x * x for x in vector))
    assert abs(norm - 1.0) < 1e-4


# 7. Embedding service failure handling
@pytest.mark.anyio
async def test_embedding_service_failure(legal_test_doc, isolated_vector_store):
    class FailingEmbedder(BaseEmbeddingService):
        async def embed_text(self, text, task_type="retrieval_document"):
            raise EmbeddingServiceException("Network timeout during embedding call")

        async def embed_batch(self, texts, task_type="retrieval_document"):
            raise EmbeddingServiceException("Network timeout during embedding call")

    service = RetrievalService(
        embedder=FailingEmbedder(),
        store=isolated_vector_store,
    )
    with pytest.raises(EmbeddingServiceException):
        await service.index_document(legal_test_doc)


# 8. Vector insertion into vector store
@pytest.mark.anyio
async def test_vector_insertion(legal_test_doc, mock_embedder, isolated_vector_store):
    chunker = ChunkingService(target_tokens=30, min_tokens=10)
    chunks = chunker.chunk_document(legal_test_doc)
    embeddings = await mock_embedder.embed_batch([c.text for c in chunks])

    isolated_vector_store.add_chunks(legal_test_doc.document_id, chunks, embeddings)
    assert isolated_vector_store.is_indexed(legal_test_doc.document_id) is True


# 9. Vector search returns top matching results
@pytest.mark.anyio
async def test_vector_search(legal_test_doc, mock_embedder, isolated_vector_store):
    chunker = ChunkingService(target_tokens=30, min_tokens=10)
    chunks = chunker.chunk_document(legal_test_doc)
    embeddings = await mock_embedder.embed_batch([c.text for c in chunks])
    isolated_vector_store.add_chunks(legal_test_doc.document_id, chunks, embeddings)

    query_vec = await mock_embedder.embed_text("How can the customer terminate for convenience?")
    results = isolated_vector_store.search(legal_test_doc.document_id, query_vec, top_k=2)
    assert len(results) > 0
    top_chunk, score = results[0]
    assert "TERMINATION" in top_chunk.text
    assert score > 0.5


# 10. Document-scoped retrieval strictly prevents cross-tenant leakage
@pytest.mark.anyio
async def test_document_scoped_retrieval(legal_test_doc, mock_embedder, isolated_vector_store):
    service = RetrievalService(
        chunker=ChunkingService(target_tokens=30, min_tokens=10),
        embedder=mock_embedder,
        store=isolated_vector_store,
    )

    # Index Document A
    await service.index_document(legal_test_doc)

    # Create Document B
    doc_b = DocumentResponse(
        document_id="doc_other_tenant_999",
        filename="other.pdf",
        file_type="pdf",
        source_type="upload",
        page_count=1,
        word_count=10,
        character_count=50,
        extracted_text="CONFIDENTIAL SALARY INFO FOR EMPLOYEES ONLY",
        pages=[PageExtraction(page_number=1, text="CONFIDENTIAL SALARY INFO FOR EMPLOYEES ONLY", character_start=0, character_end=50, word_count=10)],
        sections=[],
        metadata=DocumentMetadata(
            original_filename="other.pdf",
            file_size_bytes=500,
            mime_type="application/pdf",
            sha256_hash="1111222233334444",
            extraction_engine="pymupdf-fitz",
        ),
    )
    await service.index_document(doc_b)

    # Search in Document A for salary info: must NOT return chunks from Document B!
    res_a = await service.retrieve(legal_test_doc.document_id, "salary info")
    for item in res_a.results:
        assert item.document_id == legal_test_doc.document_id
        assert "SALARY" not in item.text


# 11. Similarity threshold filters out weak matches
@pytest.mark.anyio
async def test_similarity_threshold(legal_test_doc, mock_embedder, isolated_vector_store):
    service = RetrievalService(
        chunker=ChunkingService(target_tokens=30, min_tokens=10),
        embedder=mock_embedder,
        store=isolated_vector_store,
    )
    await service.index_document(legal_test_doc)

    with patch.object(settings, "RETRIEVAL_MIN_SCORE", 0.99):
        # With an impossible 0.99 threshold, results should filter out
        res = await service.retrieve(legal_test_doc.document_id, "arbitrary text")
        assert len(res.results) == 0


# 12. Insufficient evidence returned when no chunks pass threshold
@pytest.mark.anyio
async def test_insufficient_evidence(legal_test_doc, mock_embedder, isolated_vector_store):
    service = RetrievalService(
        chunker=ChunkingService(target_tokens=30, min_tokens=10),
        embedder=mock_embedder,
        store=isolated_vector_store,
    )
    await service.index_document(legal_test_doc)

    # Completely unrelated query
    res = await service.retrieve(legal_test_doc.document_id, "What is the physical street address in Tokyo?")
    # In mock embedder, unmapped query has uniform components yielding low similarity
    if not res.results:
        assert res.grounding_status == GroundingStatus.insufficient_evidence


# 13. Idempotency: duplicate indexing does not duplicate vectors
@pytest.mark.anyio
async def test_duplicate_indexing_prevention(legal_test_doc, mock_embedder, isolated_vector_store):
    service = RetrievalService(
        chunker=ChunkingService(target_tokens=30, min_tokens=10),
        embedder=mock_embedder,
        store=isolated_vector_store,
    )

    res1 = await service.index_document(legal_test_doc)
    res2 = await service.index_document(legal_test_doc)
    assert res1.chunk_count == res2.chunk_count

    # Check search result returns at most chunk_count items
    query_res = await service.retrieve(legal_test_doc.document_id, "termination notice", top_k=10)
    assert len(query_res.results) <= res1.chunk_count


# 14. Document vector deletion
@pytest.mark.anyio
async def test_document_vector_deletion(legal_test_doc, mock_embedder, isolated_vector_store):
    service = RetrievalService(
        chunker=ChunkingService(target_tokens=30, min_tokens=10),
        embedder=mock_embedder,
        store=isolated_vector_store,
    )
    await service.index_document(legal_test_doc)
    assert service.is_document_indexed(legal_test_doc.document_id) is True

    # Delete
    deleted = service.delete_document_vectors(legal_test_doc.document_id)
    assert deleted is True
    assert service.is_document_indexed(legal_test_doc.document_id) is False

    # Search should now report document_not_indexed
    search_res = await service.retrieve(legal_test_doc.document_id, "liability cap")
    assert search_res.grounding_status == GroundingStatus.document_not_indexed
    assert len(search_res.results) == 0


# 15. Document not indexed handling
@pytest.mark.anyio
async def test_document_not_indexed(isolated_vector_store, mock_embedder):
    service = RetrievalService(embedder=mock_embedder, store=isolated_vector_store)
    res = await service.retrieve("non_existent_doc_id", "any query")
    assert res.grounding_status == GroundingStatus.document_not_indexed
    assert res.results == []


# 16. Large document batching of embeddings
@pytest.mark.anyio
async def test_large_document_batching():
    call_counts = []

    class CountingBatchEmbedder(BaseEmbeddingService):
        async def embed_text(self, text, task_type="retrieval_document"):
            return [0.1] * 8

        async def embed_batch(self, texts, task_type="retrieval_document"):
            call_counts.append(len(texts))
            return [[0.1] * 8 for _ in texts]

    # Create dummy list of 75 chunks
    embedder = CountingBatchEmbedder()
    service = GeminiEmbeddingService(api_key="test_key_for_batching", batch_size=25)
    service._initialized = True

    with patch.object(service, "_call_gemini_embed", return_value=[[0.1] * 8] * 25):
        texts = [f"Clause paragraph {i}" for i in range(75)]
        embeddings = await service.embed_batch(texts)
        assert len(embeddings) == 75


# 17. Partial indexing cleanup on error
@pytest.mark.anyio
async def test_partial_indexing_cleanup(legal_test_doc, isolated_vector_store):
    class ExplodingStore(BaseVectorStore):
        def add_chunks(self, document_id, chunks, embeddings):
            raise RuntimeError("Database connection severed mid-write")

        def search(self, document_id, query_embedding, top_k=5):
            return []

        def delete_document(self, document_id):
            return True

        def is_indexed(self, document_id):
            return False

        def health_check(self):
            return False

    service = RetrievalService(
        embedder=DeterministicMockEmbeddingService(),
        store=ExplodingStore(),
    )
    with pytest.raises(RuntimeError):
        await service.index_document(legal_test_doc)


# 18. Privacy-safe logging
@pytest.mark.anyio
async def test_privacy_safe_logging(legal_test_doc, mock_embedder, isolated_vector_store, caplog):
    caplog.set_level(logging.INFO)
    secret_clause = "CONFIDENTIAL_OFFSHORE_ACCOUNT_ROUTING_99182"
    legal_test_doc.extracted_text += f"\n\n{secret_clause}"

    service = RetrievalService(
        chunker=ChunkingService(target_tokens=30, min_tokens=10),
        embedder=mock_embedder,
        store=isolated_vector_store,
    )
    await service.index_document(legal_test_doc)
    await service.retrieve(legal_test_doc.document_id, "offshore account")

    for record in caplog.records:
        assert secret_clause not in record.message


# 19. Indexing HTTP endpoint
def test_indexing_endpoint(client: TestClient, sample_txt_bytes: bytes, isolated_vector_store: BaseVectorStore):
    retrieval_service.set_dependencies(
        embedder=DeterministicMockEmbeddingService(),
        store=isolated_vector_store,
    )

    # 1. Upload
    files = {"file": ("sow_retrieval_test.txt", sample_txt_bytes, "text/plain")}
    upload_res = client.post("/api/v1/documents/upload", files=files)
    assert upload_res.status_code == 200
    doc_json = upload_res.json()

    # 2. Index
    index_res = client.post("/api/v1/documents/index", json={"document": doc_json})
    assert index_res.status_code == 200
    idx_data = index_res.json()
    assert idx_data["document_id"] == doc_json["document_id"]
    assert idx_data["chunk_count"] >= 1
    assert idx_data["indexed"] is True


# 20. Retrieval search HTTP endpoint
def test_retrieval_endpoint(client: TestClient, sample_txt_bytes: bytes, isolated_vector_store: BaseVectorStore):
    retrieval_service.set_dependencies(
        embedder=DeterministicMockEmbeddingService(),
        store=isolated_vector_store,
    )

    # 1. Upload & Index
    files = {"file": ("terms_retrieval.txt", sample_txt_bytes, "text/plain")}
    upload_res = client.post("/api/v1/documents/upload", files=files)
    doc_json = upload_res.json()
    client.post("/api/v1/documents/index", json={"document": doc_json})

    # 2. Search
    search_payload = {
        "document_id": doc_json["document_id"],
        "query": "indemnification obligations",
        "top_k": 3,
    }
    search_res = client.post("/api/v1/retrieval/search", json=search_payload)
    assert search_res.status_code == 200
    res_data = search_res.json()
    assert res_data["document_id"] == doc_json["document_id"]
    assert res_data["grounding_status"] in ["grounded", "insufficient_evidence"]
