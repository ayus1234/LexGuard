from pathlib import Path
from typing import List, Tuple, Union
try:
    from backend.app.core.logging import logger
    from backend.app.utils.file_validation import ExtractionFailedException
except ImportError:
    from app.core.logging import logger
    from app.utils.file_validation import ExtractionFailedException


class TextExtractionService:
    """
    Extracts text from plain text documents (.txt) with robust encoding fallback.
    Segments text into pages using form feed characters (\x0c) if present,
    or falls back to logical word-count page segmentation (approx 450 words/page).
    """

    SUPPORTED_ENCODINGS = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]

    @classmethod
    def extract_from_file(cls, filepath: Union[str, Path]) -> List[Tuple[int, str]]:
        path = Path(filepath)
        if not path.exists():
            raise ExtractionFailedException(f"Target text file does not exist: {path.name}")

        raw_bytes = path.read_bytes()
        return cls.extract_from_bytes(raw_bytes)

    @classmethod
    def extract_from_bytes(cls, content: bytes) -> List[Tuple[int, str]]:
        decoded_text: str = ""
        decoded = False

        for encoding in cls.SUPPORTED_ENCODINGS:
            try:
                decoded_text = content.decode(encoding)
                decoded = True
                break
            except (UnicodeDecodeError, LookupError):
                continue

        if not decoded:
            try:
                decoded_text = content.decode("utf-8", errors="replace")
            except Exception as e:
                logger.error(f"Failed to decode text file: {str(e)}")
                raise ExtractionFailedException("Unable to decode text content with supported character encodings.")

        # Check if form feed (\x0c) page breaks are present
        if "\x0c" in decoded_text:
            raw_pages = decoded_text.split("\x0c")
            pages: List[Tuple[int, str]] = []
            page_num = 1
            for p in raw_pages:
                clean_p = p.strip()
                if clean_p:
                    pages.append((page_num, clean_p))
                    page_num += 1
            if pages:
                return pages

        # Logical page segmentation based on word counts (450 words/page)
        words = decoded_text.split()
        if not words:
            return [(1, "")]

        words_per_page = 450
        total_pages = max(1, (len(words) + words_per_page - 1) // words_per_page)

        pages = []
        for i in range(total_pages):
            page_words = words[i * words_per_page : (i + 1) * words_per_page]
            pages.append((i + 1, " ".join(page_words)))

        return pages


text_service = TextExtractionService()
