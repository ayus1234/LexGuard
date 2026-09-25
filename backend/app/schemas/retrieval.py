from enum import Enum
from typing import List, Optional, TYPE_CHECKING
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from app.schemas.document import DocumentResponse
else:
    try:
        from backend.app.schemas.document import DocumentResponse
    except ImportError:
        from app.schemas.document import DocumentResponse


class GroundingStatus(str, Enum):
    grounded = "grounded"
    insufficient_evidence = "insufficient_evidence"
    document_not_indexed = "document_not_indexed"


class ChunkMetadata(BaseModel):
    document_id: str = Field(..., description="Document identifier this chunk belongs to")
    chunk_id: str = Field(..., description="Unique chunk identifier")
    section: Optional[str] = Field(default=None, description="Legal section heading if detected")
    page_start: int = Field(..., description="1-indexed starting page number")
    page_end: int = Field(..., description="1-indexed ending page number")
    character_start: int = Field(..., description="Global character start index in document text")
    character_end: int = Field(..., description="Global character end index in document text")


class DocumentChunk(BaseModel):
    chunk_id: str = Field(..., description="Unique deterministic identifier (e.g. 'doc123_chk_0001')")
    document_id: str = Field(..., description="Parent document identifier")
    chunk_index: int = Field(..., description="Sequential chunk index (0-indexed)")
    text: str = Field(..., description="Verbatim text content of chunk")
    section: Optional[str] = Field(default=None, description="Dominant section heading")
    page_start: int = Field(..., description="Initial page number where chunk starts")
    page_end: int = Field(..., description="Final page number where chunk concludes")
    character_start: int = Field(..., description="Global character start coordinate")
    character_end: int = Field(..., description="Global character end coordinate")
    token_estimate: int = Field(..., description="Estimated token count")
    metadata: ChunkMetadata = Field(..., description="Search and citation grounding metadata")


class RetrievalResultItem(BaseModel):
    chunk_id: str = Field(..., description="Retrieved chunk identifier")
    text: str = Field(..., description="Verbatim chunk text snippet")
    similarity_score: float = Field(..., description="Normalized cosine similarity score (0.0 to 1.0)")
    document_id: str = Field(..., description="Parent document ID")
    section: Optional[str] = Field(default=None, description="Associated legal section or heading")
    page_start: int = Field(..., description="Starting page number")
    page_end: int = Field(..., description="Ending page number")
    character_start: int = Field(..., description="Global start character offset")
    character_end: int = Field(..., description="Global end character offset")


class RetrievalResult(BaseModel):
    document_id: str = Field(..., description="Target document ID searched")
    query: str = Field(..., description="User search query")
    grounding_status: GroundingStatus = Field(..., description="Retrieval evidence validation state")
    results: List[RetrievalResultItem] = Field(default_factory=list, description="Ranked relevant chunks")


class DocumentIndexRequest(BaseModel):
    document: DocumentResponse = Field(..., description="Normalized document representation to index")


class DocumentIndexResponse(BaseModel):
    document_id: str = Field(..., description="Identifier of indexed document")
    chunk_count: int = Field(..., description="Total structured chunks created and stored")
    indexed: bool = Field(default=True, description="True if indexing succeeded")
    processing_time_ms: int = Field(..., description="Total indexing duration in milliseconds")


class RetrievalSearchRequest(BaseModel):
    document_id: str = Field(..., description="Document ID to search within (strict scoping)")
    query: str = Field(..., min_length=2, max_length=1000, description="Natural language inquiry")
    top_k: int = Field(default=5, ge=1, le=20, description="Maximum number of chunks to return")


RetrievalSearchResponse = RetrievalResult
