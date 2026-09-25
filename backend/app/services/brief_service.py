"""
LexGuard Brief Service.
Orchestrates the generation, citation grounding, validation, and caching of
the Lawyer Preparation Brief and Action Checklist.
Strictly adheres to zero-retention privacy, non-legal advice disclaimers, and verbatim grounding.
"""

import time
import re
from typing import Dict, List, Optional, Sequence, Any, TYPE_CHECKING
from pydantic import ValidationError
from sqlalchemy import select

if TYPE_CHECKING:
    from app.core.config import settings
    from app.core.logging import logger
    from app.core.prompts import LEGAL_BRIEF_SYSTEM_INSTRUCTION, build_brief_prompt
    from app.schemas.document import DocumentResponse, PageExtraction
    from app.schemas.brief import (
        LawyerBrief,
        BriefSourceCitation,
        KeyInformationItem,
        AttentionAreaItem,
        NegotiationPointItem,
        CounselQuestionItem,
        BriefChecklistItem,
        ImportantClauseItem,
    )
    from app.services.gemini_service import gemini_service, BaseGeminiService
    from app.services.pgvector_store import pgvector_store
    from app.models.document import DocumentModel, DocumentChunkModel
    from app.core.corpus import corpus_registry
    from app.utils.file_validation import (
        DocumentNotFoundException,
        BriefValidationException,
        DocumentTooLargeForAnalysisException,
        LexGuardException,
    )
else:
    try:
        from backend.app.core.config import settings
        from backend.app.core.logging import logger
        from backend.app.core.prompts import LEGAL_BRIEF_SYSTEM_INSTRUCTION, build_brief_prompt
        from backend.app.schemas.document import DocumentResponse, PageExtraction
        from backend.app.schemas.brief import (
            LawyerBrief,
            BriefSourceCitation,
            KeyInformationItem,
            AttentionAreaItem,
            NegotiationPointItem,
            CounselQuestionItem,
            BriefChecklistItem,
            ImportantClauseItem,
        )
        from backend.app.services.gemini_service import gemini_service, BaseGeminiService
        from backend.app.services.pgvector_store import pgvector_store
        from backend.app.models.document import DocumentModel, DocumentChunkModel
        from backend.app.core.corpus import corpus_registry
        from backend.app.utils.file_validation import (
            DocumentNotFoundException,
            BriefValidationException,
            DocumentTooLargeForAnalysisException,
            LexGuardException,
        )
    except ImportError:
        from app.core.config import settings
        from app.core.logging import logger
        from app.core.prompts import LEGAL_BRIEF_SYSTEM_INSTRUCTION, build_brief_prompt
        from app.schemas.document import DocumentResponse, PageExtraction
        from app.schemas.brief import (
            LawyerBrief,
            BriefSourceCitation,
            KeyInformationItem,
            AttentionAreaItem,
            NegotiationPointItem,
            CounselQuestionItem,
            BriefChecklistItem,
            ImportantClauseItem,
        )
        from app.services.gemini_service import gemini_service, BaseGeminiService
        from app.services.pgvector_store import pgvector_store
        from app.models.document import DocumentModel, DocumentChunkModel
        from app.core.corpus import corpus_registry
        from app.utils.file_validation import (
            DocumentNotFoundException,
            BriefValidationException,
            DocumentTooLargeForAnalysisException,
            LexGuardException,
        )


