from enum import Enum
from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

try:
    from .document import DocumentResponse
except ImportError:
    try:
        from backend.app.schemas.document import DocumentResponse
    except ImportError:
        from app.schemas.document import DocumentResponse


class ImportanceLevel(str, Enum):
    high = "high"
    medium = "medium"
    standard = "standard"


class ReviewLevel(str, Enum):
    review_recommended = "review_recommended"
    attention_warranted = "attention_warranted"
    advisory_only = "advisory_only"


class ClauseCategory(str, Enum):
    liability = "Liability"
    indemnification = "Indemnification"
    intellectual_property = "Intellectual Property"
    confidentiality = "Confidentiality"
    payment = "Payment"
    termination = "Termination"
    renewal = "Renewal"
    data_privacy = "Data Privacy"
    security = "Security"
    dispute_resolution = "Dispute Resolution"
    governing_law = "Governing Law"
    service_levels = "Service Levels"
    restrictions = "Restrictions"
    other = "Other"


class Party(BaseModel):
    name: str = Field(..., description="Entity or individual name identified in the agreement")
    role: str = Field(..., description="Role in agreement (e.g. 'Disclosing Party', 'Vendor', 'Client')")


class KeyInformation(BaseModel):
    category: str = Field(..., description="Domain category (e.g., 'Dates & Term', 'Financial', 'Governance')")
    label: str = Field(..., description="Metric or provision label (e.g., 'Governing Law', 'Payment Term')")
    value: Optional[str] = Field(None, description="Extracted value or null if not identified")
    source_reference: Optional[str] = Field(None, description="Anchor section or page where value is located")


class Clause(BaseModel):
    section: Optional[str] = Field(None, description="Section identifier (e.g., 'Section 8.3', 'ARTICLE IV')")
    title: str = Field(..., description="Descriptive title of the clause")
    category: ClauseCategory = Field(..., description="Taxonomy classification for the clause")
    importance: ImportanceLevel = Field(..., description="AI-generated review prioritization level")
    plain_language_summary: str = Field(..., description="Clear, non-technical explanation of clause effect")
    source_reference: Optional[str] = Field(None, description="Text snippet anchor or section citation")


class AttentionArea(BaseModel):
    title: str = Field(..., description="Identified focus area (e.g., 'Asymmetric Indemnification Obligations')")
    description: str = Field(..., description="Objective description of the contractual mechanism")
    why_it_may_matter: str = Field(..., description="Educational explanation of potential implications")
    source_reference: Optional[str] = Field(None, description="Direct section citation")
    review_level: ReviewLevel = Field(
        default=ReviewLevel.review_recommended,
        description="Recommended attention tier (non-definitive advisory)",
    )


class Citation(BaseModel):
    page: Optional[int] = Field(None, description="1-indexed document page number")
    section: Optional[str] = Field(None, description="Section identifier if identifiable")
    quoted_text: str = Field(..., description="Verbatim text quotation from document")
    character_start: Optional[int] = Field(None, description="Exact global character start offset")
    character_end: Optional[int] = Field(None, description="Exact global character end offset")
    verified: bool = Field(default=False, description="True if quoted text was verified against ground truth")


class DocumentAnalysis(BaseModel):
    document_summary: str = Field(..., description="Plain-English synthesized executive summary")
    document_type: str = Field(..., description="Identified contract type (e.g. 'Mutual Non-Disclosure Agreement')")
    jurisdiction: Optional[str] = Field(None, description="Governing jurisdiction or choice of law if stated")
    parties: List[Party] = Field(default_factory=list, description="Parties bound by agreement")
    key_information: List[KeyInformation] = Field(default_factory=list, description="Essential factual data points")
    clauses: List[Clause] = Field(default_factory=list, description="Categorized substantive clauses")
    attention_areas: List[AttentionArea] = Field(default_factory=list, description="Areas warranting human review")
    citations: List[Citation] = Field(default_factory=list, description="Verbatim supporting citations")


class AnalysisMetadata(BaseModel):
    model: str = Field(..., description="Underlying Gemini model utilized (e.g. 'gemini-1.5-flash')")
    processing_time_ms: int = Field(..., description="Total wall-clock analysis duration in milliseconds")
    character_count: int = Field(..., description="Total character length of analyzed document text")
    prompt_tokens_estimated: int = Field(..., description="Estimated token count consumed by analysis prompt")
    citations_verified_count: int = Field(default=0, description="Total citations verified against ground truth text")
    citations_unverified_count: int = Field(default=0, description="Total citations failed ground truth verification")
    analyzed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DocumentAnalysisResponse(BaseModel):
    document_id: str = Field(..., description="Internal identifier of analyzed document")
    analysis: DocumentAnalysis = Field(..., description="Structured legal intelligence data")
    metadata: AnalysisMetadata = Field(..., description="Execution telemetry and citation verification stats")


class DocumentAnalysisRequest(BaseModel):
    document: DocumentResponse = Field(..., description="Normalized document representation from ingestion pipeline")
