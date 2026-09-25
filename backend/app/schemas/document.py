from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class PageExtraction(BaseModel):
    page_number: int = Field(..., description="1-indexed document page number")
    text: str = Field(..., description="Normalized verbatim text extracted from the page")
    character_start: int = Field(..., description="Global character start index in document text")
    character_end: int = Field(..., description="Global character end index in document text")
    word_count: int = Field(..., description="Approximate word count on this page")


class SectionOutline(BaseModel):
    title: str = Field(..., description="Heading or section identifier (e.g., '§ 8.3 Limitation of Liability')")
    page_number: int = Field(..., description="Page number where the section was detected")
    character_offset: int = Field(..., description="Starting character offset in the document")


class DocumentMetadata(BaseModel):
    original_filename: str
    file_size_bytes: int
    mime_type: str
    sha256_hash: str
    extraction_engine: str
    processed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DocumentResponse(BaseModel):
    document_id: str = Field(..., description="Unique internal identifier for the document")
    filename: str = Field(..., description="Sanitized client filename")
    file_type: str = Field(..., description="Normalized file format: 'pdf', 'docx', or 'txt'")
    source_type: str = Field(default="upload", description="Source ingestion channel")
    page_count: int = Field(..., description="Total pages in the document")
    word_count: int = Field(..., description="Total word count across all pages")
    character_count: int = Field(..., description="Total character count")
    extracted_text: str = Field(..., description="Complete normalized extracted text")
    pages: List[PageExtraction] = Field(default_factory=list, description="Page-by-page text with grounding offsets")
    sections: List[SectionOutline] = Field(default_factory=list, description="Detected section headings for grounding")
    metadata: DocumentMetadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    processing_status: str = Field(default="completed", description="Ingestion processing status")


class ErrorDetail(BaseModel):
    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error explanation")


class APIErrorResponse(BaseModel):
    error: ErrorDetail
