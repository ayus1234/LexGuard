from typing import TYPE_CHECKING
import pytest
import logging
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

if TYPE_CHECKING:
    from app.schemas.document import DocumentResponse, DocumentMetadata, PageExtraction
    from app.schemas.analysis import (
        DocumentAnalysisResponse,
        DocumentAnalysisRequest,
        ImportanceLevel,
        ReviewLevel,
        ClauseCategory,
    )
    from app.services.analysis_service import analysis_service
    from app.services.gemini_service import BaseGeminiService
    from app.core.config import settings
    from app.utils.file_validation import (
        DocumentTooLargeForAnalysisException,
        AnalysisValidationException,
        GeminiServiceUnavailableException,
        GeminiQuotaExceededException,
    )
else:
    try:
        from backend.app.schemas.document import DocumentResponse, DocumentMetadata, PageExtraction
        from backend.app.schemas.analysis import (
            DocumentAnalysisResponse,
            DocumentAnalysisRequest,
            ImportanceLevel,
            ReviewLevel,
            ClauseCategory,
        )
        from backend.app.services.analysis_service import analysis_service
        from backend.app.services.gemini_service import BaseGeminiService
        from backend.app.core.config import settings
        from backend.app.utils.file_validation import (
            DocumentTooLargeForAnalysisException,
            AnalysisValidationException,
            GeminiServiceUnavailableException,
            GeminiQuotaExceededException,
        )
    except ImportError:
        from app.schemas.document import DocumentResponse, DocumentMetadata, PageExtraction
        from app.schemas.analysis import (
            DocumentAnalysisResponse,
            DocumentAnalysisRequest,
            ImportanceLevel,
            ReviewLevel,
            ClauseCategory,
        )
        from app.services.analysis_service import analysis_service
        from app.services.gemini_service import BaseGeminiService
        from app.core.config import settings
        from app.utils.file_validation import (
            DocumentTooLargeForAnalysisException,
            AnalysisValidationException,
            GeminiServiceUnavailableException,
            GeminiQuotaExceededException,
        )


class MockGeminiSuccessService(BaseGeminiService):
    def __init__(self, response_data: dict):
        self.response_data = response_data

    async def generate_structured_analysis(self, prompt: str, system_instruction: str) -> dict:
        return self.response_data


@pytest.fixture
def sample_ingested_doc() -> DocumentResponse:
    text_p1 = (
        "MUTUAL NON-DISCLOSURE AGREEMENT\n"
        "This Mutual Non-Disclosure Agreement is executed between LexGuard Corp and Acme Corp."
    )
    text_p2 = (
        "§ 8.3 Limitation of Liability\n"
        "Neither party shall be liable for indirect, special, or consequential damages.\n"
        "The governing law shall be the State of Delaware."
    )
    full_text = f"{text_p1}\n\n{text_p2}"

    p1_end = len(text_p1)
    p2_start = p1_end + 2
    p2_end = p2_start + len(text_p2)

    return DocumentResponse(
        document_id="doc_test_12345",
        filename="mutual_nda.pdf",
        file_type="pdf",
        source_type="upload",
        page_count=2,
        word_count=35,
        character_count=len(full_text),
        extracted_text=full_text,
        pages=[
            PageExtraction(
                page_number=1,
                text=text_p1,
                character_start=0,
                character_end=p1_end,
                word_count=15,
            ),
            PageExtraction(
                page_number=2,
                text=text_p2,
                character_start=p2_start,
                character_end=p2_end,
                word_count=20,
            ),
        ],
        sections=[],
        metadata=DocumentMetadata(
            original_filename="mutual_nda.pdf",
            file_size_bytes=1024,
            mime_type="application/pdf",
            sha256_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            extraction_engine="pymupdf-fitz",
        ),
    )


