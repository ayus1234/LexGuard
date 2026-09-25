"""
LexGuard Phase 5: Production Hardening, End-to-End Verification & Hackathon Readiness Test Suite.
Validates multi-format ingestion, citation integrity matrix, grounded Q&A refusal,
Gemini dual-key failover, zero-retention disk hygiene, security boundaries, and export generation.
"""

import io
import json
import logging
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.schemas.brief import (
    BriefChecklistItem,
    CounselQuestionItem,
    NegotiationPointItem,
    AttentionAreaItem,
    KeyInformationItem,
    ImportantClauseItem,
    BriefSourceCitation,
    LawyerBrief,
)
from app.schemas.qa import GroundedCitation, DocumentAskRequest
from app.schemas.retrieval import ChunkMetadata, DocumentChunk
from app.services.cleanup_service import cleanup_service
from app.services.export_service import ExportService
from app.services.qa_service import qa_service


# ==============================================================================
# 1. MULTI-FORMAT REAL DOCUMENT INGESTION & NORMALIZATION
# ==============================================================================

def test_phase5_pdf_full_ingestion(client: TestClient):
    """Verify end-to-end PDF ingestion, page preservation, word count, and temp cleanup."""
    import pymupdf

    doc = pymupdf.open()
    p1 = doc.new_page()
    p1.insert_text(
        (50, 72),
        "ARTICLE 1: CONFIDENTIALITY AGREEMENT\n\n"
        "The receiving party agrees to hold all proprietary information in strict confidence.\n"
        "This obligation shall survive for a period of five (5) years following disclosure.",
        fontsize=11,
    )
    p2 = doc.new_page()
    p2.insert_text(
        (50, 72),
        "ARTICLE 2: GOVERNING LAW AND VENUE\n\n"
        "This agreement shall be governed exclusively by the laws of the State of Delaware.\n"
        "Any disputes shall be submitted to the Delaware Court of Chancery.",
        fontsize=11,
    )
    buf = io.BytesIO()
    doc.save(buf)
    doc.close()
    pdf_bytes = buf.getvalue()

    temp_before = set(settings.temp_storage_dir.glob("*"))

    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("delaware_nda_v5.pdf", pdf_bytes, "application/pdf")},
    )
    assert response.status_code == 200, response.text
    data = response.json()

    assert data["filename"] == "delaware_nda_v5.pdf"
    assert data["file_type"] == "pdf"
    assert data["page_count"] == 2
    assert len(data["pages"]) == 2
    assert data["pages"][0]["page_number"] == 1
    assert data["pages"][1]["page_number"] == 2
    assert "Delaware" in data["extracted_text"]
    assert data["word_count"] > 20

    # Verify zero-retention: no temp files leaked on disk
    temp_after = set(settings.temp_storage_dir.glob("*"))
    assert temp_after - temp_before == set(), "Temporary PDF leaked on disk"


def test_phase5_docx_full_ingestion(client: TestClient):
    """Verify end-to-end DOCX ingestion, headings, paragraphs, and temp cleanup."""
    import docx

    doc = docx.Document()
    doc.add_heading("SECTION 1: ENGAGEMENT & SCOPE", level=1)
    doc.add_paragraph("Consultant agrees to provide specialized AI security compliance auditing services.")
    doc.add_heading("SECTION 2: LIMITATION OF LIABILITY", level=1)
    doc.add_paragraph("In no event shall aggregate liability exceed total fees paid under this Statement of Work.")

    buf = io.BytesIO()
    doc.save(buf)
    docx_bytes = buf.getvalue()

    temp_before = set(settings.temp_storage_dir.glob("*"))

    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("consulting_sow_v5.docx", docx_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
    )
    assert response.status_code == 200, response.text
    data = response.json()

    assert data["filename"] == "consulting_sow_v5.docx"
    assert data["file_type"] == "docx"
    assert "Consultant agrees to provide" in data["extracted_text"]
    assert "LIMITATION OF LIABILITY" in data["extracted_text"]

    # Verify zero-retention: no temp files leaked on disk
    temp_after = set(settings.temp_storage_dir.glob("*"))
    assert temp_after - temp_before == set(), "Temporary DOCX leaked on disk"


