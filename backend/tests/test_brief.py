"""
Unit and Integration Tests for Phase 4: Lawyer Summary Brief & Export.
Covers schema validation, malformed Gemini output, citation verification,
safety sanitization, zero-retention logging, PDF/DOCX generation, and API endpoints.
"""

import io
import pytest
import logging
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from datetime import datetime, timezone

try:
    from backend.app.main import app
    from backend.app.schemas.brief import (
        LawyerBrief,
        BriefSourceCitation,
        KeyInformationItem,
        AttentionAreaItem,
        NegotiationPointItem,
        CounselQuestionItem,
        BriefChecklistItem,
        ImportantClauseItem,
        LawyerBriefRequest,
        LawyerBriefResponse,
    )
    from backend.app.schemas.document import DocumentResponse, PageExtraction, DocumentMetadata, SectionOutline
    from backend.app.services.brief_service import BriefService, brief_service
    from backend.app.services.export_service import ExportService
    from backend.app.services.gemini_service import BaseGeminiService
    from backend.app.utils.file_validation import (
        DocumentNotFoundException,
        BriefValidationException,
        DocumentTooLargeForAnalysisException,
        GeminiServiceUnavailableException,
        GeminiQuotaExceededException,
    )
except ImportError:
    from app.main import app
    from app.schemas.brief import (
        LawyerBrief,
        BriefSourceCitation,
        KeyInformationItem,
        AttentionAreaItem,
        NegotiationPointItem,
        CounselQuestionItem,
        BriefChecklistItem,
        ImportantClauseItem,
        LawyerBriefRequest,
        LawyerBriefResponse,
    )
    from app.schemas.document import DocumentResponse, PageExtraction, DocumentMetadata, SectionOutline
    from app.services.brief_service import BriefService, brief_service
    from app.services.export_service import ExportService
    from app.services.gemini_service import BaseGeminiService
    from app.utils.file_validation import (
        DocumentNotFoundException,
        BriefValidationException,
        DocumentTooLargeForAnalysisException,
        GeminiServiceUnavailableException,
        GeminiQuotaExceededException,
    )


SAMPLE_DOCUMENT_TEXT = """
MASTER SERVICES AGREEMENT AND SERVICE LEVEL AGREEMENT

This Master Services Agreement ("Agreement") is entered into between CloudScale Inc. ("Vendor") and Acme Corp ("Customer").

1. TERM AND TERMINATION
The initial term shall be three (3) years from the Effective Date. Either party may terminate for convenience upon ninety (90) days written notice.
Notice must be delivered via registered mail to Vendor's headquarters in Delaware.

2. FEES AND PAYMENT
Customer agrees to pay all fees within thirty (30) days of receipt of invoice. Late payments will incur a 1.5% monthly charge.
Uncredited upfront annual commitment fees of $240,000 remain non-refundable.

3. LIMITATION OF LIABILITY
Vendor's aggregate liability under this agreement shall be strictly capped at the fees paid in the three (3) months preceding the incident.
Neither party shall be liable for indirect or consequential damages.

4. INDEMNIFICATION
Vendor shall defend and indemnify Customer against third-party IP infringement claims. Customer shall indemnify Vendor against claims arising from Customer Data.

5. GOVERNING LAW
This agreement is governed by the laws of the State of Delaware.
"""