@pytest.fixture
def valid_gemini_payload() -> dict:
    return {
        "document_summary": "A mutual non-disclosure agreement protecting proprietary assets between LexGuard and Acme.",
        "document_type": "Mutual Non-Disclosure Agreement",
        "jurisdiction": "State of Delaware",
        "parties": [
            {"name": "LexGuard Corp", "role": "Disclosing Party"},
            {"name": "Acme Corp", "role": "Receiving Party"},
        ],
        "key_information": [
            {
                "category": "Governance",
                "label": "Governing Law",
                "value": "State of Delaware",
                "source_reference": "Section 8.3",
            }
        ],
        "clauses": [
            {
                "section": "§ 8.3",
                "title": "Limitation of Liability",
                "category": "Liability",
                "importance": "high",
                "plain_language_summary": "Both parties disclaim liability for indirect or consequential damages.",
                "source_reference": "§ 8.3 Limitation of Liability",
            }
        ],
        "attention_areas": [
            {
                "title": "Consequential Damages Exclusion",
                "description": "Standard mutual waiver excluding special or indirect damages.",
                "why_it_may_matter": "Ensures neither party faces unexpected indirect liability exposure.",
                "source_reference": "§ 8.3",
                "review_level": "review_recommended",
            }
        ],
        "citations": [
            {
                "page": 2,
                "section": "§ 8.3",
                "quoted_text": "Neither party shall be liable for indirect, special, or consequential damages.",
                "character_start": None,
                "character_end": None,
                "verified": False,
            }
        ],
    }


# 1. Successful Gemini response parsing
@pytest.mark.anyio
async def test_analysis_schema_valid_response(sample_ingested_doc, valid_gemini_payload):
    service = MockGeminiSuccessService(valid_gemini_payload)
    analysis_service.set_gemini_service(service)

    result = await analysis_service.analyze_document(sample_ingested_doc)
    assert isinstance(result, DocumentAnalysisResponse)
    assert result.document_id == sample_ingested_doc.document_id
    assert result.analysis.document_type == "Mutual Non-Disclosure Agreement"
    assert len(result.analysis.parties) == 2
    assert len(result.analysis.clauses) == 1
    assert result.analysis.clauses[0].importance == ImportanceLevel.high
    assert result.analysis.clauses[0].category == ClauseCategory.liability


# 2. Malformed Gemini JSON handling
@pytest.mark.anyio
async def test_analysis_malformed_json(sample_ingested_doc):
    class BrokenJsonGemini(BaseGeminiService):
        async def generate_structured_analysis(self, prompt, system_instruction):
            raise AnalysisValidationException("Gemini model output could not be parsed as valid JSON.")

    analysis_service.set_gemini_service(BrokenJsonGemini())
    with pytest.raises(AnalysisValidationException) as exc_info:
        await analysis_service.analyze_document(sample_ingested_doc)
    assert exc_info.value.code == "ANALYSIS_VALIDATION_FAILED"


# 3. Missing required fields in model response
@pytest.mark.anyio
async def test_analysis_missing_required_fields(sample_ingested_doc, valid_gemini_payload):
    del valid_gemini_payload["document_summary"]  # Remove required field
    analysis_service.set_gemini_service(MockGeminiSuccessService(valid_gemini_payload))

    with pytest.raises(AnalysisValidationException):
        await analysis_service.analyze_document(sample_ingested_doc)


# 4. Invalid enum values
@pytest.mark.anyio
async def test_analysis_invalid_enum(sample_ingested_doc, valid_gemini_payload):
    valid_gemini_payload["clauses"][0]["importance"] = "EXTREME_DANGER"  # Invalid enum
    analysis_service.set_gemini_service(MockGeminiSuccessService(valid_gemini_payload))

    with pytest.raises(AnalysisValidationException):
        await analysis_service.analyze_document(sample_ingested_doc)


# 5. Citation verification success
@pytest.mark.anyio
async def test_citation_verification_success(sample_ingested_doc, valid_gemini_payload):
    analysis_service.set_gemini_service(MockGeminiSuccessService(valid_gemini_payload))
    result = await analysis_service.analyze_document(sample_ingested_doc)

    citation = result.analysis.citations[0]
    assert citation.verified is True
    assert citation.character_start is not None
    assert citation.character_end is not None
    assert citation.page == 2
    # Verify the slice in the original document text matches the quoted text
    extracted_slice = sample_ingested_doc.extracted_text[citation.character_start : citation.character_end]
    assert extracted_slice == citation.quoted_text
    assert result.metadata.citations_verified_count == 1
    assert result.metadata.citations_unverified_count == 0


