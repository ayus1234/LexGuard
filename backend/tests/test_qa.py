import pytest
import logging
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.main import app
    from app.schemas.qa import (
        DocumentAskRequest,
        DocumentAskResponse,
        GroundedCitation,
        GroundedAnswerTelemetry,
    )
    from app.schemas.retrieval import (
        RetrievalResult,
        RetrievalResultItem,
        GroundingStatus,
    )
    from app.services.qa_service import QAService, qa_service
    from app.services.retrieval_service import RetrievalService
    from app.services.gemini_service import BaseGeminiService
    from app.utils.file_validation import (
        DocumentNotIndexedException,
        GeminiServiceUnavailableException,
        GeminiQuotaExceededException,
    )
else:
    try:
        from backend.app.main import app
        from backend.app.schemas.qa import (
            DocumentAskRequest,
            DocumentAskResponse,
            GroundedCitation,
            GroundedAnswerTelemetry,
        )
        from backend.app.schemas.retrieval import (
            RetrievalResult,
            RetrievalResultItem,
            GroundingStatus,
        )
        from backend.app.services.qa_service import QAService, qa_service
        from backend.app.services.retrieval_service import RetrievalService
        from backend.app.services.gemini_service import BaseGeminiService
        from backend.app.utils.file_validation import (
            DocumentNotIndexedException,
            GeminiServiceUnavailableException,
            GeminiQuotaExceededException,
        )
    except ImportError:
        from app.main import app
        from app.schemas.qa import (
            DocumentAskRequest,
            DocumentAskResponse,
            GroundedCitation,
            GroundedAnswerTelemetry,
        )
        from app.schemas.retrieval import (
            RetrievalResult,
            RetrievalResultItem,
            GroundingStatus,
        )
        from app.services.qa_service import QAService, qa_service
        from app.services.retrieval_service import RetrievalService
        from app.services.gemini_service import BaseGeminiService
        from app.utils.file_validation import (
            DocumentNotIndexedException,
            GeminiServiceUnavailableException,
            GeminiQuotaExceededException,
        )


class MockGeminiQAService(BaseGeminiService):
    def __init__(self, response_dict: dict):
        self.response_dict = response_dict

    async def generate_structured_analysis(self, prompt: str, system_instruction: str) -> dict:
        return self.response_dict


class MockRetrievalService(RetrievalService):
    def __init__(self, indexed_docs: set, results_map: dict):
        self.indexed_docs = indexed_docs
        self.results_map = results_map

    def is_document_indexed(self, document_id: str) -> bool:
        return document_id in self.indexed_docs

    async def retrieve(self, document_id: str, query: str, top_k: int = 5) -> RetrievalResult:
        if document_id not in self.indexed_docs:
            return RetrievalResult(
                document_id=document_id,
                query=query,
                grounding_status=GroundingStatus.document_not_indexed,
                results=[],
            )
        return self.results_map.get(
            document_id,
            RetrievalResult(
                document_id=document_id,
                query=query,
                grounding_status=GroundingStatus.insufficient_evidence,
                results=[],
            ),
        )


@pytest.fixture
def mock_retrieval_results():
    chunk_1 = RetrievalResultItem(
        chunk_id="doc123_chk_0000",
        text="Section 9.2 Termination for Convenience: Either party may terminate this Agreement without cause upon ninety (90) days prior written notice.",
        similarity_score=0.88,
        document_id="doc_123",
        section="Section 9.2",
        page_start=11,
        page_end=11,
        character_start=480,
        character_end=620,
    )
    chunk_2 = RetrievalResultItem(
        chunk_id="doc123_chk_0001",
        text="Section 4.3 Fees: All prepaid annual subscription fees are non-refundable in the event of termination for convenience.",
        similarity_score=0.79,
        document_id="doc_123",
        section="Section 4.3",
        page_start=5,
        page_end=5,
        character_start=180,
        character_end=300,
    )
    return RetrievalResult(
        document_id="doc_123",
        query="What is the notice period for early termination?",
        grounding_status=GroundingStatus.grounded,
        results=[chunk_1, chunk_2],
    )