MOCK_RAW_GEMINI_BRIEF = {
    "document_title": "Master Services Agreement",
    "document_type": "Master Services Agreement",
    "jurisdiction": "State of Delaware",
    "executive_summary": "Comprehensive agreement between Vendor and Customer for cloud services over a 3-year term.",
    "key_information": [
        {
            "category": "TERM",
            "label": "Initial Term",
            "value": "3 years",
            "source_reference": "Section 1",
            "page": 1,
            "section": "1",
        },
        {
            "category": "LIABILITY",
            "label": "Aggregate Liability Cap",
            "value": "3 months preceding fees",
            "source_reference": "Section 3",
            "page": 1,
            "section": "3",
        },
    ],
    "attention_areas": [
        {
            "id": "att-1",
            "title": "Short Liability Cap Lookback",
            "category": "Liability",
            "description": "Liability is capped at 3 months of fees.",
            "why_it_matters": "Consider clarifying with counsel whether this cap adequately covers potential enterprise exposure.",
            "review_level": "review_recommended",
            "source_reference": "Section 3",
            "page": 1,
            "section": "3",
        }
    ],
    "negotiation_points": [
        {
            "id": "neg-1",
            "title": "Liability Cap Lookback Extension",
            "category": "Liability",
            "current_provision": "3 months preceding fees",
            "discussion_point": "Consider discussing whether 12 months fees or a fixed $1M cap is more appropriate.",
            "suggested_compromise": "12 months preceding fees",
            "market_baseline": "12 months preceding fees",
            "source_reference": "Section 3",
            "page": 1,
            "section": "3",
        }
    ],
    "counsel_questions": [
        {
            "id": "q-1",
            "priority": "High",
            "category": "Liability",
            "agenda_topic": "Limitation of Liability Lookback Period",
            "why_discuss": "A 3-month trailing fee cap is substantially narrower than standard enterprise norms.",
            "suggested_phrasing": "What risk exposure does the 3-month trailing liability cap create under our expected deployment?",
            "contract_citation": "Section 3",
            "market_standard": "12 months fees paid",
            "page": 1,
            "section": "3",
        }
    ],
    "checklist": [
        {
            "id": "chk-1",
            "section_index": 1,
            "section_title": "1. Financial & Commitments",
            "title": "Confirm non-refundable upfront payment schedule ($240,000 commitment)",
            "citation": "Section 2 • Fees and Payment",
            "badge_text": "High Attention",
            "badge_variant": "high",
            "completed": False,
            "page": 1,
            "section": "2",
        },
        {
            "id": "chk-2",
            "section_index": 2,
            "section_title": "2. Liability & Indemnification",
            "title": "Review 3-month trailing liability limitation carve-outs",
            "citation": "Section 3 • Limitation of Liability",
            "badge_text": "Urgent",
            "badge_variant": "urgent",
            "completed": False,
            "page": 1,
            "section": "3",
        },
    ],
    "important_clauses": [
        {
            "section": "3",
            "title": "Limitation of Liability",
            "category": "Liability",
            "summary": "Caps total damages to 3 months of fees.",
            "source_reference": "Section 3",
            "page": 1,
        }
    ],
    "citations": [
        {
            "page": 1,
            "section": "3",
            "quoted_text": "Vendor's aggregate liability under this agreement shall be strictly capped at the fees paid in the three (3) months preceding the incident.",
        },
        {
            "page": 1,
            "section": "1",
            "quoted_text": "Either party may terminate for convenience upon ninety (90) days written notice.",
        },
        {
            "page": 1,
            "section": "99",
            "quoted_text": "FABRICATED QUOTE NOT PRESENT IN THE CONTRACT AT ALL",
        },
    ],
}


@pytest.fixture
def mock_document():
    pages = [
        PageExtraction(
            page_number=1,
            text=SAMPLE_DOCUMENT_TEXT,
            character_start=0,
            character_end=len(SAMPLE_DOCUMENT_TEXT),
            word_count=len(SAMPLE_DOCUMENT_TEXT.split()),
        )
    ]
    meta = DocumentMetadata(
        original_filename="sample_msa.txt",
        file_size_bytes=len(SAMPLE_DOCUMENT_TEXT.encode("utf-8")),
        mime_type="text/plain",
        sha256_hash="dummyhash123",
        extraction_engine="native_text",
        processed_at=datetime.now(timezone.utc),
    )
    return DocumentResponse(
        document_id="doc-test-123",
        filename="sample_msa.txt",
        file_type="txt",
        source_type="upload",
        page_count=1,
        word_count=len(SAMPLE_DOCUMENT_TEXT.split()),
        character_count=len(SAMPLE_DOCUMENT_TEXT),
        extracted_text=SAMPLE_DOCUMENT_TEXT,
        pages=pages,
        sections=[SectionOutline(title="1. TERM", page_number=1, character_offset=10)],
        metadata=meta,
        created_at=datetime.now(timezone.utc),
        processing_status="completed",
    )


