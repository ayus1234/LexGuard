# LexGuard Backend Service

AI Legal Document Intelligence Platform — Backend Foundation & Document Ingestion Pipeline.

## Features
- **FastAPI** high-performance asynchronous application.
- **Privacy-First Ingestion**: Ephemeral document processing with guaranteed temporary file cleanup.
- **Document Text & Grounding Extraction**:
  - **PDF** via PyMuPDF (`fitz`): page-by-page text, character offsets, section headings.
  - **DOCX** via `python-docx`: paragraphs, structured headings, table extraction.
  - **TXT**: safe UTF-8 decoding with fallback handling.
- **Strict File Validation**: extension, MIME type, magic bytes, file-size enforcement (<= 50MB), empty and corrupted file detection.
- **Standardized Machine-Readable Errors**: `{ "error": { "code": "...", "message": "..." } }`.

## Setup & Running

1. Create a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   # or source .venv/bin/activate (Linux/Mac)
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the development server:
   ```bash
   uvicorn app.main:app --port 8000 --reload
   ```

4. Interactive API Docs:
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

5. Run test suite:
   ```bash
   pytest tests -v
   ```
