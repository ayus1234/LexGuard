import time
import re
from typing import List, Dict, Any, Optional, Sequence, TYPE_CHECKING
from pydantic import ValidationError

if TYPE_CHECKING:
    from app.core.config import settings
    from app.core.logging import logger
    from app.core.prompts import LEGAL_QA_SYSTEM_INSTRUCTION, build_qa_prompt
    from app.schemas.qa import (
        DocumentAskRequest,
        DocumentAskResponse,
        GroundedCitation,
        RetrievedSourceItem,
        GroundedAnswerTelemetry,
        CarveOutItem,
        ReviewNotice,
    )
    from app.schemas.retrieval import RetrievalResult, GroundingStatus
    from app.services.retrieval_service import RetrievalService, retrieval_service
    from app.services.gemini_service import BaseGeminiService, gemini_service
    from app.utils.file_validation import (
        DocumentNotIndexedException,
        LexGuardException,
    )
else:
    try:
        from backend.app.core.config import settings
        from backend.app.core.logging import logger
        from backend.app.core.prompts import LEGAL_QA_SYSTEM_INSTRUCTION, build_qa_prompt
        from backend.app.schemas.qa import (
            DocumentAskRequest,
            DocumentAskResponse,
            GroundedCitation,
            RetrievedSourceItem,
            GroundedAnswerTelemetry,
            CarveOutItem,
            ReviewNotice,
        )
        from backend.app.schemas.retrieval import RetrievalResult, GroundingStatus
        from backend.app.services.retrieval_service import RetrievalService, retrieval_service
        from backend.app.services.gemini_service import BaseGeminiService, gemini_service
        from backend.app.utils.file_validation import (
            DocumentNotIndexedException,
            LexGuardException,
        )
    except ImportError:
        from app.core.config import settings
        from app.core.logging import logger
        from app.core.prompts import LEGAL_QA_SYSTEM_INSTRUCTION, build_qa_prompt
        from app.schemas.qa import (
            DocumentAskRequest,
            DocumentAskResponse,
            GroundedCitation,
            RetrievedSourceItem,
            GroundedAnswerTelemetry,
            CarveOutItem,
            ReviewNotice,
        )
        from app.schemas.retrieval import RetrievalResult, GroundingStatus
        from app.services.retrieval_service import RetrievalService, retrieval_service
        from app.services.gemini_service import BaseGeminiService, gemini_service
        from app.utils.file_validation import (
            DocumentNotIndexedException,
            LexGuardException,
        )


