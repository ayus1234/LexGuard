from pathlib import Path
from typing import List, Tuple, Union
try:
    from backend.app.core.logging import logger
    from backend.app.services.pdf_service import pdf_service
    from backend.app.services.docx_service import docx_service
    from backend.app.services.text_service import text_service
    from backend.app.utils.file_validation import (
        UnsupportedFileTypeException,
        ExtractionFailedException,
        CorruptedPDFException,
        UnreadableDOCXException,
    )
except ImportError:
    from app.core.logging import logger
    from app.services.pdf_service import pdf_service
    from app.services.docx_service import docx_service
    from app.services.text_service import text_service
    from app.utils.file_validation import (
        UnsupportedFileTypeException,
        ExtractionFailedException,
        CorruptedPDFException,
        UnreadableDOCXException,
    )


class DocumentExtractionService:
    """
    Central dispatcher that routes document parsing to specialized extraction engines:
    - PyMuPDF (fitz) for PDF files
    - python-docx for Microsoft Word DOCX files
    - TextExtractionService for plain text files
    """

    @classmethod
    def extract_document(
        cls, filepath: Union[str, Path], file_type: str
    ) -> Tuple[List[Tuple[int, str]], str]:
        """
        Dispatches extraction based on normalized file_type ('pdf', 'docx', 'txt').
        Returns:
            Tuple of (raw_pages, extraction_engine_name)
        """
        path = Path(filepath)
        normalized_type = file_type.lower().strip()

        if normalized_type == "pdf":
            engine = "pymupdf-fitz"
            pages = pdf_service.extract_from_file(path)
            return pages, engine

        elif normalized_type == "docx":
            engine = "python-docx"
            pages = docx_service.extract_from_file(path)
            return pages, engine

        elif normalized_type == "txt":
            engine = "plain-text-decoder"
            pages = text_service.extract_from_file(path)
            return pages, engine

        else:
            raise UnsupportedFileTypeException(f"Unsupported file format for extraction: {normalized_type}")


extraction_service = DocumentExtractionService()