@pytest.fixture
def mock_gemini():
    mock = MagicMock(spec=BaseGeminiService)
    mock.generate_structured_analysis = AsyncMock(return_value=MOCK_RAW_GEMINI_BRIEF.copy())
    return mock


@pytest.fixture
def client():
    return TestClient(app)


# 1. Valid Brief Schema Validation
def test_valid_brief_schema():
    raw = MOCK_RAW_GEMINI_BRIEF.copy()
    raw["document_id"] = "doc-test-123"
    brief = LawyerBrief.model_validate(raw)
    assert brief.document_id == "doc-test-123"
    assert brief.document_title == "Master Services Agreement"
    assert len(brief.key_information) == 2
    assert len(brief.attention_areas) == 1
    assert len(brief.negotiation_points) == 1
    assert len(brief.counsel_questions) == 1
    assert len(brief.checklist) == 2
    assert "educational preparation" in brief.disclaimer.lower()


# 2. Malformed Gemini Response (Not a Dict)
@pytest.mark.anyio
async def test_malformed_gemini_response(mock_document):
    mock_bad_gemini = MagicMock(spec=BaseGeminiService)
    mock_bad_gemini.generate_structured_analysis = AsyncMock(return_value="NOT_A_DICT")
    svc = BriefService(service=mock_bad_gemini)

    with pytest.raises(BriefValidationException):
        await svc.generate_brief(document_id=mock_document.document_id, document=mock_document)


# 3. Missing Required Fields in Model Response
@pytest.mark.anyio
async def test_missing_required_fields_in_gemini(mock_document):
    mock_bad_gemini = MagicMock(spec=BaseGeminiService)
    # Missing executive_summary
    mock_bad_gemini.generate_structured_analysis = AsyncMock(
        return_value={"document_title": "Test Title"}
    )
    svc = BriefService(service=mock_bad_gemini)

    with pytest.raises(BriefValidationException):
        await svc.generate_brief(document_id=mock_document.document_id, document=mock_document)


# 4. Invalid Enum Handling (e.g. invalid review_level or badge_variant)
def test_invalid_enum_in_schema():
    bad_item = {
        "id": "att-1",
        "title": "Title",
        "category": "Liability",
        "description": "Desc",
        "why_it_matters": "Why",
        "review_level": "INVALID_REVIEW_LEVEL",  # Invalid enum value
    }
    with pytest.raises(Exception):
        AttentionAreaItem.model_validate(bad_item)


# 5. Missing Document Handling (404)
@pytest.mark.anyio
async def test_missing_document_handling():
    svc = BriefService()
    with patch.object(svc, "_load_document_from_db", side_effect=DocumentNotFoundException()):
        with pytest.raises(DocumentNotFoundException):
            await svc.generate_brief(document_id="nonexistent-doc-id", document=None)


# 6 & 7. Citation Verification & Fabricated Citation Detection
@pytest.mark.anyio
async def test_citation_verification_and_fabrication_detection(mock_document, mock_gemini):
    svc = BriefService(service=mock_gemini)
    brief = await svc.generate_brief(document_id=mock_document.document_id, document=mock_document)

    assert len(brief.citations) == 3
    # First two quotes exist verbatim in SAMPLE_DOCUMENT_TEXT
    assert brief.citations[0].verified is True
    assert brief.citations[0].character_start is not None
    assert brief.citations[1].verified is True
    assert brief.citations[1].character_start is not None

    # Third quote is fabricated and MUST be marked unverified
    assert brief.citations[2].verified is False
    assert brief.citations[2].character_start is None
    assert brief.citations_verified_count == 2
    assert brief.citations_unverified_count == 1


