from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class GroundedCitation(BaseModel):
    page: Optional[int] = Field(default=None, description="1-indexed document page number where evidence was located")
    section: Optional[str] = Field(default=None, description="Section code or clause identifier (e.g., '§ 8.3')")
    section_title: Optional[str] = Field(default=None, description="Title of the section if identifiable")
    quoted_text: str = Field(..., description="Exact verbatim excerpt from source document")
    chunk_id: Optional[str] = Field(default=None, description="Identifier of the source chunk")
    character_start: Optional[int] = Field(default=None, description="Global character start coordinate in document")
    character_end: Optional[int] = Field(default=None, description="Global character end coordinate in document")
    verified: bool = Field(default=False, description="True if quoted text was verified against ground truth")


class RetrievedSourceItem(BaseModel):
    chunk_id: str = Field(..., description="Retrieved chunk identifier")
    page: int = Field(..., description="1-indexed page number where chunk starts")
    section: Optional[str] = Field(default=None, description="Section heading associated with chunk")
    similarity: float = Field(..., description="Normalized cosine similarity score (0.0 to 1.0)")
    text_snippet: Optional[str] = Field(default=None, description="Truncated chunk text snippet for display")


class GroundedAnswerTelemetry(BaseModel):
    retrieval_ms: int = Field(..., description="Wall-clock milliseconds for vector search")
    generation_ms: int = Field(..., description="Wall-clock milliseconds for Gemini generation")
    total_ms: int = Field(..., description="Total wall-clock duration in milliseconds")


class CarveOutItem(BaseModel):
    type: str = Field(default="standard", description="'urgent' or 'standard'")
    title: str = Field(..., description="Carve-out or exclusion title")
    description: str = Field(..., description="Explanation of carve-out")


class ReviewNotice(BaseModel):
    title: str = Field(..., description="Review recommended headline")
    description: str = Field(..., description="Detailed explanation of strategic note")
    anchor_link: Optional[str] = Field(default=None, description="Navigation anchor for source viewport")


class DocumentAskRequest(BaseModel):
    document_id: str = Field(..., min_length=3, max_length=64, description="Target document ID (strict scoping)")
    session_id: Optional[str] = Field(default=None, max_length=64, description="Optional active user session ID")
    question: str = Field(..., min_length=2, max_length=1000, description="Natural language inquiry regarding document")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of relevant chunks to retrieve")
    conversation_history: Optional[List[Dict[str, str]]] = Field(
        default=None,
        description="Optional list of prior turn dicts ({'role': 'user'|'assistant', 'content': '...'}) for conversational context",
    )


class DocumentAskResponse(BaseModel):
    document_id: str = Field(..., description="Queried document ID")
    session_id: Optional[str] = Field(default=None, description="Associated session ID")
    question: str = Field(..., description="User question asked")
    answer: str = Field(..., description="Grounded, objective factual response")
    grounded: bool = Field(..., description="True if evidence was found in the document")
    confidence: str = Field(..., description="Subjective confidence rating (e.g., '99.4%', 'Insufficient Evidence')")
    citations: List[GroundedCitation] = Field(default_factory=list, description="Verified source citations")
    retrieved_sources: List[RetrievedSourceItem] = Field(default_factory=list, description="Raw source chunks retrieved")
    model: str = Field(..., description="Model identifier used for synthesis")
    telemetry: GroundedAnswerTelemetry = Field(..., description="Latency breakdown")
    badges: List[str] = Field(default_factory=list, description="Contextual badges (e.g., '§ 8.3 Verified')")
    carve_out_matrix: Optional[List[CarveOutItem]] = Field(default=None, description="Identified exceptions or carve-outs")
    strategic_consideration: Optional[str] = Field(default=None, description="Educational strategic consideration")
    review_recommended_notice: Optional[ReviewNotice] = Field(default=None, description="Notice recommending counsel review")