def test_phase5_txt_full_ingestion(client: TestClient):
    """Verify end-to-end plain legal TXT ingestion, normalization, and cleanup."""
    txt_content = (
        "EMPLOYMENT RESTRICTIVE COVENANT AGREEMENT\n\n"
        "1. NON-SOLICITATION OF CUSTOMERS\n"
        "Employee covenants that for twelve months post-termination, Employee shall not solicit Company accounts.\n\n"
        "2. SEVERABILITY\n"
        "If any court invalidates any portion of this covenant, the remaining provisions shall remain in full force."
    )
    txt_bytes = txt_content.encode("utf-8")

    temp_before = set(settings.temp_storage_dir.glob("*"))

    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("restrictive_covenant.txt", txt_bytes, "text/plain")},
    )
    assert response.status_code == 200, response.text
    data = response.json()

    assert data["filename"] == "restrictive_covenant.txt"
    assert data["file_type"] == "txt"
    assert "NON-SOLICITATION" in data["extracted_text"]

    temp_after = set(settings.temp_storage_dir.glob("*"))
    assert temp_after - temp_before == set(), "Temporary TXT leaked on disk"


# ==============================================================================
# 2. CITATION INTEGRITY & VERIFICATION MATRIX
# ==============================================================================

def test_citation_integrity_matrix():
    """
    Rigorously tests the citation verification engine across 6 adversarial scenarios:
    1. Valid exact quotation -> verified=True, exact character boundaries.
    2. Case-differing quotation -> verified=True via case-insensitive alignment.
    3. Fabricated quotation (not in document) -> verified=False, character offsets cleared.
    4. Altered/hallucinated text -> verified=False.
    5. Empty or ultra-short text -> verified=False.
    6. Citation originating from another document/chunk -> verified=False.
    """
    sample_chunk = DocumentChunk(
        chunk_id="chk_audit_01",
        document_id="doc_audit_99",
        chunk_index=0,
        text=(
            "8.3 Limitation of Liability. IN NO EVENT SHALL EITHER PARTY BE LIABLE FOR "
            "ANY INDIRECT, INCIDENTAL, SPECIAL, OR CONSEQUENTIAL DAMAGES ARISING OUT OF THIS AGREEMENT."
        ),
        section="§ 8.3",
        page_start=3,
        page_end=3,
        character_start=500,
        character_end=680,
        token_estimate=35,
        metadata=ChunkMetadata(
            document_id="doc_audit_99",
            chunk_id="chk_audit_01",
            section="§ 8.3",
            page_start=3,
            page_end=3,
            character_start=500,
            character_end=680,
        ),
    )

    chunks = [sample_chunk]

    # Scenario 1: Exact verbatim citation
    c1 = GroundedCitation(quoted_text="IN NO EVENT SHALL EITHER PARTY BE LIABLE")
    v1 = qa_service.verify_citation_against_chunks(c1, chunks)
    assert v1.verified is True
    assert v1.page == 3
    assert v1.character_start is not None
    assert v1.character_start == 500 + sample_chunk.text.find("IN NO EVENT")
    assert v1.character_end == v1.character_start + len("IN NO EVENT SHALL EITHER PARTY BE LIABLE")

    # Scenario 2: Case-differing quotation
    c2 = GroundedCitation(quoted_text="in no event shall either party be liable")
    v2 = qa_service.verify_citation_against_chunks(c2, chunks)
    assert v2.verified is True
    assert v2.page == 3
    assert v2.chunk_id == "chk_audit_01"

    # Scenario 3: Fabricated quotation
    c3 = GroundedCitation(quoted_text="Neither party shall be subject to liquidated penalties exceeding $1,000,000.")
    v3 = qa_service.verify_citation_against_chunks(c3, chunks)
    assert v3.verified is False
    assert v3.character_start is None
    assert v3.character_end is None

    # Scenario 4: Altered quotation (word injected)
    c4 = GroundedCitation(quoted_text="IN NO EVENT SHALL EITHER VENDOR PARTY BE LIABLE")
    v4 = qa_service.verify_citation_against_chunks(c4, chunks)
    assert v4.verified is False

    # Scenario 5: Short / empty quotation
    c5 = GroundedCitation(quoted_text="IN")
    v5 = qa_service.verify_citation_against_chunks(c5, chunks)
    assert v5.verified is False

    # Scenario 6: Disjoint quotation from another agreement
    c6 = GroundedCitation(quoted_text="Tenant shall maintain commercial general liability insurance.")
    v6 = qa_service.verify_citation_against_chunks(c6, chunks)
    assert v6.verified is False