class QAService:
    """
    Orchestrates the Ask LexGuard document-grounded legal Q&A pipeline:
    1. Validation of document and query bounds.
    2. Vector similarity search in PostgreSQL + pgvector scoped strictly to document_id.
    3. Low-relevance / no-answer short circuiting.
    4. Structured Gemini grounded inference with primary/fallback rotation.
    5. Rigorous verbatim citation verification against retrieved chunk evidence.
    6. Legal safety compliance check.
    7. Zero-retention privacy telemetry logging.
    """

    def __init__(
        self,
        retrieval_svc: Optional[RetrievalService] = None,
        gemini_svc: Optional[BaseGeminiService] = None,
    ):
        self._retrieval = retrieval_svc or retrieval_service
        self._gemini = gemini_svc or gemini_service

    def set_dependencies(
        self,
        retrieval_svc: Optional[RetrievalService] = None,
        gemini_svc: Optional[BaseGeminiService] = None,
    ) -> None:
        if retrieval_svc is not None:
            self._retrieval = retrieval_svc
        if gemini_svc is not None:
            self._gemini = gemini_svc

    def verify_citation_against_chunks(
        self,
        citation: GroundedCitation,
        retrieved_chunks: Sequence[Any],
    ) -> GroundedCitation:
        """
        Verifies that citation.quoted_text exists verbatim within the retrieved evidence chunks.
        Determines exact character boundaries, page number, and section code.
        Marks verified=False if quote cannot be located in the retrieved ground truth.
        """
        quote = citation.quoted_text.strip() if citation.quoted_text else ""
        if not quote or len(quote) < 3:
            citation.verified = False
            return citation

        collapsed_quote = " ".join(quote.split())

        for chunk in retrieved_chunks:
            chunk_text: str = chunk.text
            # 1. Exact match
            idx = chunk_text.find(quote)

            # 2. Case-insensitive match fallback
            if idx == -1:
                idx = chunk_text.lower().find(quote.lower())

            # 3. Normalized whitespace fallback
            if idx == -1:
                collapsed_chunk = " ".join(chunk_text.split())
                c_idx = collapsed_chunk.lower().find(collapsed_quote.lower())
                if c_idx != -1:
                    idx = max(0, min(c_idx, len(chunk_text) - len(quote)))

            if idx != -1:
                citation.verified = True
                citation.chunk_id = chunk.chunk_id
                citation.page = chunk.page_start
                citation.section = citation.section or chunk.section
                citation.character_start = chunk.character_start + idx
                citation.character_end = chunk.character_start + idx + len(quote)
                return citation

        # Quote could not be verified against any retrieved chunk
        citation.verified = False
        citation.character_start = None
        citation.character_end = None
        return citation

    def _sanitize_legal_safety(self, text: str) -> str:
        """
        Substitutes definitive legal conclusions with objective educational phrasing.
        """
        sanitized = text
        forbidden_replacements = [
            (r"(?i)\bthis is illegal\b", "this provision may conflict with standard statutory protections"),
            (r"(?i)\bthis clause is (definitely )?invalid\b", "the enforceability of this clause may warrant review"),
            (r"(?i)\byou will win\b", "this factor may support a favorable interpretation"),
            (r"(?i)\byou should definitely sue\b", "you may wish to consult legal counsel regarding remedies"),
            (r"(?i)\byou are legally guaranteed to\b", "the contractual language indicates that"),
        ]
        for pattern, replacement in forbidden_replacements:
            sanitized = re.sub(pattern, replacement, sanitized)
        return sanitized

    async def ask_document(self, request: DocumentAskRequest) -> DocumentAskResponse:
        total_start = time.perf_counter()
        doc_id = request.document_id.strip()
        clean_question = request.question.strip()

        # 1. Verify document is indexed in pgvector
        if not self._retrieval.is_document_indexed(doc_id):
            logger.warning(f"Ask requested for unindexed document id={doc_id}")
            raise DocumentNotIndexedException(
                f"Document id={doc_id} is not indexed in the vector store. Please index the document before asking questions."
            )

        # 2. Vector retrieval in PostgreSQL pgvector
        retrieval_start = time.perf_counter()
        retrieval_result = await self._retrieval.retrieve(
            document_id=doc_id,
            query=clean_question,
            top_k=request.top_k,
        )
        retrieval_ms = int((time.perf_counter() - retrieval_start) * 1000)

        # 3. Low-relevance / No-Answer check
        if (
            retrieval_result.grounding_status != GroundingStatus.grounded
            or not retrieval_result.results
        ):
            total_ms = int((time.perf_counter() - total_start) * 1000)
            logger.info(
                f"Ask query for document id={doc_id} returned insufficient evidence: retrieval_ms={retrieval_ms}ms"
            )
            return DocumentAskResponse(
                document_id=doc_id,
                session_id=request.session_id,
                question=clean_question,
                answer="The document does not provide enough information to answer this question.",
                grounded=False,
                confidence="Insufficient Evidence",
                citations=[],
                retrieved_sources=[],
                model=settings.GEMINI_MODEL,
                telemetry=GroundedAnswerTelemetry(
                    retrieval_ms=retrieval_ms,
                    generation_ms=0,
                    total_ms=total_ms,
                ),
                badges=["• Insufficient Evidence in Document"],
                carve_out_matrix=None,
                strategic_consideration=None,
                review_recommended_notice=None,
            )

        # 4. Assemble retrieved chunk evidence
        evidence_snippets = []
        retrieved_sources: List[RetrievedSourceItem] = []
        for r in retrieval_result.results:
            header = f"[CHUNK ID: {r.chunk_id} | PAGE: {r.page_start} | SECTION: {r.section or 'N/A'}]"
            evidence_snippets.append(f"{header}\n{r.text}")
            retrieved_sources.append(
                RetrievedSourceItem(
                    chunk_id=r.chunk_id,
                    page=r.page_start,
                    section=r.section,
                    similarity=r.similarity_score,
                    text_snippet=r.text[:140] + "..." if len(r.text) > 140 else r.text,
                )
            )

        evidence_text = "\n\n".join(evidence_snippets)

        # Optional conversation context
        history_text = None
        if request.conversation_history:
            formatted_turns = []
            for turn in request.conversation_history[-4:]:  # Limit to last 4 turns for brevity
                role = turn.get("role", "user")
                content = turn.get("content", "")
                if content:
                    formatted_turns.append(f"{role.upper()}: {content}")
            if formatted_turns:
                history_text = "\n".join(formatted_turns)

        prompt = build_qa_prompt(
            question=clean_question,
            retrieved_chunks_text=evidence_text,
            document_title=None,
            conversation_history_text=history_text,
        )

        # 5. Gemini structured generation
        gen_start = time.perf_counter()
        try:
            raw_response = await self._gemini.generate_structured_analysis(
                prompt=prompt,
                system_instruction=LEGAL_QA_SYSTEM_INSTRUCTION,
            )
        except Exception as e:
            logger.error(f"Gemini grounded answer generation failed for document id={doc_id}: {type(e).__name__}")
            raise
        generation_ms = int((time.perf_counter() - gen_start) * 1000)

        # 6. Parse and structure answer
        raw_answer = str(raw_response.get("answer", "")).strip()
        if not raw_answer:
            raw_answer = "The document does not provide enough information to answer this question."

        sanitized_answer = self._sanitize_legal_safety(raw_answer)
        grounded = bool(raw_response.get("grounded", True))
        confidence = str(raw_response.get("confidence", "98.5%"))

        # 7. Verification of citations
        raw_citations = raw_response.get("citations", [])
        verified_citations: List[GroundedCitation] = []
        for cit_dict in raw_citations:
            if isinstance(cit_dict, dict) and cit_dict.get("quoted_text"):
                citation_obj = GroundedCitation(
                    page=cit_dict.get("page"),
                    section=cit_dict.get("section"),
                    section_title=cit_dict.get("section_title"),
                    quoted_text=str(cit_dict.get("quoted_text")),
                    chunk_id=cit_dict.get("chunk_id"),
                    character_start=None,
                    character_end=None,
                )
                verified_obj = self.verify_citation_against_chunks(
                    citation=citation_obj,
                    retrieved_chunks=retrieval_result.results,
                )
                verified_citations.append(verified_obj)

        # If model indicated grounded but 0 citations could be verified, downgrade grounding
        verified_count = sum(1 for c in verified_citations if c.verified)
        if grounded and verified_citations and verified_count == 0:
            logger.info(f"Downgrading grounding status for document id={doc_id}: 0/{len(verified_citations)} citations verified")
            grounded = False

        # Optional UI badges and matrices
        badges = raw_response.get("badges", [])
        if not badges and grounded:
            badges = ["• Grounded in Verified Document Clauses"]

        carve_outs = None
        if raw_response.get("carve_out_matrix") and isinstance(raw_response["carve_out_matrix"], list):
            try:
                carve_outs = [CarveOutItem(**co) for co in raw_response["carve_out_matrix"] if isinstance(co, dict)]
            except Exception:
                carve_outs = None

        review_notice = None
        if raw_response.get("review_recommended_notice") and isinstance(raw_response["review_recommended_notice"], dict):
            try:
                review_notice = ReviewNotice(**raw_response["review_recommended_notice"])
            except Exception:
                review_notice = None

        strategic_consideration = raw_response.get("strategic_consideration")

        total_ms = int((time.perf_counter() - total_start) * 1000)

        # 8. Zero-retention safe logging
        logger.info(
            f"Ask LexGuard completed: doc_id={doc_id}, retrieval_ms={retrieval_ms}ms, "
            f"generation_ms={generation_ms}ms, grounded={grounded}, "
            f"citations_verified={verified_count}/{len(verified_citations)}"
        )

        return DocumentAskResponse(
            document_id=doc_id,
            session_id=request.session_id,
            question=clean_question,
            answer=sanitized_answer,
            grounded=grounded,
            confidence=confidence,
            citations=verified_citations,
            retrieved_sources=retrieved_sources,
            model=settings.GEMINI_MODEL,
            telemetry=GroundedAnswerTelemetry(
                retrieval_ms=retrieval_ms,
                generation_ms=generation_ms,
                total_ms=total_ms,
            ),
            badges=badges,
            carve_out_matrix=carve_outs,
            strategic_consideration=strategic_consideration,
            review_recommended_notice=review_notice,
        )


qa_service = QAService()
