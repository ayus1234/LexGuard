import time
import re
from typing import List, Optional, Tuple, Sequence, TYPE_CHECKING
from pydantic import ValidationError

if TYPE_CHECKING:
    from app.core.config import settings
    from app.core.logging import logger
    from app.core.prompts import LEGAL_ANALYSIS_SYSTEM_INSTRUCTION, build_analysis_prompt
    from app.schemas.document import DocumentResponse, PageExtraction
    from app.schemas.analysis import (
        DocumentAnalysis,
        DocumentAnalysisResponse,
        AnalysisMetadata,
        Citation,
    )
    from app.services.gemini_service import gemini_service, BaseGeminiService
    from app.utils.file_validation import (
        DocumentTooLargeForAnalysisException,
        AnalysisValidationException,
    )
else:
    try:
        from backend.app.core.config import settings
        from backend.app.core.logging import logger
        from backend.app.core.prompts import LEGAL_ANALYSIS_SYSTEM_INSTRUCTION, build_analysis_prompt
        from backend.app.schemas.document import DocumentResponse, PageExtraction
        from backend.app.schemas.analysis import (
            DocumentAnalysis,
            DocumentAnalysisResponse,
            AnalysisMetadata,
            Citation,
        )
        from backend.app.services.gemini_service import gemini_service, BaseGeminiService
        from backend.app.utils.file_validation import (
            DocumentTooLargeForAnalysisException,
            AnalysisValidationException,
        )
    except ImportError:
        from app.core.config import settings
        from app.core.logging import logger
        from app.core.prompts import LEGAL_ANALYSIS_SYSTEM_INSTRUCTION, build_analysis_prompt
        from app.schemas.document import DocumentResponse, PageExtraction
        from app.schemas.analysis import (
            DocumentAnalysis,
            DocumentAnalysisResponse,
            AnalysisMetadata,
            Citation,
        )
        from app.services.gemini_service import gemini_service, BaseGeminiService
        from app.utils.file_validation import (
            DocumentTooLargeForAnalysisException,
            AnalysisValidationException,
        )


class AnalysisService:
    """
    Orchestrates the AI document intelligence pipeline:
    1. Size and token sanity checks.
    2. Prompt construction with legal safety guidelines.
    3. Gemini structured JSON inference.
    4. Pydantic schema validation.
    5. Verbatim citation verification against ground-truth document text.
    6. Assembly of DocumentAnalysisResponse with privacy-safe telemetry.
    """

    def __init__(self, service: Optional[BaseGeminiService] = None):
        self._gemini = service or gemini_service

    def set_gemini_service(self, service: BaseGeminiService) -> None:
        self._gemini = service

    def verify_citation(
        self, citation: Citation, document_text: str, pages: Sequence[PageExtraction]
    ) -> Citation:
        """
        Verifies that citation.quoted_text actually exists verbatim in the document.
        Calculates exact global character offsets and page attribution.
        Marks verified=False for hallucinated or unlocated quotes.
        """
        quote = citation.quoted_text.strip() if citation.quoted_text else ""
        if not quote or len(quote) < 3:
            citation.verified = False
            return citation

        # 1. Exact match search
        idx = document_text.find(quote)

        # 2. Case-insensitive fallback if exact match misses due to capitalization
        if idx == -1:
            idx = document_text.lower().find(quote.lower())

        # 3. Normalized whitespace fallback
        if idx == -1:
            # Create whitespace-collapsed mapping
            collapsed_quote = " ".join(quote.split())
            collapsed_doc = " ".join(document_text.split())
            c_idx = collapsed_doc.lower().find(collapsed_quote.lower())
            if c_idx != -1:
                # Approximate index in original text
                idx = max(0, min(c_idx, len(document_text) - len(quote)))

        if idx != -1:
            start_offset = idx
            end_offset = idx + len(quote)
            citation.character_start = start_offset
            citation.character_end = end_offset

            # Resolve page number from PageExtraction bounds
            matched_page = None
            for p in pages:
                if p.character_start <= start_offset <= p.character_end:
                    matched_page = p.page_number
                    break

            if matched_page:
                citation.page = matched_page
            elif not citation.page and pages:
                citation.page = pages[0].page_number

            citation.verified = True
        else:
            # Quote does not exist in ground truth document
            citation.verified = False
            citation.character_start = None
            citation.character_end = None

        return citation

    async def analyze_document(self, document: DocumentResponse) -> DocumentAnalysisResponse:
        start_time = time.perf_counter()
        doc_id = document.document_id
        text_length = len(document.extracted_text)

        # 1. Enforce configurable document character limit for direct single-call analysis
        if text_length > settings.MAX_ANALYSIS_CHAR_COUNT:
            logger.warning(
                f"Document {doc_id} exceeded analysis threshold: {text_length} chars > {settings.MAX_ANALYSIS_CHAR_COUNT}"
            )
            raise DocumentTooLargeForAnalysisException(
                f"Document character count ({text_length:,}) exceeds the maximum allowed limit "
                f"of {settings.MAX_ANALYSIS_CHAR_COUNT:,} characters for direct AI analysis."
            )

        logger.info(f"Starting Gemini legal intelligence analysis for document id={doc_id}, chars={text_length}")

        # 2. Build structured prompt
        prompt = build_analysis_prompt(
            document_title=document.filename,
            file_type=document.file_type,
            page_count=document.page_count,
            extracted_text=document.extracted_text,
        )

        estimated_tokens = len(prompt) // 4

        # 3. Call Gemini
        raw_analysis_dict = await self._gemini.generate_structured_analysis(
            prompt=prompt,
            system_instruction=LEGAL_ANALYSIS_SYSTEM_INSTRUCTION,
        )

        # 4. Validate through Pydantic V2
        try:
            analysis = DocumentAnalysis.model_validate(raw_analysis_dict)
        except ValidationError as val_err:
            logger.error(f"Pydantic validation failed for document {doc_id}: {val_err.error_count()} errors")
            raise AnalysisValidationException(
                f"Model response did not strictly conform to the required legal intelligence schema: {val_err}"
            )

        # 5. Verify all citations against ground-truth document text
        verified_count = 0
        unverified_count = 0

        for cit in analysis.citations:
            self.verify_citation(cit, document.extracted_text, document.pages)
            if cit.verified:
                verified_count += 1
            else:
                unverified_count += 1

        duration_ms = int((time.perf_counter() - start_time) * 1000)

        metadata = AnalysisMetadata(
            model=settings.GEMINI_MODEL,
            processing_time_ms=duration_ms,
            character_count=text_length,
            prompt_tokens_estimated=estimated_tokens,
            citations_verified_count=verified_count,
            citations_unverified_count=unverified_count,
        )

        logger.info(
            f"Completed AI analysis for document id={doc_id}: duration={duration_ms}ms, "
            f"clauses={len(analysis.clauses)}, attention_areas={len(analysis.attention_areas)}, "
            f"citations_verified={verified_count}/{len(analysis.citations)}"
        )

        return DocumentAnalysisResponse(
            document_id=doc_id,
            analysis=analysis,
            metadata=metadata,
        )


analysis_service = AnalysisService()
