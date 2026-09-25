from pathlib import Path
from typing import Tuple
from fastapi import UploadFile
try:
    from backend.app.core.config import settings
except ImportError:
    from app.core.config import settings


class LexGuardException(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class UnsupportedFileTypeException(LexGuardException):
    def __init__(self, message: str = "Only PDF, DOCX and TXT files are supported."):
        super().__init__(code="UNSUPPORTED_FILE_TYPE", message=message, status_code=400)


class FileTooLargeException(LexGuardException):
    def __init__(self, message: str = f"File exceeds maximum allowed limit of {settings.MAX_UPLOAD_SIZE_MB}MB."):
        super().__init__(code="FILE_TOO_LARGE", message=message, status_code=413)


class EmptyFileException(LexGuardException):
    def __init__(self, message: str = "Uploaded file is empty (0 bytes)."):
        super().__init__(code="EMPTY_FILE", message=message, status_code=400)


class CorruptedPDFException(LexGuardException):
    def __init__(self, message: str = "The PDF file is corrupted or could not be decoded."):
        super().__init__(code="CORRUPTED_PDF", message=message, status_code=400)


class UnreadableDOCXException(LexGuardException):
    def __init__(self, message: str = "The DOCX file is malformed or unreadable."):
        super().__init__(code="UNREADABLE_DOCX", message=message, status_code=400)


class ExtractionFailedException(LexGuardException):
    def __init__(self, message: str = "Text extraction failed due to an internal processing error."):
        super().__init__(code="EXTRACTION_FAILED", message=message, status_code=500)


class DocumentTooLargeForAnalysisException(LexGuardException):
    def __init__(self, message: str = "Document exceeds the maximum character threshold supported for direct AI analysis."):
        super().__init__(code="DOCUMENT_TOO_LARGE_FOR_ANALYSIS", message=message, status_code=413)


class GeminiServiceUnavailableException(LexGuardException):
    def __init__(self, message: str = "Gemini AI analysis service is temporarily unavailable or misconfigured."):
        super().__init__(code="AI_SERVICE_UNAVAILABLE", message=message, status_code=503)


class GeminiQuotaExceededException(LexGuardException):
    def __init__(self, message: str = "Gemini AI API rate limit or quota exceeded. Please retry after a brief delay."):
        super().__init__(code="AI_QUOTA_EXCEEDED", message=message, status_code=429)


class AnalysisValidationException(LexGuardException):
    def __init__(self, message: str = "The AI model response failed structural validation or schema constraints."):
        super().__init__(code="ANALYSIS_VALIDATION_FAILED", message=message, status_code=502)


class DocumentNotIndexedException(LexGuardException):
    def __init__(self, message: str = "The requested document has not been indexed in the vector store."):
        super().__init__(code="DOCUMENT_NOT_INDEXED", message=message, status_code=404)


class DocumentNotFoundException(LexGuardException):
    def __init__(self, message: str = "The requested document was not found."):
        super().__init__(code="DOCUMENT_NOT_FOUND", message=message, status_code=404)


class BriefValidationException(LexGuardException):
    def __init__(self, message: str = "The AI model response failed structural validation for the lawyer brief."):
        super().__init__(code="BRIEF_VALIDATION_FAILED", message=message, status_code=502)


class EmbeddingServiceException(LexGuardException):
    def __init__(self, message: str = "Failed to generate vector embeddings for document text."):
        super().__init__(code="EMBEDDING_FAILED", message=message, status_code=502)


class VectorStoreException(LexGuardException):
    def __init__(self, message: str = "Vector database encountered an internal indexing or search error."):
        super().__init__(code="VECTOR_STORE_ERROR", message=message, status_code=500)


class ShareNotFoundException(LexGuardException):
    def __init__(self, message: str = "The shared dossier link was not found or has been revoked."):
        super().__init__(code="SHARE_NOT_FOUND", message=message, status_code=404)


class ShareExpiredException(LexGuardException):
    def __init__(self, message: str = "The shared dossier link has expired."):
        super().__init__(code="SHARE_EXPIRED", message=message, status_code=410)


ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}


def detect_file_type(filename: str, header_bytes: bytes) -> str:
    """
    Validates extension and signature magic bytes to prevent masqueraded files.
    Returns normalized type: 'pdf', 'docx', or 'txt'.
    """
    if not filename:
        raise UnsupportedFileTypeException("Filename is missing.")

    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise UnsupportedFileTypeException(
            f"Unsupported file extension '{ext}'. Only PDF, DOCX and TXT files are supported."
        )

    # Magic byte verification
    if ext == ".pdf":
        if not header_bytes.startswith(b"%PDF-"):
            raise CorruptedPDFException("Invalid PDF header signature.")
        return "pdf"

    if ext == ".docx":
        # DOCX is an OOXML ZIP package starting with PK\x03\x04
        if not header_bytes.startswith(b"PK\x03\x04"):
            raise UnreadableDOCXException("Invalid DOCX package signature.")
        return "docx"

    if ext == ".txt":
        # Basic check for null bytes which would indicate binary executable/data
        if b"\x00" in header_bytes[:512]:
            raise UnsupportedFileTypeException("Binary data detected in text file.")
        return "txt"

    raise UnsupportedFileTypeException()


def validate_file_content(content: bytes, filename: str) -> str:
    """
    Validates complete byte buffer against size limits, empty files, and format signatures.
    """
    if len(content) == 0:
        raise EmptyFileException()

    if len(content) > settings.max_upload_size_bytes:
        raise FileTooLargeException(
            f"File size ({len(content) / (1024 * 1024):.1f}MB) exceeds maximum allowed limit of {settings.MAX_UPLOAD_SIZE_MB}MB."
        )

    file_type = detect_file_type(filename, content[:16])
    return file_type
