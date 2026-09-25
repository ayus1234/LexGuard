from fastapi.testclient import TestClient


def test_upload_valid_pdf(client: TestClient, sample_pdf_bytes: bytes):
    """
    Test uploading a valid multi-page PDF document.
    Asserts:
      - 200 OK
      - file_type is 'pdf'
      - page_count is 2
      - pages contains grounding character offsets
      - section detection found 'ARTICLE 1' or '§ 8.3'
      - SHA-256 fingerprint generated
    """
    files = {"file": ("enterprise_nda.pdf", sample_pdf_bytes, "application/pdf")}
    response = client.post("/api/v1/documents/upload", files=files)
    assert response.status_code == 200

    data = response.json()
    assert data["filename"] == "enterprise_nda.pdf"
    assert data["file_type"] == "pdf"
    assert data["page_count"] == 2
    assert len(data["pages"]) == 2
    assert data["word_count"] > 10
    assert data["character_count"] > 50

    # Grounding checks
    first_page = data["pages"][0]
    assert first_page["page_number"] == 1
    assert first_page["character_start"] == 0
    assert first_page["character_end"] > 0
    assert "NON-DISCLOSURE" in first_page["text"]

    second_page = data["pages"][1]
    assert second_page["page_number"] == 2
    assert second_page["character_start"] > first_page["character_end"]
    assert "Limitation of Liability" in second_page["text"]

    # Section detection
    section_titles = [s["title"] for s in data["sections"]]
    assert any("ARTICLE" in t or "§" in t for t in section_titles)

    # Metadata checks
    meta = data["metadata"]
    assert meta["file_size_bytes"] == len(sample_pdf_bytes)
    assert len(meta["sha256_hash"]) == 64
    assert meta["extraction_engine"] == "pymupdf-fitz"


def test_upload_valid_docx(client: TestClient, sample_docx_bytes: bytes):
    """
    Test uploading a valid DOCX document.
    Asserts:
      - 200 OK
      - file_type is 'docx'
      - Headings, text paragraphs, and table contents extracted
    """
    files = {
        "file": (
            "statement_of_work.docx",
            sample_docx_bytes,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    }
    response = client.post("/api/v1/documents/upload", files=files)
    assert response.status_code == 200

    data = response.json()
    assert data["filename"] == "statement_of_work.docx"
    assert data["file_type"] == "docx"
    assert data["page_count"] >= 1
    assert "INTELLECTUAL PROPERTY" in data["extracted_text"]
    assert "TABLE DATA" in data["extracted_text"]
    assert "Phase 1 Completion" in data["extracted_text"]
    assert data["metadata"]["extraction_engine"] == "python-docx"


def test_upload_valid_txt(client: TestClient, sample_txt_bytes: bytes):
    """
    Test uploading a valid plain text legal document.
    Asserts:
      - 200 OK
      - file_type is 'txt'
      - Accurately captures text and word count
    """
    files = {"file": ("terms.txt", sample_txt_bytes, "text/plain")}
    response = client.post("/api/v1/documents/upload", files=files)
    assert response.status_code == 200

    data = response.json()
    assert data["filename"] == "terms.txt"
    assert data["file_type"] == "txt"
    assert "MASTER SERVICES AGREEMENT" in data["extracted_text"]
    assert data["word_count"] > 10
    assert data["metadata"]["extraction_engine"] == "plain-text-decoder"
