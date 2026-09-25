import io
from pathlib import Path
from typing import List, Tuple, Union
import docx
try:
    from backend.app.core.logging import logger
    from backend.app.utils.file_validation import UnreadableDOCXException, ExtractionFailedException
except ImportError:
    from app.core.logging import logger
    from app.utils.file_validation import UnreadableDOCXException, ExtractionFailedException


class DOCXExtractionService:
    """
    Extracts text, headings, and table structures from DOCX documents using python-docx.
    Organizes text into logical page units (detecting page breaks or estimating standard 450-word page units).
    """

    @classmethod
    def extract_from_file(cls, filepath: Union[str, Path]) -> List[Tuple[int, str]]:
        path = Path(filepath)
        if not path.exists():
            raise ExtractionFailedException(f"Target DOCX file does not exist: {path.name}")

        try:
            doc = docx.Document(io.BytesIO(path.read_bytes()))
        except Exception as e:
            logger.error(f"Failed to open DOCX package: {str(e)}")
            raise UnreadableDOCXException(f"The DOCX file is malformed or unreadable: {str(e)}")

        try:
            chunks: List[str] = []

            # 1. Extract paragraphs and headings
            for p in doc.paragraphs:
                text = p.text.strip()
                if not text:
                    continue

                # Preserve headings with prefix for legal citation detection
                if p.style and p.style.name and p.style.name.startswith("Heading"):
                    chunks.append(f"\n{text}\n")
                else:
                    chunks.append(text)

            # 2. Extract tables as structured text
            for table in doc.tables:
                table_lines: List[str] = []
                for row in table.rows:
                    row_cells = [cell.text.strip().replace("\n", " ") for cell in row.cells]
                    # Filter out duplicate merged cells
                    filtered_cells = []
                    for c in row_cells:
                        if not filtered_cells or c != filtered_cells[-1]:
                            filtered_cells.append(c)
                    if any(filtered_cells):
                        table_lines.append(" | ".join(filtered_cells))

                if table_lines:
                    chunks.append("\n[TABLE DATA]:\n" + "\n".join(table_lines) + "\n")

            if not chunks:
                return [(1, "")]

            full_text = "\n\n".join(chunks)

            # Segment into estimated standard page bounds (approx 500 words per page)
            words = full_text.split()
            words_per_page = 450
            total_estimated_pages = max(1, (len(words) + words_per_page - 1) // words_per_page)

            pages: List[Tuple[int, str]] = []
            for i in range(total_estimated_pages):
                page_words = words[i * words_per_page : (i + 1) * words_per_page]
                pages.append((i + 1, " ".join(page_words)))

            return pages
        except UnreadableDOCXException:
            raise
        except Exception as e:
            logger.error(f"Error during DOCX extraction: {str(e)}")
            raise ExtractionFailedException(f"Failed to extract text from DOCX: {str(e)}")


docx_service = DOCXExtractionService()