# 6. Fabricated citation rejection
@pytest.mark.anyio
async def test_fabricated_citation_rejection(sample_ingested_doc, valid_gemini_payload):
    # Insert a quote that does NOT exist in the document
    valid_gemini_payload["citations"].append(
        {
            "page": 1,
            "section": "§ 99.9",
            "quoted_text": "Party shall pay an astronomical penalty of $500,000,000 USD immediately.",
            "character_start": None,
            "character_end": None,
            "verified": False,
        }
    )
    analysis_service.set_gemini_service(MockGeminiSuccessService(valid_gemini_payload))
    result = await analysis_service.analyze_document(sample_ingested_doc)

    fake_citation = result.analysis.citations[1]
    assert fake_citation.verified is False
    assert fake_citation.character_start is None
    assert fake_citation.character_end is None
    assert result.metadata.citations_unverified_count == 1


# 7. Document too large for analysis rejection
@pytest.mark.anyio
async def test_document_too_large_rejection(sample_ingested_doc, valid_gemini_payload):
    analysis_service.set_gemini_service(MockGeminiSuccessService(valid_gemini_payload))
    with patch.object(settings, "MAX_ANALYSIS_CHAR_COUNT", 50):
        with pytest.raises(DocumentTooLargeForAnalysisException) as exc_info:
            await analysis_service.analyze_document(sample_ingested_doc)
        assert exc_info.value.code == "DOCUMENT_TOO_LARGE_FOR_ANALYSIS"
        assert exc_info.value.status_code == 413


# 8. Gemini API failure handling
@pytest.mark.anyio
async def test_gemini_api_failure(sample_ingested_doc):
    class FailingGemini(BaseGeminiService):
        async def generate_structured_analysis(self, prompt, system_instruction):
            raise GeminiServiceUnavailableException("Gemini API connection error")

    analysis_service.set_gemini_service(FailingGemini())
    with pytest.raises(GeminiServiceUnavailableException):
        await analysis_service.analyze_document(sample_ingested_doc)


# 9. Gemini API timeout handling
@pytest.mark.anyio
async def test_gemini_api_timeout(sample_ingested_doc):
    class TimeoutGemini(BaseGeminiService):
        async def generate_structured_analysis(self, prompt, system_instruction):
            raise GeminiServiceUnavailableException("Gemini API request timed out.")

    analysis_service.set_gemini_service(TimeoutGemini())
    with pytest.raises(GeminiServiceUnavailableException):
        await analysis_service.analyze_document(sample_ingested_doc)


# 10. Privacy check: No document text or prompts in log output
@pytest.mark.anyio
async def test_privacy_no_text_in_logs(sample_ingested_doc, valid_gemini_payload, caplog):
    caplog.set_level(logging.INFO)
    secret_text = "ULTRA_CONFIDENTIAL_MERGER_CODE_98765"
    sample_ingested_doc.extracted_text += f"\n{secret_text}"

    analysis_service.set_gemini_service(MockGeminiSuccessService(valid_gemini_payload))
    await analysis_service.analyze_document(sample_ingested_doc)

    for record in caplog.records:
        assert secret_text not in record.message


# 11. Legal safety check: non-definitive review levels
@pytest.mark.anyio
async def test_legal_safety_review_levels(sample_ingested_doc, valid_gemini_payload):
    analysis_service.set_gemini_service(MockGeminiSuccessService(valid_gemini_payload))
    result = await analysis_service.analyze_document(sample_ingested_doc)

    for area in result.analysis.attention_areas:
        assert area.review_level in [
            ReviewLevel.review_recommended,
            ReviewLevel.attention_warranted,
            ReviewLevel.advisory_only,
        ]
        # Must not contain banned definitive language in titles or description
        assert "illegal" not in area.title.lower()
        assert "void" not in area.title.lower()


# 12. End-to-end integration: Upload document then analyze via HTTP TestClient
def test_end_to_end_upload_and_analyze(client: TestClient, sample_txt_bytes: bytes, valid_gemini_payload):
    analysis_service.set_gemini_service(MockGeminiSuccessService(valid_gemini_payload))

    # Step 1: Upload
    files = {"file": ("integration_test_agreement.txt", sample_txt_bytes, "text/plain")}
    upload_res = client.post("/api/v1/documents/upload", files=files)
    assert upload_res.status_code == 200
    doc_data = upload_res.json()

    # Step 2: Analyze
    analyze_payload = {"document": doc_data}
    analyze_res = client.post("/api/v1/documents/analyze", json=analyze_payload)
    assert analyze_res.status_code == 200

    analysis_json = analyze_res.json()
    assert analysis_json["document_id"] == doc_data["document_id"]
    assert "analysis" in analysis_json
    assert "metadata" in analysis_json
    assert analysis_json["metadata"]["model"] == settings.GEMINI_MODEL
