import io
import zipfile
import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.services.share_service import share_service
from backend.app.schemas.share import CreateShareRequest
from backend.app.schemas.brief import (
    LawyerBrief,
    KeyInformationItem,
    AttentionAreaItem,
    BriefChecklistItem,
)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def sample_brief():
    return LawyerBrief(
        document_id="test-doc-share-001",
        document_title="Master Services Agreement - ACME Corp",
        document_type="Commercial Agreement",
        jurisdiction="State of Delaware",
        generated_at=datetime.now(timezone.utc),
        executive_summary="This Master Services Agreement establishes commercial terms for cloud computing infrastructure.",
        key_information=[
            KeyInformationItem(
                category="Commercial Term",
                label="Governing Law",
                value="Delaware",
                source_reference="Section 14.1",
                page=12,
                section="14.1",
                verified=True,
            )
        ],
        attention_areas=[
            AttentionAreaItem(
                id="att-1",
                title="Uncapped Indemnification",
                category="Liability",
                description="Indemnity exposure is uncapped for third-party claims.",
                why_it_matters="Presents unlimited balance sheet exposure.",
                review_level="review_recommended",
                source_reference="Section 9.2",
                page=8,
                section="9.2",
                verified=True,
            )
        ],
        checklist=[
            BriefChecklistItem(
                id="chk-1",
                section_index=1,
                section_title="Financial & Commitments",
                title="Confirm SLA remedies",
                citation="Section 4.3",
                badge_text="Urgent",
                badge_variant="urgent",
                completed=False,
                page=3,
                section="4.3",
            )
        ],
        disclaimer="LexGuard Counsel Preparation Brief is for educational consultation preparation only.",
        model="gemini-1.5-flash",
        citations_verified_count=1,
        citations_unverified_count=0,
        processing_time_ms=1200,
    )


def test_pdf_export_endpoint(client, sample_brief):
    """Verifies that PDF export returns valid binary PDF with correct attachment headers."""
    resp = client.post(
        f"/api/v1/documents/{sample_brief.document_id}/brief/export/pdf",
        json={"document_id": sample_brief.document_id, "brief": sample_brief.model_dump(mode="json")},
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert "LexGuard_Executive_Brief.pdf" in resp.headers["content-disposition"]
    # PDF magic signature
    assert resp.content.startswith(b"%PDF-")


def test_docx_export_endpoint(client, sample_brief):
    """Verifies that DOCX export returns a valid OpenXML Word document containing expected text."""
    resp = client.post(
        f"/api/v1/documents/{sample_brief.document_id}/brief/export/docx",
        json={"document_id": sample_brief.document_id, "brief": sample_brief.model_dump(mode="json")},
    )
    assert resp.status_code == 200
    assert "wordprocessingml.document" in resp.headers["content-type"]
    assert "LexGuard_Word_Checklist.docx" in resp.headers["content-disposition"]

    # Verify DOCX is a valid ZIP archive containing word/document.xml
    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        namelist = zf.namelist()
        assert "word/document.xml" in namelist
        doc_xml = zf.read("word/document.xml").decode("utf-8")
        assert "Master Services Agreement - ACME Corp" in doc_xml


def test_create_and_get_secure_share(client, sample_brief):
    """Verifies cryptographic share creation, unguessable token, and read-only retrieval."""
    payload = {
        "document_id": sample_brief.document_id,
        "title": sample_brief.document_title,
        "brief": sample_brief.model_dump(mode="json"),
        "ttl_hours": 24,
    }
    create_resp = client.post("/api/v1/share/dossier", json=payload)
    assert create_resp.status_code == 201
    data = create_resp.json()

    share_id = data["share_id"]
    assert len(share_id) >= 24  # Sufficient entropy
    assert "share_url" in data
    assert f"/share/{share_id}" in data["share_url"]
    assert "expires_at" in data

    # Retrieve shared dossier
    get_resp = client.get(f"/api/v1/share/dossier/{share_id}")
    assert get_resp.status_code == 200
    retrieved = get_resp.json()
    assert retrieved["share_id"] == share_id
    assert retrieved["title"] == sample_brief.document_title
    assert retrieved["brief"]["document_id"] == sample_brief.document_id
    assert len(retrieved["brief"]["checklist"]) == 1

    # Ensure no internal secrets or DB paths leaked
    raw_text = get_resp.text
    assert "password" not in raw_text.lower()
    assert "postgresql://" not in raw_text
    assert "api_key" not in raw_text.lower()


def test_invalid_share_token_returns_404(client):
    """Verifies that invalid or nonexistent share tokens return HTTP 404."""
    resp = client.get("/api/v1/share/dossier/nonexistent-token-abc-123")
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "SHARE_NOT_FOUND"


def test_expired_share_token_returns_410(client, sample_brief):
    """Verifies that expired share tokens return HTTP 410 and are cleared."""
    # Manually inject an already-expired share into service
    expired_token = "test-expired-token-xyz"
    past_time = datetime.now(timezone.utc) - timedelta(hours=1)
    share_service._shares[expired_token] = {
        "share_id": expired_token,
        "document_id": sample_brief.document_id,
        "title": sample_brief.document_title,
        "created_at": past_time - timedelta(hours=24),
        "expires_at": past_time,
        "brief": sample_brief,
    }

    resp = client.get(f"/api/v1/share/dossier/{expired_token}")
    assert resp.status_code == 410
    assert resp.json()["error"]["code"] == "SHARE_EXPIRED"

    # Verify expired token was cleaned up
    assert expired_token not in share_service._shares
