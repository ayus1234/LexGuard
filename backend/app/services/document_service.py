from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.core.config import settings
    from app.core.logging import logger
    from app.core.security import generate_document_id, sanitize_filename, create_safe_temp_filepath
    from app.schemas.document import (
        DocumentResponse,
        DocumentMetadata,
        PageExtraction,
        SectionOutline,
    )
    from app.utils.file_validation import validate_file_content, LexGuardException, ExtractionFailedException
    from app.services.cleanup_service import cleanup_service
    from app.services.extraction_service import extraction_service
    from app.services.normalization_service import normalization_service
else:
    try:
        from backend.app.core.config import settings
        from backend.app.core.logging import logger
        from backend.app.core.security import generate_document_id, sanitize_filename, create_safe_temp_filepath
        from backend.app.schemas.document import (
            DocumentResponse,
            DocumentMetadata,
            PageExtraction,
            SectionOutline,
        )
        from backend.app.utils.file_validation import validate_file_content, LexGuardException, ExtractionFailedException
        from backend.app.services.cleanup_service import cleanup_service
        from backend.app.services.extraction_service import extraction_service
        from backend.app.services.normalization_service import normalization_service
    except ImportError:
        from app.core.config import settings
        from app.core.logging import logger
        from app.core.security import generate_document_id, sanitize_filename, create_safe_temp_filepath
        from app.schemas.document import (
            DocumentResponse,
            DocumentMetadata,
            PageExtraction,
            SectionOutline,
        )
        from app.utils.file_validation import validate_file_content, LexGuardException, ExtractionFailedException
        from app.services.cleanup_service import cleanup_service
        from app.services.extraction_service import extraction_service
        from app.services.normalization_service import normalization_service


class DocumentService:
    """
    Orchestrates the complete document ingestion pipeline:
    1. Validation: size limits, empty check, extension, and magic byte verification
    2. Secure temporary staging with UUID file paths
    3. Engine-specific text & structure extraction
    4. Text normalization and section heading detection with global grounding offsets
    5. Deterministic guaranteed temporary storage cleanup
    6. Response assembly matching DocumentResponse schema
    """

    @classmethod
    async def process_uploaded_document(
        cls, file_bytes: bytes, original_filename: str, mime_type: Optional[str] = None
    ) -> DocumentResponse:
        # 1. Validation
        file_type = validate_file_content(file_bytes, original_filename)
        safe_filename = sanitize_filename(original_filename)
        document_id = generate_document_id()
        sha256_hash = normalization_service.compute_sha256(file_bytes)

        # 2. Stage securely to isolated temporary file with UUID
        temp_filepath = create_safe_temp_filepath(suffix=f".{file_type}")
        try:
            temp_filepath.write_bytes(file_bytes)
            logger.info(
                f"Document staged for processing: id={document_id}, size={len(file_bytes)} bytes, type={file_type}"
            )

            # 3. Text Extraction
            try:
                raw_pages, engine_name = extraction_service.extract_document(temp_filepath, file_type)
            except LexGuardException:
                raise
            except Exception as e:
                logger.error(f"Failed to extract document {document_id}: {str(e)}")
                raise ExtractionFailedException(f"Failed to extract document: {str(e)}")

            # 4. Text Normalization and Grounding Offsets
            full_text, pages_data, sections_data = normalization_service.process_pages(raw_pages)

            # 5. Assemble Schema Models
            pages: list[PageExtraction] = [
                PageExtraction(
                    page_number=p.page_number,
                    text=p.text,
                    character_start=p.character_start,
                    character_end=p.character_end,
                    word_count=p.word_count,
                )
                for p in pages_data
            ]

            sections: list[SectionOutline] = [
                SectionOutline(
                    title=s.title,
                    page_number=s.page_number,
                    character_offset=s.character_offset,
                )
                for s in sections_data
            ]

            total_words = sum(p.word_count for p in pages)
            total_chars = len(full_text)
            page_count = len(pages) if pages else 1

            effective_mime = mime_type or (
                "application/pdf"
                if file_type == "pdf"
                else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                if file_type == "docx"
                else "text/plain"
            )

            metadata = DocumentMetadata(
                original_filename=safe_filename,
                file_size_bytes=len(file_bytes),
                mime_type=effective_mime,
                sha256_hash=sha256_hash,
                extraction_engine=engine_name,
                processed_at=datetime.now(timezone.utc),
            )

            response = DocumentResponse(
                document_id=document_id,
                filename=safe_filename,
                file_type=file_type,
                source_type="upload",
                page_count=page_count,
                word_count=total_words,
                character_count=total_chars,
                extracted_text=full_text,
                pages=pages,
                sections=sections,
                metadata=metadata,
                created_at=datetime.now(timezone.utc),
                processing_status="completed",
            )

            logger.info(
                f"Document processing completed: id={document_id}, pages={page_count}, words={total_words}"
            )
            return response

        finally:
            # 6. Guaranteed deterministic cleanup of host disk artifact
            cleanup_service.cleanup_file(temp_filepath)


document_service = DocumentService()
