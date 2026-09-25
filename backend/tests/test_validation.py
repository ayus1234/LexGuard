import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch


def test_unsupported_file_extension(client: TestClient):
    """Uploading files with unauthorized extensions must return 400 UNSUPPORTED_FILE_TYPE."""
    files = {"file": ("malicious_payload.exe", b"MZ\x90\x00\x03\x00\x00\x00", "application/octet-stream")}
    response = client.post("/api/v1/documents/upload", files=files)
    assert response.status_code == 400
    data = response.json()
    assert data["error"]["code"] == "UNSUPPORTED_FILE_TYPE"


def test_empty_file(client: TestClient):
    """Uploading an empty file (0 bytes) must return 400 EMPTY_FILE."""
    files = {"file": ("empty_contract.pdf", b"", "application/pdf")}
    response = client.post("/api/v1/documents/upload", files=files)
    assert response.status_code == 400
    data = response.json()
    assert data["error"]["code"] == "EMPTY_FILE"


def test_masqueraded_pdf(client: TestClient, masqueraded_file_bytes: bytes):
    """Uploading a file disguised as a PDF with non-PDF magic bytes must return 400 CORRUPTED_PDF."""
    files = {"file": ("spoofed.pdf", masqueraded_file_bytes, "application/pdf")}
    response = client.post("/api/v1/documents/upload", files=files)
    assert response.status_code == 400
    data = response.json()
    assert data["error"]["code"] == "CORRUPTED_PDF"


def test_corrupted_pdf(client: TestClient, corrupted_pdf_bytes: bytes):
    """Uploading a corrupted PDF that cannot be parsed by PyMuPDF must return 400."""
    files = {"file": ("broken.pdf", corrupted_pdf_bytes, "application/pdf")}
    response = client.post("/api/v1/documents/upload", files=files)
    assert response.status_code == 400
    data = response.json()
    assert data["error"]["code"] in ["CORRUPTED_PDF", "EXTRACTION_FAILED"]


def test_file_too_large(client: TestClient):
    """Simulate file exceeding size threshold and verify 413 FILE_TOO_LARGE."""
    from backend.app.core.config import settings

    # Patch settings.MAX_UPLOAD_SIZE_MB to 1KB for this test
    with patch.object(type(settings), "max_upload_size_bytes", new=100):
        files = {"file": ("oversized.txt", b"A" * 200, "text/plain")}
        response = client.post("/api/v1/documents/upload", files=files)
        assert response.status_code == 413
        data = response.json()
        assert data["error"]["code"] == "FILE_TOO_LARGE"