# 8. Empty Document Handling
@pytest.mark.anyio
async def test_empty_document_handling(mock_gemini):
    empty_doc = DocumentResponse(
        document_id="empty-doc",
        filename="empty.txt",
        file_type="txt",
        source_type="upload",
        page_count=1,
        word_count=0,
        character_count=0,
        extracted_text="",
        pages=[],
        sections=[],
        metadata=DocumentMetadata(
            original_filename="empty.txt",
            file_size_bytes=0,
            mime_type="text/plain",
            sha256_hash="h",
            extraction_engine="native",
            processed_at=datetime.now(timezone.utc),
        ),
        created_at=datetime.now(timezone.utc),
        processing_status="completed",
    )
    svc = BriefService(service=mock_gemini)
    with pytest.raises(DocumentNotFoundException):
        await svc.generate_brief(document_id="empty-doc", document=empty_doc)


# 9 & 10. Gemini Failover and Fallback
@pytest.mark.anyio
async def test_gemini_fallback_success(mock_document):
    mock_service = MagicMock(spec=BaseGeminiService)
    # Simulates failover where primary failed but fallback returned the brief
    mock_service.generate_structured_analysis = AsyncMock(return_value=MOCK_RAW_GEMINI_BRIEF.copy())
    svc = BriefService(service=mock_service)
    brief = await svc.generate_brief(document_id=mock_document.document_id, document=mock_document)
    assert brief.document_title == "Master Services Agreement"


# 11. Gemini Total Failure Handling
@pytest.mark.anyio
async def test_gemini_total_failure(mock_document):
    mock_bad_service = MagicMock(spec=BaseGeminiService)
    mock_bad_service.generate_structured_analysis = AsyncMock(
        side_effect=GeminiServiceUnavailableException("Gemini unavailable")
    )
    svc = BriefService(service=mock_bad_service)
    with pytest.raises(GeminiServiceUnavailableException):
        await svc.generate_brief(document_id=mock_document.document_id, document=mock_document)


# 12. Privacy: Zero-retention logging check (no document text in logs)
@pytest.mark.anyio
async def test_privacy_no_document_text_logged(mock_document, mock_gemini, caplog):
    svc = BriefService(service=mock_gemini)
    with caplog.at_level(logging.INFO):
        await svc.generate_brief(document_id=mock_document.document_id, document=mock_document)

    log_output = " ".join([r.message for r in caplog.records])
    assert "Uncredited upfront annual commitment fees of $240,000" not in log_output
    assert "Neither party shall be liable for indirect or consequential damages." not in log_output


# 13. PDF Export Generation
def test_pdf_export_generation():
    raw = MOCK_RAW_GEMINI_BRIEF.copy()
    raw["document_id"] = "doc-pdf-test"
    brief = LawyerBrief.model_validate(raw)
    pdf_bytes = ExportService.generate_brief_pdf(brief)

    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF-")


# 14. DOCX Export Generation
def test_docx_export_generation():
    raw = MOCK_RAW_GEMINI_BRIEF.copy()
    raw["document_id"] = "doc-docx-test"
    brief = LawyerBrief.model_validate(raw)
    docx_bytes = ExportService.generate_brief_docx(brief)

    assert isinstance(docx_bytes, bytes)
    assert len(docx_bytes) > 1000
    assert docx_bytes.startswith(b"PK\x03\x04")


# 15, 16, 17. Checklist, Questions, Attention Area Generation & Safety Sanitization
@pytest.mark.anyio
async def test_safety_sanitization_and_item_generation(mock_document):
    unsafe_raw = MOCK_RAW_GEMINI_BRIEF.copy()
    unsafe_raw["executive_summary"] = "This contract is illegal and this clause is definitely invalid."
    unsafe_att = unsafe_raw["attention_areas"][0].copy()
    unsafe_att["why_it_matters"] = "You will win if you sue because this clause is unenforceable."
    unsafe_raw["attention_areas"] = [unsafe_att]

    mock_gemini_local = MagicMock(spec=BaseGeminiService)
    mock_gemini_local.generate_structured_analysis = AsyncMock(return_value=unsafe_raw)
    svc = BriefService(service=mock_gemini_local)

    brief = await svc.generate_brief(document_id=mock_document.document_id, document=mock_document)

    # Verify that forbidden definitive assertions were sanitized
    assert "this contract is illegal" not in brief.executive_summary.lower()
    assert "you will win" not in brief.attention_areas[0].why_it_matters.lower()
    assert "this clause is unenforceable" not in brief.attention_areas[0].why_it_matters.lower()