@pytest.fixture
def mock_gemini_qa_payload():
    return {
        "answer": "Under Section 9.2, either party may terminate the agreement for convenience by providing ninety (90) days prior written notice. However, Section 4.3 stipulates that prepaid fees are non-refundable.",
        "grounded": True,
        "confidence": "99.4%",
        "badges": ["§ 9.2 & § 4.3 Verified", "• 100% Grounded in Agreement Clauses"],
        "citations": [
            {
                "page": 11,
                "section": "Section 9.2",
                "section_title": "Termination for Convenience",
                "quoted_text": "Either party may terminate this Agreement without cause upon ninety (90) days prior written notice.",
                "chunk_id": "doc123_chk_0000",
            },
            {
                "page": 5,
                "section": "Section 4.3",
                "section_title": "Fees",
                "quoted_text": "All prepaid annual subscription fees are non-refundable",
                "chunk_id": "doc123_chk_0001",
            },
        ],
        "carve_out_matrix": [
            {
                "type": "standard",
                "title": "Non-Refundable Upfront Fees",
                "description": "Prepaid annual commitments are forfeited upon convenience termination.",
            }
        ],
        "strategic_consideration": "Consider negotiating pro-rata fee reimbursement if the vendor changes core features.",
        "review_recommended_notice": {
            "title": "Review Recommended: Non-Refundable Fee Forfeiture",
            "description": "Early termination does not trigger pro-rata refund of prepaid fees.",
            "anchor_link": "Page 11 • Section 9.2 ->",
        },
    }


# TEST 1: End-to-End Grounded Q&A Success with Citation Verification
@pytest.mark.anyio
async def test_ask_document_grounded_success(mock_retrieval_results, mock_gemini_qa_payload):
    retrieval_svc = MockRetrievalService(
        indexed_docs={"doc_123"},
        results_map={"doc_123": mock_retrieval_results},
    )
    gemini_svc = MockGeminiQAService(mock_gemini_qa_payload)
    qa_svc = QAService(retrieval_svc=retrieval_svc, gemini_svc=gemini_svc)

    req = DocumentAskRequest(
        document_id="doc_123",
        question="What is the notice period for early termination?",
        top_k=5,
    )
    resp = await qa_svc.ask_document(req)

    assert resp.document_id == "doc_123"
    assert resp.grounded is True
    assert "ninety (90) days" in resp.answer
    assert len(resp.citations) == 2
    assert resp.citations[0].verified is True
    assert resp.citations[0].page == 11
    assert resp.citations[1].verified is True
    assert len(resp.retrieved_sources) == 2
    assert resp.telemetry.retrieval_ms >= 0
    assert resp.telemetry.generation_ms >= 0


# TEST 2: Document Not Indexed raises Controlled Exception
@pytest.mark.anyio
async def test_ask_document_not_indexed():
    retrieval_svc = MockRetrievalService(indexed_docs=set(), results_map={})
    qa_svc = QAService(retrieval_svc=retrieval_svc)

    req = DocumentAskRequest(
        document_id="unindexed_doc_999",
        question="What is the liability cap?",
    )
    with pytest.raises(DocumentNotIndexedException) as exc_info:
        await qa_svc.ask_document(req)
    assert "not indexed" in str(exc_info.value).lower()


# TEST 3: Insufficient Evidence / Question Outside Document Returns Controlled No-Answer
@pytest.mark.anyio
async def test_ask_document_insufficient_evidence():
    empty_result = RetrievalResult(
        document_id="doc_123",
        query="What is the CEO's personal home address?",
        grounding_status=GroundingStatus.insufficient_evidence,
        results=[],
    )
    retrieval_svc = MockRetrievalService(
        indexed_docs={"doc_123"},
        results_map={"doc_123": empty_result},
    )
    # Gemini should NOT even be called if evidence is below threshold
    gemini_svc = MockGeminiQAService({"answer": "Should not be called"})
    qa_svc = QAService(retrieval_svc=retrieval_svc, gemini_svc=gemini_svc)

    req = DocumentAskRequest(
        document_id="doc_123",
        question="What is the CEO's personal home address?",
    )
    resp = await qa_svc.ask_document(req)

    assert resp.grounded is False
    assert "does not provide enough information" in resp.answer
    assert resp.confidence == "Insufficient Evidence"
    assert len(resp.citations) == 0


