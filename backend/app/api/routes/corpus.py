"""
Corpus Registry API Routes.

Exposes LexGuard's 500-document corpus metadata for frontend consumption.
Supports pagination, filtering, and search.
"""

from typing import TYPE_CHECKING, Optional
from fastapi import APIRouter, Query, status

if TYPE_CHECKING:
    from app.schemas.corpus import CorpusListResponse, CorpusStatsResponse, CorpusDocumentItem
    from app.core.corpus import corpus_registry, CorpusDocument
else:
    try:
        from backend.app.schemas.corpus import CorpusListResponse, CorpusStatsResponse, CorpusDocumentItem
        from backend.app.core.corpus import corpus_registry, CorpusDocument
    except ImportError:
        from app.schemas.corpus import CorpusListResponse, CorpusStatsResponse, CorpusDocumentItem
        from app.core.corpus import corpus_registry, CorpusDocument

router = APIRouter(prefix="/corpus", tags=["Corpus"])


def _convert_to_schema(doc: "CorpusDocument") -> "CorpusDocumentItem":
    """Convert internal CorpusDocument to API schema."""
    return CorpusDocumentItem(
        id=doc.id,
        title=doc.title,
        doc_type=doc.doc_type,
        category=doc.category,
        jurisdiction=doc.jurisdiction,
        word_count=doc.word_count,
        page_count=doc.page_count,
        citation=doc.citation,
        summary=doc.summary,
        accessible=doc.accessible,
        analyzable=doc.analyzable,
    )


@router.get(
    "/documents",
    response_model=CorpusListResponse,
    status_code=status.HTTP_200_OK,
    summary="List corpus documents with pagination and filters",
    description="Returns paginated corpus metadata with optional filtering by document type, category, jurisdiction, and search query.",
)
async def list_corpus_documents(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(12, ge=1, le=100, description="Items per page"),
    doc_type: Optional[str] = Query(None, description="Filter by document type: template, public_law, fictional_demo"),
    category: Optional[str] = Query(None, description="Filter by category"),
    jurisdiction: Optional[str] = Query(None, description="Filter by jurisdiction"),
    search: Optional[str] = Query(None, description="Search in title, summary, citation"),
) -> CorpusListResponse:
    """
    Retrieve paginated corpus documents with optional filters.
    
    **Query Parameters:**
    - `page`: Current page number (default: 1)
    - `page_size`: Documents per page (default: 12, max: 100)
    - `doc_type`: Filter by type (template|public_law|fictional_demo)
    - `category`: Filter by legal category
    - `jurisdiction`: Filter by jurisdiction
    - `search`: Search across title, summary, and citation
    
    **Returns:**
    Paginated list with total count and page metadata.
    """
    # Apply filters
    filtered_docs = corpus_registry.filter(
        doc_type=doc_type,
        category=category,
        jurisdiction=jurisdiction,
    )
    
    # Apply search if provided
    if search and search.strip():
        search_lower = search.lower().strip()
        filtered_docs = [
            doc for doc in filtered_docs
            if (
                search_lower in doc.title.lower()
                or search_lower in doc.summary.lower()
                or search_lower in doc.citation.lower()
                or search_lower in doc.category.lower()
                or search_lower in doc.jurisdiction.lower()
            )
        ]
    
    # Calculate pagination
    total_docs = len(filtered_docs)
    total_pages = (total_docs + page_size - 1) // page_size  # Ceiling division
    
    # Ensure page is within bounds
    if page > total_pages and total_pages > 0:
        page = total_pages
    
    # Extract page slice
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    page_docs = filtered_docs[start_idx:end_idx]
    
    # Convert to schema
    doc_items = [_convert_to_schema(doc) for doc in page_docs]
    
    return CorpusListResponse(
        total=total_docs,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        documents=doc_items,
    )


@router.get(
    "/stats",
    response_model=CorpusStatsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get corpus statistics",
    description="Returns inventory counts and available filter values.",
)
async def get_corpus_stats() -> CorpusStatsResponse:
    """
    Retrieve corpus-wide statistics including counts and available filter values.
    
    **Returns:**
    - Total counts by document type
    - Available categories
    - Available jurisdictions
    """
    all_docs = corpus_registry.list_all()
    
    # Extract unique categories and jurisdictions
    categories = sorted(set(doc.category for doc in all_docs))
    jurisdictions = sorted(set(doc.jurisdiction for doc in all_docs))
    
    return CorpusStatsResponse(
        total_count=corpus_registry.total_count,
        templates_count=corpus_registry.templates_count,
        public_laws_count=corpus_registry.public_laws_count,
        demo_documents_count=corpus_registry.demo_documents_count,
        categories=categories,
        jurisdictions=jurisdictions,
    )