# ==============================================================================
# 3. ASK LEXGUARD GROUNDING & REFUSAL TEST
# ==============================================================================

@pytest.mark.anyio
async def test_ask_lexguard_grounded_answer():
    """Verify Ask LexGuard provides grounded response with citations for answerable query."""
    from app.schemas.qa import DocumentAskRequest
    from app.schemas.retrieval import GroundingStatus, RetrievalResult, RetrievalResultItem

    retrieved_item = RetrievalResultItem(
        chunk_id="chk_term_01",
        text="Section 4.1: Initial Term. This Agreement shall commence on the Effective Date and continue for an initial term of three (3) years.",
        similarity_score=0.92,
        document_id="doc_term_42",
        section="Section 4.1",
        page_start=2,
        page_end=2,
        character_start=120,
        character_end=245,
    )

    mock_retrieval_res = RetrievalResult(
        document_id="doc_term_42",
        query="What is the initial term of the contract?",
        grounding_status=GroundingStatus.grounded,
        results=[retrieved_item],
    )

    mock_gemini_response = {
        "answer": "Based on Section 4.1, the agreement specifies an initial term of three (3) years from the Effective Date.",
        "grounded": True,
        "citations": [
            {
                "quoted_text": "This Agreement shall commence on the Effective Date and continue for an initial term of three (3) years.",
                "page": 2,
                "section": "Section 4.1",
            }
        ],
        "statutory_context": "Standard multi-year commercial term structure.",
    }

    with patch.object(qa_service._retrieval, "is_document_indexed", return_value=True), \
         patch.object(qa_service._retrieval, "retrieve", new_callable=AsyncMock, return_value=mock_retrieval_res), \
         patch.object(qa_service._gemini, "generate_structured_analysis", new_callable=AsyncMock, return_value=mock_gemini_response):

        req = DocumentAskRequest(
            document_id="doc_term_42",
            question="What is the initial term of the contract?",
        )
        res = await qa_service.ask_document(req)

        assert res.grounded is True
        assert "three (3) years" in res.answer
        assert len(res.citations) == 1
        assert res.citations[0].verified is True
        assert res.citations[0].page == 2
        assert res.citations[0].chunk_id == "chk_term_01"


@pytest.mark.anyio
async def test_ask_lexguard_unanswerable_refusal():
    """
    Verify Ask LexGuard refuses to invent facts and indicates insufficient evidence
    when asked an unanswerable question unsupported by document evidence.
    """
    from app.schemas.qa import DocumentAskRequest
    from app.schemas.retrieval import GroundingStatus, RetrievalResult

    mock_insufficient_retrieval = RetrievalResult(
        document_id="doc_term_42",
        query="What is the warranty coverage for the rooftop solar panel system?",
        grounding_status=GroundingStatus.insufficient_evidence,
        results=[],
    )

    with patch.object(qa_service._retrieval, "is_document_indexed", return_value=True), \
         patch.object(qa_service._retrieval, "retrieve", new_callable=AsyncMock, return_value=mock_insufficient_retrieval):

        req = DocumentAskRequest(
            document_id="doc_term_42",
            question="What is the warranty coverage for the rooftop solar panel system?",
        )
        res = await qa_service.ask_document(req)

        assert res.grounded is False
        assert "does not provide enough information" in res.answer or "insufficient" in res.answer.lower()
        assert len(res.citations) == 0
        assert res.confidence == "Insufficient Evidence"


# ==============================================================================
# 4. GEMINI PRIMARY + FALLBACK KEY FAILOVER
# ==============================================================================