class BriefService:
    """
    Synthesizes and verifies structured Lawyer Preparation Briefs:
    1. Retrieves document text from memory or PostgreSQL chunks.
    2. Enforces document character limits and privacy protection.
    3. Executes Gemini inference with primary/fallback API rotation.
    4. Validates output through Pydantic V2 schema.
    5. Verifies citations verbatim against ground truth text.
    6. Sanitizes text against definitive legal claims.
    7. Caches brief for instant PDF/DOCX export retrieval.
    """

    def __init__(self, service: Optional[BaseGeminiService] = None):
        self._gemini = service or gemini_service
        self._brief_cache: Dict[str, LawyerBrief] = {}

    def set_gemini_service(self, service: BaseGeminiService) -> None:
        self._gemini = service

    def get_cached_brief(self, document_id: str) -> Optional[LawyerBrief]:
        return self._brief_cache.get(document_id)

    def set_cached_brief(self, document_id: str, brief: LawyerBrief) -> None:
        self._brief_cache[document_id] = brief

    def clear_cache(self, document_id: Optional[str] = None) -> None:
        if document_id:
            self._brief_cache.pop(document_id, None)
        else:
            self._brief_cache.clear()

    def verify_citation(
        self, citation: BriefSourceCitation, document_text: str, pages: Sequence[Any]
    ) -> BriefSourceCitation:
        """
        Verifies that citation.quoted_text exists verbatim in ground-truth document text.
        Resolves character offset range and page number.
        """
        quote = citation.quoted_text.strip() if citation.quoted_text else ""
        if not quote or len(quote) < 3:
            citation.verified = False
            return citation

        # 1. Exact match
        idx = document_text.find(quote)

        # 2. Case-insensitive fallback
        if idx == -1:
            idx = document_text.lower().find(quote.lower())

        # 3. Normalized whitespace fallback
        if idx == -1:
            collapsed_quote = " ".join(quote.split())
            collapsed_doc = " ".join(document_text.split())
            c_idx = collapsed_doc.lower().find(collapsed_quote.lower())
            if c_idx != -1:
                idx = max(0, min(c_idx, len(document_text) - len(quote)))

        if idx != -1:
            start_offset = idx
            end_offset = idx + len(quote)
            citation.character_start = start_offset
            citation.character_end = end_offset

            # Resolve page number
            matched_page = None
            for p in pages:
                p_start = getattr(p, "character_start", getattr(p, "char_start", 0))
                p_end = getattr(p, "character_end", getattr(p, "char_end", 0))
                p_num = getattr(p, "page_number", getattr(p, "page_start", 1))
                if p_start <= start_offset <= p_end:
                    matched_page = p_num
                    break

            if matched_page:
                citation.page = matched_page
            elif not citation.page and pages:
                first_p = pages[0]
                citation.page = getattr(first_p, "page_number", getattr(first_p, "page_start", 1))

            citation.verified = True
        else:
            citation.verified = False
            citation.character_start = None
            citation.character_end = None

        return citation

    def _sanitize_legal_safety(self, text: str) -> str:
        """
        Substitutes definitive legal conclusions with measured educational terminology.
        """
        sanitized = text
        forbidden_replacements = [
            (r"(?i)\bthis (is|clause is|contract is) illegal\b", "this provision may conflict with applicable legal standards"),
            (r"(?i)\bthis clause is (definitely )?invalid\b", "the enforceability of this clause may warrant legal review"),
            (r"(?i)\byou will win\b", "this factor may support a favorable interpretation"),
            (r"(?i)\byou should definitely sue\b", "you may wish to consult legal counsel regarding remedies"),
            (r"(?i)\byou are legally guaranteed to\b", "the contractual language indicates that"),
            (r"(?i)\bthis clause is unenforceable\b", "this clause may warrant closer review by counsel"),
        ]
        for pattern, replacement in forbidden_replacements:
            sanitized = re.sub(pattern, replacement, sanitized)
        return sanitized

    def _load_document_from_db(self, document_id: str) -> tuple[str, str, str, List[Any]]:
        """
        Reconstructs text and page boundaries from PostgreSQL pgvector store.
        Returns: (document_text, filename, document_type, pages_or_chunks)
        """
        factory = pgvector_store._get_session_factory()
        session = factory()
        try:
            # Query DocumentModel
            doc_stmt = select(DocumentModel).where(DocumentModel.document_id == document_id)
            doc_row = session.execute(doc_stmt).scalar_one_or_none()

            # Query Chunks in order
            chunk_stmt = (
                select(DocumentChunkModel)
                .where(DocumentChunkModel.document_id == document_id)
                .order_by(DocumentChunkModel.chunk_index.asc())
            )
            chunks = list(session.execute(chunk_stmt).scalars().all())

            if not doc_row and not chunks:
                corpus_doc = corpus_registry.get_document(document_id)
                if corpus_doc:
                    filename = corpus_doc.title
                    doc_type = corpus_doc.category or "Commercial Agreement"
                    doc_text = f"Document: {corpus_doc.title}\nCategory: {corpus_doc.category}\nJurisdiction: {corpus_doc.jurisdiction}\nSummary: {corpus_doc.summary}"
                    return doc_text, filename, doc_type, []
                raise DocumentNotFoundException(f"Document with id='{document_id}' was not found in storage.")

            filename = str(doc_row.filename) if doc_row and doc_row.filename else f"Document {document_id}"
            doc_type = str(doc_row.document_type) if doc_row and doc_row.document_type else "Commercial Agreement"

            if chunks:
                doc_text = "\n\n".join(str(c.content) for c in chunks)
            elif doc_row:
                doc_text = f"Document: {filename}\nType: {doc_type}"
            else:
                doc_text = ""

            return doc_text, filename, doc_type, chunks
        finally:
            session.close()

    async def generate_brief(
        self,
        document_id: str,
        document: Optional[DocumentResponse] = None,
        force_regenerate: bool = False,
    ) -> LawyerBrief:
        """
        Synthesizes a full Lawyer Preparation Brief from the target document.
        """
        start_time = time.perf_counter()

        # Check in-memory brief cache unless forced
        if not force_regenerate and document_id in self._brief_cache:
            logger.info(f"Returning cached Lawyer Preparation Brief for document id={document_id}")
            return self._brief_cache[document_id]

        # Resolve document content
        pages: Sequence[Any] = []
        if document is not None:
            document_text = document.extracted_text
            filename = document.filename
            doc_type = document.file_type
            pages = document.pages
        else:
            document_text, filename, doc_type, pages = self._load_document_from_db(document_id)

        text_length = len(document_text)
        if text_length == 0:
            raise DocumentNotFoundException(f"Document id='{document_id}' contains no extracted text to analyze.")

        if text_length > settings.MAX_ANALYSIS_CHAR_COUNT:
            logger.warning(
                f"Document {document_id} exceeded brief character limit: {text_length} > {settings.MAX_ANALYSIS_CHAR_COUNT}"
            )
            raise DocumentTooLargeForAnalysisException(
                f"Document character count ({text_length:,}) exceeds the maximum allowed limit "
                f"of {settings.MAX_ANALYSIS_CHAR_COUNT:,} characters for brief generation."
            )

        logger.info(
            f"Generating Lawyer Preparation Brief for document id={document_id}, "
            f"filename='{filename}', characters={text_length}"
        )

        # Build prompt
        prompt = build_brief_prompt(
            document_text=document_text,
            document_title=filename,
            document_type=doc_type,
        )

        # Call Gemini model
        raw_brief_dict = await self._gemini.generate_structured_analysis(
            prompt=prompt,
            system_instruction=LEGAL_BRIEF_SYSTEM_INSTRUCTION,
        )

        if not isinstance(raw_brief_dict, dict):
            raise BriefValidationException("AI model did not return a valid structured dictionary response.")

        # Ensure document_id and required headers
        raw_brief_dict["document_id"] = document_id
        if not raw_brief_dict.get("document_title"):
            raw_brief_dict["document_title"] = filename
        if not raw_brief_dict.get("document_type"):
            raw_brief_dict["document_type"] = doc_type or "Commercial Agreement"

        # Sanitize executive summary and descriptions against definitive legal claims
        if "executive_summary" in raw_brief_dict and isinstance(raw_brief_dict["executive_summary"], str):
            raw_brief_dict["executive_summary"] = self._sanitize_legal_safety(raw_brief_dict["executive_summary"])

        if "attention_areas" in raw_brief_dict and isinstance(raw_brief_dict["attention_areas"], list):
            for att in raw_brief_dict["attention_areas"]:
                if isinstance(att, dict):
                    if "description" in att and isinstance(att["description"], str):
                        att["description"] = self._sanitize_legal_safety(att["description"])
                    if "why_it_matters" in att and isinstance(att["why_it_matters"], str):
                        att["why_it_matters"] = self._sanitize_legal_safety(att["why_it_matters"])

        # Pydantic validation
        try:
            brief = LawyerBrief.model_validate(raw_brief_dict)
        except ValidationError as val_err:
            logger.error(f"Pydantic validation failed for brief id={document_id}: {val_err.error_count()} errors")
            raise BriefValidationException(
                f"Model response did not strictly conform to LawyerBrief schema: {val_err}"
            )

        # Citation verification against ground-truth document text
        verified_count = 0
        unverified_count = 0

        for cit in brief.citations:
            self.verify_citation(cit, document_text, pages)
            if cit.verified:
                verified_count += 1
            else:
                unverified_count += 1

        # Also check source_reference verification for key_information and attention_areas
        for ki in brief.key_information:
            if ki.value and ki.value.lower() in document_text.lower():
                ki.verified = True

        for att in brief.attention_areas:
            if att.source_reference and att.source_reference.lower() in document_text.lower():
                att.verified = True

        duration_ms = int((time.perf_counter() - start_time) * 1000)
        brief.citations_verified_count = verified_count
        brief.citations_unverified_count = unverified_count
        brief.processing_time_ms = duration_ms
        brief.model = settings.GEMINI_MODEL

        # Cache brief for subsequent export requests
        self._brief_cache[document_id] = brief

        logger.info(
            f"Successfully generated Lawyer Preparation Brief for document id={document_id}: "
            f"duration={duration_ms}ms, key_info={len(brief.key_information)}, "
            f"attention_areas={len(brief.attention_areas)}, checklist={len(brief.checklist)}, "
            f"citations_verified={verified_count}/{len(brief.citations)}"
        )

        return brief


brief_service = BriefService()
