import re
import hashlib
from typing import List, Tuple
try:
    from backend.app.models.document import PageData, SectionData
except ImportError:
    from app.models.document import PageData, SectionData


class NormalizationService:
    """
    Standardizes whitespace, calculates global grounding character offsets,
    computes cryptographic digests, and identifies potential legal section markers.
    """

    # Matches Section and Article headings common in contracts:
    # e.g., '§ 8.3', 'Section 8.3', 'ARTICLE 8', 'Article IV', 'SCHEDULE B'
    SECTION_PATTERN = re.compile(
        r'(?:^|\n)\s*(§\s*\d+(?:\.\d+)*[a-zA-Z\d\(\)]*|'
        r'SECTION\s+\d+(?:\.\d+)*[a-zA-Z\d\(\)]*|'
        r'ARTICLE\s+(?:[IVXLCDM]+|\d+)|'
        r'SCHEDULE\s+[A-Z\d]+)'
        r'[\.:\s\-]+([^\n]{3,80})',
        re.IGNORECASE
    )

    @staticmethod
    def compute_sha256(content: bytes) -> str:
        """Compute SHA-256 cryptographic fingerprint of raw document bytes."""
        hasher = hashlib.sha256()
        hasher.update(content)
        return hasher.hexdigest()

    @staticmethod
    def clean_text(text: str) -> str:
        """Normalize line endings, replace non-breaking spaces, and strip trailing whitespace."""
        if not text:
            return ""

        # Normalize carriage returns
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        # Replace non-breaking and special unicode spaces
        text = re.sub(r'[\u00A0\u1680\u2000-\u200B\u202F\u205F\u3000]', ' ', text)
        # Strip trailing whitespace on each line
        lines = [line.rstrip() for line in text.split("\n")]
        # Collapse excessive blank lines (> 2 into 2)
        cleaned = re.sub(r'\n{3,}', '\n\n', "\n".join(lines))
        return cleaned.strip()

    @staticmethod
    def count_words(text: str) -> int:
        """Count approximate words in text using whitespace splitting."""
        if not text:
            return 0
        return len(text.split())

    @classmethod
    def process_pages(cls, raw_pages: List[Tuple[int, str]]) -> Tuple[str, List[PageData], List[SectionData]]:
        """
        Accepts list of (page_number, raw_text).
        Produces:
          - full unified document text
          - PageData list with accurate character_start and character_end bounds
          - SectionData list with headings and page anchors
        """
        pages: List[PageData] = []
        sections: List[SectionData] = []
        full_text_chunks: List[str] = []
        current_offset = 0

        for page_num, raw_text in raw_pages:
            normalized_page_text = cls.clean_text(raw_text)
            start_idx = current_offset
            end_idx = start_idx + len(normalized_page_text)
            page_words = cls.count_words(normalized_page_text)

            pages.append(
                PageData(
                    page_number=page_num,
                    text=normalized_page_text,
                    character_start=start_idx,
                    character_end=end_idx,
                    word_count=page_words,
                )
            )

            # Detect headings on this page
            for match in cls.SECTION_PATTERN.finditer(normalized_page_text):
                prefix = match.group(1).strip()
                title_rest = match.group(2).strip()
                full_title = f"{prefix}: {title_rest}" if title_rest else prefix
                section_offset = start_idx + match.start()
                sections.append(
                    SectionData(
                        title=full_title,
                        page_number=page_num,
                        character_offset=section_offset,
                    )
                )

            full_text_chunks.append(normalized_page_text)
            # Add separation delimiter length between pages for global document text (\n\n)
            current_offset = end_idx + 2

        full_document_text = "\n\n".join(full_text_chunks)
        return full_document_text, pages, sections


normalization_service = NormalizationService()