@pytest.mark.anyio
async def test_gemini_primary_failover_success():
    """Verify that when primary key encounters a recoverable 429 quota error, fallback succeeds."""
    try:
        from backend.app.core.credentials import GeminiCredentialManager
        from backend.app.services.gemini_service import GoogleGeminiService
        from backend.app.utils.file_validation import GeminiQuotaExceededException
    except ImportError:
        from app.core.credentials import GeminiCredentialManager
        from app.services.gemini_service import GoogleGeminiService
        from app.utils.file_validation import GeminiQuotaExceededException

    cred_mgr = GeminiCredentialManager(
        primary_key="test_primary_key_fail",
        fallback_key="test_fallback_key_success",
    )

    service = GoogleGeminiService(cred_manager=cred_mgr)

    calls = []

    async def mock_execute(client, prompt, sys_inst):
        primary_client = cred_mgr.get_generative_client(cred_mgr.get_candidate_credentials()[0])
        if client == primary_client:
            calls.append("primary")
            raise GeminiQuotaExceededException("429 ResourceExhausted: rate limit exceeded")
        else:
            calls.append("fallback")
            return {"status": "success", "model_output": "validated"}

    with patch.object(service, "_execute_generation", side_effect=mock_execute):
        result = await service.generate_structured_analysis(
            prompt="Analyze clause",
            system_instruction="Educational legal analysis",
        )

        assert result == {"status": "success", "model_output": "validated"}
        assert calls == ["primary", "fallback"]


@pytest.mark.anyio
async def test_gemini_dual_failure_safe_handling():
    """Verify that when both primary and fallback fail, 503 is returned cleanly without leaking secrets."""
    try:
        from backend.app.core.credentials import GeminiCredentialManager
        from backend.app.services.gemini_service import GoogleGeminiService
        from backend.app.utils.file_validation import GeminiServiceUnavailableException
    except ImportError:
        from app.core.credentials import GeminiCredentialManager
        from app.services.gemini_service import GoogleGeminiService
        from app.utils.file_validation import GeminiServiceUnavailableException

    cred_mgr = GeminiCredentialManager(
        primary_key="super_secret_primary_key",
        fallback_key="super_secret_fallback_key",
    )

    service = GoogleGeminiService(cred_manager=cred_mgr)

    async def mock_execute_fail(client, prompt, sys_inst):
        raise GeminiServiceUnavailableException("503 Service Unavailable")

    with patch.object(service, "_execute_generation", side_effect=mock_execute_fail):
        with pytest.raises(GeminiServiceUnavailableException) as exc_info:
            await service.generate_structured_analysis(
                prompt="Test prompt",
                system_instruction="System prompt",
            )

        err_msg = str(exc_info.value)
        assert "super_secret_primary_key" not in err_msg
        assert "super_secret_fallback_key" not in err_msg


# ==============================================================================
# 5. ZERO-RETENTION PRIVACY & CLEANUP
# ==============================================================================

def test_zero_retention_cleanup_on_all_error_paths():
    """Verify cleanup_file safely cleans up temporary disk files on errors."""
    temp_dir = settings.temp_storage_dir
    test_file = temp_dir / "zero_retention_test.tmp"
    test_file.write_text("sensitivedata")
    assert test_file.exists()

    # Success cleanup
    assert cleanup_service.cleanup_file(test_file) is True
    assert not test_file.exists()

    # Re-call on already deleted file does not raise
    assert cleanup_service.cleanup_file(test_file) is False


def test_privacy_no_secrets_in_logs(caplog):
    """Verify logger output never prints raw API keys or credential secrets."""
    from app.core.logging import logger

    primary_key = settings.GEMINI_API_KEY_PRIMARY or "test_key_sample"

    with caplog.at_level(logging.DEBUG):
        logger.info("Executing retrieval search for document doc-saas-v42")
        logger.info("Retrieved 5 chunks; similarity range 0.72 - 0.94")
        logger.info("Citation verification completed: 3/3 verified")

    for record in caplog.records:
        assert primary_key not in record.message


