import re
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.core.config import settings
    from app.schemas.document import DocumentResponse, PageExtraction, SectionOutline
    from app.schemas.retrieval import DocumentChunk, ChunkMetadata
else:
    try:
        from backend.app.core.config import settings
        from backend.app.schemas.document import DocumentResponse, PageExtraction, SectionOutline
        from backend.app.schemas.retrieval import DocumentChunk, ChunkMetadata
    except ImportError:
        from app.core.config import settings
        from app.schemas.document import DocumentResponse, PageExtraction, SectionOutline
        from app.schemas.retrieval import DocumentChunk, ChunkMetadata


class ChunkingService:
    """
    Structurally-aware legal document chunker.
    Splits along legal hierarchies (Sections, Articles, Paragraphs) while preserving:
    - Verbatim text slices
    - Global character offsets (character_start, character_end)
    - Source page boundaries (page_start, page_end)
    - Active legal section heading
    """

    def __init__(
        self,
        target_tokens: Optional[int] = None,
        overlap_tokens: Optional[int] = None,
        min_tokens: Optional[int] = None,
    ):
        self.target_chars = (target_tokens or settings.CHUNK_TARGET_SIZE) * 4
        self.overlap_chars = (overlap_tokens or settings.CHUNK_OVERLAP) * 4
        self.min_chars = (min_tokens or settings.MIN_CHUNK_SIZE) * 4

    def _find_section_for_offset(
        self, offset: int, sections: List[SectionOutline]
    ) -> Optional[str]:
        """Finds the most recent section heading that precedes or starts at offset."""
        active_section = None
        for s in sections:
            if s.character_offset <= offset:
                active_section = s.title
            else:
                break
        return active_section

    def _find_page_for_offset(
        self, offset: int, pages: List[PageExtraction], default_page: int = 1
    ) -> int:
        """Finds which 1-indexed page contains the given character offset."""
        for p in pages:
            if p.character_start <= offset <= p.character_end:
                return p.page_number
        return default_page

    def chunk_document(self, document: DocumentResponse) -> List[DocumentChunk]:
        full_text = document.extracted_text
        doc_id = document.document_id
        pages = document.pages
        sections = sorted(document.sections, key=lambda s: s.character_offset)

        if not full_text or not full_text.strip():
            return []

        # If document is smaller than target chunk size, return single comprehensive chunk
        if len(full_text) <= self.target_chars:
            p_start = self._find_page_for_offset(0, pages, 1)
            p_end = self._find_page_for_offset(len(full_text), pages, p_start)
            sec = self._find_section_for_offset(0, sections)
            metadata = ChunkMetadata(
                document_id=doc_id,
                chunk_id=f"{doc_id}_chk_0000",
                section=sec,
                page_start=p_start,
                page_end=p_end,
                character_start=0,
                character_end=len(full_text),
            )
            return [
                DocumentChunk(
                    chunk_id=f"{doc_id}_chk_0000",
                    document_id=doc_id,
                    chunk_index=0,
                    text=full_text,
                    section=sec,
                    page_start=p_start,
                    page_end=p_end,
                    character_start=0,
                    character_end=len(full_text),
                    token_estimate=max(1, len(full_text) // 4),
                    metadata=metadata,
                )
            ]

        # Identify natural split boundaries (paragraphs, double newlines, section headings)
        # We find paragraph spans (start_idx, end_idx) in full_text
        paragraphs: List[tuple[int, int]] = []
        for m in re.finditer(r'\S.*?(?=\n\s*\n|\Z)', full_text, flags=re.DOTALL):
            p_start = m.start()
            p_end = m.end()
            if p_end > p_start:
                paragraphs.append((p_start, p_end))

        if not paragraphs:
            paragraphs = [(0, len(full_text))]

        chunks: List[DocumentChunk] = []
        current_start = paragraphs[0][0]
        current_end = paragraphs[0][1]
        chunk_idx = 0

        section_offsets = {s.character_offset for s in sections}

        for i in range(1, len(paragraphs)):
            next_start, next_end = paragraphs[i]
            potential_len = next_end - current_start
            is_section_break = next_start in section_offsets

            # Check if we should finalize chunk:
            # 1. We reached target size and have minimum size
            # 2. Or we encountered a major section break and current chunk has sufficient size
            should_break = (
                potential_len > self.target_chars and (current_end - current_start) >= self.min_chars
            ) or (
                is_section_break and (current_end - current_start) >= self.min_chars
            )

            if should_break:
                # Slice verbatim text
                chunk_text = full_text[current_start:current_end]
                p_start = self._find_page_for_offset(current_start, pages, 1)
                p_end = self._find_page_for_offset(current_end, pages, p_start)
                sec = self._find_section_for_offset(current_start, sections)
                cid = f"{doc_id}_chk_{chunk_idx:04d}"

                metadata = ChunkMetadata(
                    document_id=doc_id,
                    chunk_id=cid,
                    section=sec,
                    page_start=p_start,
                    page_end=p_end,
                    character_start=current_start,
                    character_end=current_end,
                )

                chunks.append(
                    DocumentChunk(
                        chunk_id=cid,
                        document_id=doc_id,
                        chunk_index=chunk_idx,
                        text=chunk_text,
                        section=sec,
                        page_start=p_start,
                        page_end=p_end,
                        character_start=current_start,
                        character_end=current_end,
                        token_estimate=max(1, len(chunk_text) // 4),
                        metadata=metadata,
                    )
                )
                chunk_idx += 1

                # Start next chunk with clean sentence overlap if applicable
                current_start = next_start
                current_end = next_end
            else:
                current_end = next_end

        # Append final chunk
        if current_end > current_start:
            chunk_text = full_text[current_start:current_end]
            p_start = self._find_page_for_offset(current_start, pages, 1)
            p_end = self._find_page_for_offset(current_end, pages, p_start)
            sec = self._find_section_for_offset(current_start, sections)
            cid = f"{doc_id}_chk_{chunk_idx:04d}"

            metadata = ChunkMetadata(
                document_id=doc_id,
                chunk_id=cid,
                section=sec,
                page_start=p_start,
                page_end=p_end,
                character_start=current_start,
                character_end=current_end,
            )

            chunks.append(
                DocumentChunk(
                    chunk_id=cid,
                    document_id=doc_id,
                    chunk_index=chunk_idx,
                    text=chunk_text,
                    section=sec,
                    page_start=p_start,
                    page_end=p_end,
                    character_start=current_start,
                    character_end=current_end,
                    token_estimate=max(1, len(chunk_text) // 4),
                    metadata=metadata,
                )
            )

        return chunks


chunking_service = ChunkingService()
