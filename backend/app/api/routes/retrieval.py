from typing import TYPE_CHECKING
from fastapi import APIRouter, status

if TYPE_CHECKING:
    from app.schemas.retrieval import (
        DocumentIndexRequest,
        DocumentIndexResponse,
        RetrievalSearchRequest,
        RetrievalSearchResponse,
    )
    from app.schemas.document import APIErrorResponse
    from app.services.retrieval_service import retrieval_service
else:
    try:
        from backend.app.schemas.retrieval import (
            DocumentIndexRequest,
            DocumentIndexResponse,
            RetrievalSearchRequest,
            RetrievalSearchResponse,
        )
        from backend.app.schemas.document import APIErrorResponse
        from backend.app.services.retrieval_service import retrieval_service
    except ImportError:
        from app.schemas.retrieval import (
            DocumentIndexRequest,
            DocumentIndexResponse,
            RetrievalSearchRequest,
            RetrievalSearchResponse,
        )
        from app.schemas.document import APIErrorResponse
        from app.services.retrieval_service import retrieval_service

router = APIRouter(tags=["Retrieval"])


@router.post(
    "/documents/index",
    response_model=DocumentIndexResponse,
    status_code=status.HTTP_200_OK,
    summary="Index document chunks in vector store",
    description="Splits a normalized legal document into structurally-aware chunks, generates vector embeddings, and stores them in PostgreSQL with pgvector.",
    responses={
        400: {"model": APIErrorResponse, "description": "Invalid document representation"},
        500: {"model": APIErrorResponse, "description": "Vector database error"},
        502: {"model": APIErrorResponse, "description": "Embedding model failure"},
    },
)
async def index_document(request: DocumentIndexRequest) -> DocumentIndexResponse:
    return await retrieval_service.index_document(request.document)


@router.post(
    "/retrieval/search",
    response_model=RetrievalSearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Semantic similarity search over document chunks",
    description="Retrieves the most relevant grounded chunks for a query within a specified document, preserving exact page, section, and character offsets.",
    responses={
        400: {"model": APIErrorResponse, "description": "Invalid query parameters"},
        500: {"model": APIErrorResponse, "description": "Vector search failure"},
    },
)
async def search_document(request: RetrievalSearchRequest) -> RetrievalSearchResponse:
    return await retrieval_service.retrieve(
        document_id=request.document_id,
        query=request.query,
        top_k=request.top_k,
    )


@router.delete(
    "/documents/{document_id}/vectors",
    status_code=status.HTTP_200_OK,
    summary="Delete document vector entries",
    description="Deletes all indexed vector embeddings and chunks associated with the specified document for privacy cleanup.",
)
async def delete_document_vectors(document_id: str):
    success = retrieval_service.delete_document_vectors(document_id)
    return {"document_id": document_id, "deleted": success}