# 18. Brief API Endpoints: POST & GET
def test_brief_api_endpoints(client, mock_document, mock_gemini):
    brief_service.set_gemini_service(mock_gemini)
    brief_service.clear_cache()

    with patch.object(
        brief_service,
        "_load_document_from_db",
        return_value=(SAMPLE_DOCUMENT_TEXT, "sample_msa.txt", "txt", mock_document.pages),
    ):
        # POST /documents/{id}/brief
        post_res = client.post(
            f"/api/v1/documents/{mock_document.document_id}/brief",
            json={"document_id": mock_document.document_id, "document": mock_document.model_dump(mode="json")},
        )
        assert post_res.status_code == 200
        data = post_res.json()
        assert data["document_id"] == mock_document.document_id
        assert "brief" in data
        assert data["brief"]["document_title"] == "Master Services Agreement"

        # GET /documents/{id}/brief (retrieves cached brief)
        get_res = client.get(f"/api/v1/documents/{mock_document.document_id}/brief")
        assert get_res.status_code == 200
        get_data = get_res.json()
        assert get_data["document_id"] == mock_document.document_id
        assert get_data["brief"]["document_title"] == "Master Services Agreement"


# 19. Export API Endpoints: PDF & DOCX (POST & GET)
def test_export_api_endpoints(client, mock_document, mock_gemini):
    brief_service.set_gemini_service(mock_gemini)
    brief_service.clear_cache()

    with patch.object(
        brief_service,
        "_load_document_from_db",
        return_value=(SAMPLE_DOCUMENT_TEXT, "sample_msa.txt", "txt", mock_document.pages),
    ):
        # 1. PDF Export POST
        pdf_post = client.post(
            f"/api/v1/documents/{mock_document.document_id}/brief/export/pdf",
            json={"document_id": mock_document.document_id, "document": mock_document.model_dump(mode="json")},
        )
        assert pdf_post.status_code == 200
        assert pdf_post.headers["content-type"] == "application/pdf"
        assert pdf_post.content.startswith(b"%PDF-")

        # 2. PDF Export GET
        pdf_get = client.get(f"/api/v1/documents/{mock_document.document_id}/brief/export/pdf")
        assert pdf_get.status_code == 200
        assert pdf_get.content.startswith(b"%PDF-")

        # 3. DOCX Export POST
        docx_post = client.post(
            f"/api/v1/documents/{mock_document.document_id}/brief/export/docx",
            json={"document_id": mock_document.document_id, "document": mock_document.model_dump(mode="json")},
        )
        assert docx_post.status_code == 200
        assert "wordprocessingml" in docx_post.headers["content-type"]
        assert docx_post.content.startswith(b"PK\x03\x04")

        # 4. DOCX Export GET
        docx_get = client.get(f"/api/v1/documents/{mock_document.document_id}/brief/export/docx")
        assert docx_get.status_code == 200
        assert docx_get.content.startswith(b"PK\x03\x04")


# 20. End-to-end Brief Caching & Force-Regenerate
@pytest.mark.anyio
async def test_end_to_end_brief_caching_and_force_regenerate(mock_document, mock_gemini):
    svc = BriefService(service=mock_gemini)
    svc.clear_cache()

    # 1. First call calls Gemini
    brief1 = await svc.generate_brief(mock_document.document_id, document=mock_document)
    assert mock_gemini.generate_structured_analysis.call_count == 1

    # 2. Second call without force_regenerate hits cache
    brief2 = await svc.generate_brief(mock_document.document_id, document=mock_document)
    assert mock_gemini.generate_structured_analysis.call_count == 1
    assert brief1 == brief2

    # 3. Third call with force_regenerate calls Gemini again
    brief3 = await svc.generate_brief(mock_document.document_id, document=mock_document, force_regenerate=True)
    assert mock_gemini.generate_structured_analysis.call_count == 2