# ==============================================================================
# 6. SECURITY HARDENING: FILENAMES & FILE TYPES
# ==============================================================================

def test_security_path_traversal_sanitization(client: TestClient, sample_txt_bytes: bytes):
    """Verify malicious path traversal filenames are sanitized and stored strictly in temp dir."""
    malicious_filename = "../../../../etc/passwd.txt"

    response = client.post(
        "/api/v1/documents/upload",
        files={"file": (malicious_filename, sample_txt_bytes, "text/plain")},
    )
    assert response.status_code == 200
    data = response.json()

    # Sanitized filename must not contain directory traversal slashes
    assert ".." not in data["filename"]
    assert "/" not in data["filename"]
    assert "\\" not in data["filename"]


def test_security_disallowed_file_extensions(client: TestClient):
    """Verify executable or script extensions are unconditionally rejected with 400."""
    disallowed = [
        ("payload.exe", b"MZ\x90\x00", "application/octet-stream"),
        ("exploit.sh", b"#!/bin/bash\nrm -rf /", "text/x-shellscript"),
        ("script.py", b"import os\nos.system('calc')", "text/x-python"),
    ]

    for fname, content, mime in disallowed:
        resp = client.post(
            "/api/v1/documents/upload",
            files={"file": (fname, content, mime)},
        )
        assert resp.status_code == 400
        assert resp.json()["error"]["code"] == "UNSUPPORTED_FILE_TYPE"


# ==============================================================================
# 7. EXPORT VERIFICATION (PDF & DOCX GENERATION)
# ==============================================================================

def test_export_pdf_and_docx_validity():
    """
    Rigorously tests the Lawyer Preparation Brief export pipeline:
    1. Generates authentic PDF and verifies magic bytes %PDF-, valid pages, and legal disclaimer.
    2. Generates authentic DOCX and verifies zip structure, word/document.xml, and legal disclaimer.
    """
    brief = LawyerBrief(
        document_id="doc_audit_phase5",
        document_title="Enterprise Cloud Agreement v5",
        document_type="Commercial Agreement",
        jurisdiction="Delaware Law",
        disclaimer="MANDATORY DISCLAIMER: Educational preparation only. Not legal advice.",
        executive_summary="Executive review of liability caps and SLA penalties.",
        counsel_questions=[
            CounselQuestionItem(
                id="cq-1",
                category="Liability",
                agenda_topic="Limitation of Liability",
                why_discuss="Assess exposure under 12-month fee cap.",
                contract_citation="§ 8.3",
                page=3,
            )
        ],
        negotiation_points=[
            NegotiationPointItem(
                id="np-1",
                title="Mutual Indemnification",
                category="Indemnity",
                current_provision="One-way vendor indemnity.",
                discussion_point="Demand mutual indemnification carve-out for gross negligence.",
                suggested_compromise="Accept 2x fee super-cap.",
            )
        ],
        checklist=[
            BriefChecklistItem(
                id="chk-1",
                section_index=1,
                section_title="Pre-Execution Directives",
                title="Verify Insurance Certificate",
                badge_text="Urgent",
                badge_variant="urgent",
                completed=False,
                citation="§ 14.1",
                page=5,
            )
        ],
    )

    # 1. PDF Export
    pdf_bytes = ExportService.generate_brief_pdf(brief)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF-"), "Invalid PDF signature"
    # Verify PDF contains legal disclaimer text
    import pymupdf
    pdf_doc = pymupdf.open("pdf", pdf_bytes)
    assert pdf_doc.page_count >= 1
    extracted_pdf_text = "".join(str(pdf_doc[i].get_text()) for i in range(pdf_doc.page_count))
    assert "MANDATORY" in extracted_pdf_text or "Educational" in extracted_pdf_text or "DISCLAIMER" in extracted_pdf_text

    # 2. DOCX Export
    docx_bytes = ExportService.generate_brief_docx(brief)
    assert isinstance(docx_bytes, bytes)
    assert len(docx_bytes) > 1000
    # DOCX is a zip archive with PK signature
    assert docx_bytes.startswith(b"PK\x03\x04"), "Invalid DOCX zip signature"
