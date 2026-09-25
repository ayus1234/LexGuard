from pathlib import Path
from typing import List, Tuple, Union, TYPE_CHECKING
import pymupdf

if TYPE_CHECKING:
    from app.core.logging import logger
    from app.utils.file_validation import CorruptedPDFException, ExtractionFailedException
else:
    try:
        from backend.app.core.logging import logger
        from backend.app.utils.file_validation import CorruptedPDFException, ExtractionFailedException
    except ImportError:
        from app.core.logging import logger
        from app.utils.file_validation import CorruptedPDFException, ExtractionFailedException


class PDFExtractionService:
    """
    Extracts text and page-level grounding metadata from PDF documents using PyMuPDF (fitz).
    Preserves exact 1-indexed page boundaries for downstream legal citation.
    """

    @classmethod
    def extract_from_file(cls, filepath: Union[str, Path]) -> List[Tuple[int, str]]:
        path = Path(filepath)
        if not path.exists():
            raise ExtractionFailedException(f"Target PDF file does not exist: {path.name}")

        try:
            doc = pymupdf.open(stream=path.read_bytes(), filetype="pdf")
        except Exception as e:
            logger.error(f"Failed to open PDF document: {str(e)}")
            raise CorruptedPDFException(f"The PDF file is corrupted or cannot be read: {str(e)}")

        try:
            if doc.is_encrypted:
                # Attempt to authenticate with empty password (some PDFs are encrypted with blank pw)
                if not doc.authenticate(""):
                    raise CorruptedPDFException("Password-protected or encrypted PDF cannot be parsed.")

            total_pages = len(doc)
            if total_pages == 0:
                raise CorruptedPDFException("The PDF document contains 0 pages.")

            pages: List[Tuple[int, str]] = []
            for page_index in range(total_pages):
                page = doc[page_index]
                text = str(page.get_text("text") or "")
                pages.append((page_index + 1, text))

            return pages
        except CorruptedPDFException:
            raise
        except Exception as e:
            logger.error(f"Error during PDF text extraction: {str(e)}")
            raise ExtractionFailedException(f"Failed to extract text from PDF: {str(e)}")
        finally:
            doc.close()


pdf_service = PDFExtractionService()
