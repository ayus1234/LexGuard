from datetime import datetime, timezone
from typing import List, Optional, Literal, TYPE_CHECKING
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from app.schemas.document import DocumentResponse
else:
    try:
        from backend.app.schemas.document import DocumentResponse
    except ImportError:
        from app.schemas.document import DocumentResponse


class BriefSourceCitation(BaseModel):
    page: Optional[int] = Field(None, description="1-indexed document page number")
    section: Optional[str] = Field(None, description="Contract section code or title")
    quoted_text: str = Field(..., description="Exact verbatim text quoted from the source document")
    character_start: Optional[int] = Field(None, description="Global character start index")
    character_end: Optional[int] = Field(None, description="Global character end index")
    verified: bool = Field(False, description="Whether citation was verified against ground-truth document text")


class KeyInformationItem(BaseModel):
    category: str = Field(..., description="Key information domain (e.g., 'PARTIES', 'TERM', 'LIABILITY', 'PAYMENT')")
    label: str = Field(..., description="Item descriptor")
    value: Optional[str] = Field(default=None, description="Document-stated value or null if unstated")
    source_reference: Optional[str] = Field(default=None, description="Section or page anchor")
    page: Optional[int] = Field(default=None, description="Page number")
    section: Optional[str] = Field(default=None, description="Section identifier")
    verified: bool = Field(default=False, description="Verification status")


class AttentionAreaItem(BaseModel):
    id: str = Field(..., description="Unique item identifier")
    title: str = Field(..., description="Descriptive headline of attention item")
    category: str = Field(..., description="Clause category")
    description: str = Field(..., description="Objective summary of what agreement states")
    why_it_matters: str = Field(..., description="Operational or financial impact warranting counsel review")
    review_level: Literal["review_recommended", "attention_warranted", "advisory_only"] = Field(
        ..., description="Standard non-definitive review taxonomy"
    )
    source_reference: Optional[str] = Field(default=None, description="Contract clause anchor")
    page: Optional[int] = Field(default=None, description="Page number")
    section: Optional[str] = Field(default=None, description="Section code")
    verified: bool = Field(default=False, description="Verification status")


class NegotiationPointItem(BaseModel):
    id: str = Field(..., description="Unique item identifier")
    title: str = Field(..., description="Negotiation discussion topic")
    category: str = Field(..., description="Clause category")
    current_provision: str = Field(..., description="Current contractual mechanism as stated in document")
    discussion_point: str = Field(..., description="Consideration or topic to explore with counsel")
    suggested_compromise: Optional[str] = Field(default=None, description="Sample compromise formulation for counsel prep")
    market_baseline: Optional[str] = Field(default=None, description="Commercial market baseline comparison")
    source_reference: Optional[str] = Field(default=None, description="Contract clause anchor")
    page: Optional[int] = Field(default=None, description="Page number")
    section: Optional[str] = Field(default=None, description="Section code")
    verified: bool = Field(default=False, description="Verification status")


class CounselQuestionItem(BaseModel):
    id: str = Field(..., description="Unique item identifier")
    priority: Literal["High", "Medium", "Standard"] = Field(default="Medium", description="Discussion priority")
    category: str = Field(..., description="Category topic")
    agenda_topic: str = Field(..., description="Focused agenda question for counsel consultation")
    why_discuss: str = Field(..., description="Context for counsel consultation")
    suggested_phrasing: Optional[str] = Field(default=None, description="Exact suggested phrasing for user to ask attorney")
    contract_citation: Optional[str] = Field(default=None, description="Contract anchor reference")
    market_standard: Optional[str] = Field(default=None, description="Market standard comparison")
    page: Optional[int] = Field(default=None, description="Page number")
    section: Optional[str] = Field(default=None, description="Section code")
    verified: bool = Field(default=False, description="Verification status")


class BriefChecklistItem(BaseModel):
    id: str = Field(..., description="Unique checklist identifier")
    section_index: int = Field(..., description="Section index: 1 (Financial), 2 (Liability), 3 (Governance), etc.")
    section_title: str = Field(..., description="Section heading")
    title: str = Field(..., description="Actionable verification directive")
    citation: str = Field(..., description="Source reference and impact context")
    badge_text: str = Field(..., description="Badge text: Urgent, High Attention, Medium, Scheduled, Verified")
    badge_variant: Literal["urgent", "high", "medium", "scheduled", "verified"] = Field(
        ..., description="Visual badge variant"
    )
    completed: bool = Field(default=False, description="Checklist item state")
    page: Optional[int] = Field(default=None, description="Page number")
    section: Optional[str] = Field(default=None, description="Section code")


class ImportantClauseItem(BaseModel):
    section: Optional[str] = Field(default=None, description="Section code or number")
    title: str = Field(..., description="Clause title")
    category: str = Field(..., description="Category")
    summary: str = Field(..., description="Plain-language factual summary")
    source_reference: Optional[str] = Field(default=None, description="Citation anchor")
    page: Optional[int] = Field(default=None, description="Page number")
    verified: bool = Field(default=False, description="Verification status")


class LawyerBrief(BaseModel):
    document_id: str = Field(..., description="Target document identifier")
    document_title: str = Field(..., description="Document filename or title")
    document_type: str = Field(..., description="Identified contract format")
    jurisdiction: Optional[str] = Field(None, description="Governing law jurisdiction if stated")
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    executive_summary: str = Field(..., description="Objective synthesis of agreement facts and commercial structure")
    key_information: List[KeyInformationItem] = Field(default_factory=list)
    attention_areas: List[AttentionAreaItem] = Field(default_factory=list)
    negotiation_points: List[NegotiationPointItem] = Field(default_factory=list)
    counsel_questions: List[CounselQuestionItem] = Field(default_factory=list)
    checklist: List[BriefChecklistItem] = Field(default_factory=list)
    important_clauses: List[ImportantClauseItem] = Field(default_factory=list)
    citations: List[BriefSourceCitation] = Field(default_factory=list)
    disclaimer: str = Field(
        default="LexGuard Counsel Preparation Brief is generated deterministically from provided document text for educational preparation. Not a formal legal opinion. Qualified corporate counsel must independently review all citations, redline proposals, and statutory assertions prior to contract execution."
    )
    model: str = Field(default="gemini-1.5-flash")
    citations_verified_count: int = Field(default=0)
    citations_unverified_count: int = Field(default=0)
    processing_time_ms: int = Field(default=0)


class LawyerBriefRequest(BaseModel):
    document_id: Optional[str] = Field(None, description="Identifier of target document")
    document: Optional[DocumentResponse] = Field(None, description="Optional full document response if not pre-persisted")
    brief: Optional[LawyerBrief] = Field(None, description="Optional pre-synthesized brief for direct export")


class LawyerBriefResponse(BaseModel):
    document_id: str
    brief: LawyerBrief
