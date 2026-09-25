from typing import TYPE_CHECKING, Any, cast
from fastapi import APIRouter, status

if TYPE_CHECKING:
    from app.schemas.analysis import DocumentAnalysisRequest, DocumentAnalysisResponse
    from app.schemas.document import APIErrorResponse, DocumentResponse
    from app.services.analysis_service import analysis_service
else:
    try:
        from backend.app.schemas.analysis import DocumentAnalysisRequest, DocumentAnalysisResponse
        from backend.app.schemas.document import APIErrorResponse, DocumentResponse
        from backend.app.services.analysis_service import analysis_service
    except ImportError:
        from app.schemas.analysis import DocumentAnalysisRequest, DocumentAnalysisResponse
        from app.schemas.document import APIErrorResponse, DocumentResponse
        from app.services.analysis_service import analysis_service

router = APIRouter(prefix="/documents", tags=["Analysis"])


@router.post(
    "/analyze",
    response_model=DocumentAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze legal document with Gemini AI",
    description=(
        "Performs document-grounded legal intelligence analysis on an ingested document. "
        "Extracts parties, key information, clauses, attention areas, and verified citations. "
        "Strictly provides educational information without definitive legal advice."
    ),
    responses={
        400: {"model": APIErrorResponse, "description": "Invalid document input or payload"},
        413: {"model": APIErrorResponse, "description": "Document exceeds maximum character limit for direct analysis"},
        429: {"model": APIErrorResponse, "description": "Gemini rate limit or quota exceeded"},
        502: {"model": APIErrorResponse, "description": "AI model output failed schema validation"},
        503: {"model": APIErrorResponse, "description": "Gemini AI service unavailable or misconfigured"},
    },
)
async def analyze_document(request: DocumentAnalysisRequest) -> DocumentAnalysisResponse:
    doc: DocumentResponse = cast(Any, request.document)
    return await analysis_service.analyze_document(doc)