# TEST 4: Hallucinated Citations Are Rejected / Verified=False
@pytest.mark.anyio
async def test_citation_verification_rejects_hallucination(mock_retrieval_results):
    payload_with_hallucination = {
        "answer": "The agreement includes a $50,000,000 penalty clause.",
        "grounded": True,
        "confidence": "95.0%",
        "citations": [
            {
                "page": 1,
                "section": "Section 99.9",
                "quoted_text": "This text does not exist anywhere in the chunks.",
                "chunk_id": "doc123_chk_0000",
            }
        ],
    }
    retrieval_svc = MockRetrievalService(
        indexed_docs={"doc_123"},
        results_map={"doc_123": mock_retrieval_results},
    )
    gemini_svc = MockGeminiQAService(payload_with_hallucination)
    qa_svc = QAService(retrieval_svc=retrieval_svc, gemini_svc=gemini_svc)

    req = DocumentAskRequest(
        document_id="doc_123",
        question="What is the penalty?",
    )
    resp = await qa_svc.ask_document(req)

    assert len(resp.citations) == 1
    assert resp.citations[0].verified is False
    assert resp.citations[0].character_start is None
    # Grounding status downgraded because 0 citations verified
    assert resp.grounded is False


# TEST 5: Legal Safety Filter Neutralizes Definitive Conclusions
@pytest.mark.anyio
async def test_legal_safety_sanitization(mock_retrieval_results):
    payload_with_forbidden_claims = {
        "answer": "This is illegal under federal law, and you will win in arbitration because this clause is definitely invalid.",
        "grounded": True,
        "confidence": "99.0%",
        "citations": [],
    }
    retrieval_svc = MockRetrievalService(
        indexed_docs={"doc_123"},
        results_map={"doc_123": mock_retrieval_results},
    )
    gemini_svc = MockGeminiQAService(payload_with_forbidden_claims)
    qa_svc = QAService(retrieval_svc=retrieval_svc, gemini_svc=gemini_svc)

    req = DocumentAskRequest(
        document_id="doc_123",
        question="Is this enforceable?",
    )
    resp = await qa_svc.ask_document(req)

    assert "this is illegal" not in resp.answer.lower()
    assert "you will win" not in resp.answer.lower()
    assert "this clause is definitely invalid" not in resp.answer.lower()


# TEST 6: Multi-Turn Conversation History is Included in Prompt
@pytest.mark.anyio
async def test_conversation_history_continuity(mock_retrieval_results, mock_gemini_qa_payload):
    captured_prompt = None

    class CapturingGeminiService(BaseGeminiService):
        async def generate_structured_analysis(self, prompt: str, system_instruction: str) -> dict:
            nonlocal captured_prompt
            captured_prompt = prompt
            return mock_gemini_qa_payload

    retrieval_svc = MockRetrievalService(
        indexed_docs={"doc_123"},
        results_map={"doc_123": mock_retrieval_results},
    )
    qa_svc = QAService(retrieval_svc=retrieval_svc, gemini_svc=CapturingGeminiService())

    req = DocumentAskRequest(
        document_id="doc_123",
        question="Is that notice period mutual?",
        conversation_history=[
            {"role": "user", "content": "What is the termination notice period?"},
            {"role": "assistant", "content": "The notice period is 90 days under Section 9.2."},
        ],
    )
    await qa_svc.ask_document(req)

    assert captured_prompt is not None
    assert "What is the termination notice period?" in captured_prompt
    assert "PRIOR CONVERSATION CONTEXT" in captured_prompt


