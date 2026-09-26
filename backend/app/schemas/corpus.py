"""
Pydantic schemas for Corpus Registry API endpoints.
"""

from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class CorpusDocumentItem(BaseModel):
    """Individual corpus document metadata."""

    id: str = Field(..., description="Unique document identifier")
    title: str = Field(..., description="Document title")
    doc_type: Literal["template", "public_law", "fictional_demo"] = Field(
        ..., description="Document classification type"
    )
    category: str = Field(..., description="Legal category")
    jurisdiction: str = Field(..., description="Governing jurisdiction")
    word_count: int = Field(..., description="Total word count", gt=0)
    page_count: int = Field(..., description="Total page count", gt=0)
    citation: str = Field(..., description="Legal citation or standard reference")
    summary: str = Field(..., description="Document summary")
    accessible: bool = Field(default=True, description="Whether document is accessible")
    analyzable: bool = Field(default=True, description="Whether document can be analyzed")


class CorpusListResponse(BaseModel):
    """Paginated corpus document listing."""

    total: int = Field(..., description="Total documents matching filters")
    page: int = Field(..., description="Current page number (1-indexed)", ge=1)
    page_size: int = Field(..., description="Items per page", ge=1, le=100)
    total_pages: int = Field(..., description="Total number of pages")
    documents: List[CorpusDocumentItem] = Field(..., description="Document items for current page")


class CorpusStatsResponse(BaseModel):
    """Corpus inventory statistics."""

    total_count: int = Field(..., description="Total corpus size")
    templates_count: int = Field(..., description="Number of institutional templates")
    public_laws_count: int = Field(..., description="Number of public legal documents")
    demo_documents_count: int = Field(..., description="Number of demo documents")
    categories: List[str] = Field(..., description="Available categories")
    jurisdictions: List[str] = Field(..., description="Available jurisdictions")