# TEST 7: Document Scoping Isolation - Document A Cannot Retrieve Document B
@pytest.mark.anyio
async def test_cross_document_isolation():
    chunk_a = RetrievalResultItem(
        chunk_id="docA_chk_0000",
        text="Agreement A confidential terms only.",
        similarity_score=0.90,
        document_id="doc_A",
        section="Section 1",
        page_start=1,
        page_end=1,
        character_start=0,
        character_end=35,
    )
    chunk_b = RetrievalResultItem(
        chunk_id="docB_chk_0000",
        text="Agreement B proprietary trade secrets.",
        similarity_score=0.92,
        document_id="doc_B",
        section="Section 1",
        page_start=1,
        page_end=1,
        character_start=0,
        character_end=38,
    )

    retrieval_svc = MockRetrievalService(
        indexed_docs={"doc_A", "doc_B"},
        results_map={
            "doc_A": RetrievalResult(
                document_id="doc_A",
                query="query",
                grounding_status=GroundingStatus.grounded,
                results=[chunk_a],
            ),
            "doc_B": RetrievalResult(
                document_id="doc_B",
                query="query",
                grounding_status=GroundingStatus.grounded,
                results=[chunk_b],
            ),
        },
    )
    gemini_svc = MockGeminiQAService({
        "answer": "Answer based on document A",
        "grounded": True,
        "confidence": "99%",
        "citations": [],
    })
    qa_svc = QAService(retrieval_svc=retrieval_svc, gemini_svc=gemini_svc)

    resp_a = await qa_svc.ask_document(DocumentAskRequest(document_id="doc_A", question="query"))
    for src in resp_a.retrieved_sources:
        assert "Agreement B" not in (src.text_snippet or "")
        assert src.chunk_id != "docB_chk_0000"


# TEST 8: Zero-Retention Privacy - Sensitive Text Not Emitted in Logger
@pytest.mark.anyio
async def test_privacy_zero_retention_logging(mock_retrieval_results, mock_gemini_qa_payload, caplog):
    retrieval_svc = MockRetrievalService(
        indexed_docs={"doc_123"},
        results_map={"doc_123": mock_retrieval_results},
    )
    gemini_svc = MockGeminiQAService(mock_gemini_qa_payload)
    qa_svc = QAService(retrieval_svc=retrieval_svc, gemini_svc=gemini_svc)

    with caplog.at_level(logging.INFO):
        req = DocumentAskRequest(
            document_id="doc_123",
            question="SECRET_CONFIDENTIAL_USER_QUERY_TEXT_NEVER_LOG",
        )
        await qa_svc.ask_document(req)

    logged_output = " ".join([r.message for r in caplog.records])
    assert "SECRET_CONFIDENTIAL_USER_QUERY_TEXT_NEVER_LOG" not in logged_output
    assert "All prepaid annual subscription fees are non-refundable" not in logged_output


# TEST 9: FastAPI Endpoint POST /api/v1/documents/ask Integration
def test_api_ask_endpoint_integration(client: TestClient):
    chunk = RetrievalResultItem(
        chunk_id="chk_integration_01",
        text="This agreement is governed by the laws of the State of Delaware.",
        similarity_score=0.92,
        document_id="doc_test_12345",
        section="§ 18.1 Governing Law",
        page_start=17,
        page_end=17,
        character_start=0,
        character_end=64,
    )
    retrieval_svc = MockRetrievalService(
        indexed_docs={"doc_test_12345"},
        results_map={
            "doc_test_12345": RetrievalResult(
                document_id="doc_test_12345",
                query="What is the governing law?",
                grounding_status=GroundingStatus.grounded,
                results=[chunk],
            )
        },
    )
    gemini_svc = MockGeminiQAService({
        "answer": "This agreement is governed by Delaware law.",
        "citations": [
            {
                "page": 17,
                "section": "18.1",
                "quoted_text": "This agreement is governed by the laws of the State of Delaware.",
                "verified": True,
            }
        ],
        "confidence": "99.2%",
        "badges": ["• Grounded in Section 18.1"],
    })
    qa_service.set_dependencies(retrieval_svc=retrieval_svc, gemini_svc=gemini_svc)

    payload = {
        "document_id": "doc_test_12345",
        "question": "What is the governing law?",
        "top_k": 3,
    }
    resp = client.post("/api/v1/documents/ask", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["document_id"] == "doc_test_12345"
    assert data["grounded"] is True
    assert "Delaware" in data["answer"]
    assert len(data["citations"]) == 1
    assert data["citations"][0]["verified"] is True


# TEST 10: Validation Rejection for Empty Question
def test_api_ask_endpoint_empty_question(client: TestClient):
    payload = {
        "document_id": "doc_test_12345",
        "question": " ",  # whitespace only
    }
    resp = client.post("/api/v1/documents/ask", json=payload)
    # FastAPI returns 422 for pydantic min_length / validation error
    assert resp.status_code == 422
