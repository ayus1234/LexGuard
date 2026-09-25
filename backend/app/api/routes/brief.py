from typing import Optional, TYPE_CHECKING
from fastapi import APIRouter, Response, status, Query

if TYPE_CHECKING:
    from app.schemas.document import APIErrorResponse
    from app.schemas.brief import LawyerBriefRequest, LawyerBriefResponse, LawyerBrief
    from app.services.brief_service import brief_service
    from app.services.export_service import ExportService
else:
    try:
        from backend.app.schemas.document import APIErrorResponse
        from backend.app.schemas.brief import LawyerBriefRequest, LawyerBriefResponse, LawyerBrief
        from backend.app.services.brief_service import brief_service
        from backend.app.services.export_service import ExportService
    except ImportError:
        from app.schemas.document import APIErrorResponse
        from app.schemas.brief import LawyerBriefRequest, LawyerBriefResponse, LawyerBrief
        from app.services.brief_service import brief_service
        from app.services.export_service import ExportService

router = APIRouter(prefix="/documents", tags=["Lawyer Brief"])


@router.post(
    "/{document_id}/brief",
    response_model=LawyerBriefResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate or retrieve Counsel Preparation Brief",
    description=(
        "Synthesizes an objective, document-grounded Lawyer Preparation Brief containing "
        "executive summary, commercial terms, review areas, negotiation points, questions for counsel, "
        "and an action checklist with verified citations."
    ),
    responses={
        400: {"model": APIErrorResponse, "description": "Invalid document or request payload"},
        404: {"model": APIErrorResponse, "description": "Document not found in storage or index"},
        413: {"model": APIErrorResponse, "description": "Document exceeds maximum character limit for brief synthesis"},
        429: {"model": APIErrorResponse, "description": "Gemini rate limit or quota exceeded"},
        502: {"model": APIErrorResponse, "description": "AI model output failed schema validation"},
        503: {"model": APIErrorResponse, "description": "Gemini AI service unavailable or misconfigured"},
    },
)
async def generate_brief(
    document_id: str,
    request: Optional[LawyerBriefRequest] = None,
    force_regenerate: bool = Query(False, description="Force re-generation bypassing cache"),
) -> LawyerBriefResponse:
    doc_payload = request.document if request else None
    brief = await brief_service.generate_brief(
        document_id=document_id,
        document=doc_payload,
        force_regenerate=force_regenerate,
    )
    return LawyerBriefResponse(document_id=document_id, brief=brief)


@router.get(
    "/{document_id}/brief",
    response_model=LawyerBriefResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve Counsel Preparation Brief",
    description="Retrieves the cached or synthesized Lawyer Preparation Brief for an ingested document.",
    responses={
        404: {"model": APIErrorResponse, "description": "Document not found"},
        500: {"model": APIErrorResponse, "description": "Internal synthesis failure"},
    },
)
async def get_brief(
    document_id: str,
    force_regenerate: bool = Query(False, description="Force re-generation bypassing cache"),
) -> LawyerBriefResponse:
    brief = await brief_service.generate_brief(
        document_id=document_id,
        document=None,
        force_regenerate=force_regenerate,
    )
    return LawyerBriefResponse(document_id=document_id, brief=brief)


@router.post(
    "/{document_id}/brief/export/pdf",
    status_code=status.HTTP_200_OK,
    summary="Export Counsel Preparation Brief as PDF",
    description="Generates and streams a professional, consultation-ready PDF brief dossier.",
    responses={
        404: {"model": APIErrorResponse, "description": "Document not found"},
        500: {"model": APIErrorResponse, "description": "PDF generation failed"},
    },
)
async def export_brief_pdf_post(
    document_id: str,
    request: Optional[LawyerBriefRequest] = None,
) -> Response:
    if request and request.brief:
        brief = request.brief
    else:
        doc_payload = request.document if request else None
        brief = await brief_service.generate_brief(
            document_id=document_id,
            document=doc_payload,
        )
    pdf_bytes = ExportService.generate_brief_pdf(brief)
    safe_name = "LexGuard_Executive_Brief.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{safe_name}"',
            "Cache-Control": "no-cache",
        },
    )


@router.get(
    "/{document_id}/brief/export/pdf",
    status_code=status.HTTP_200_OK,
    summary="Download Counsel Preparation Brief PDF via GET",
    description="Direct browser download endpoint for PDF export.",
)
async def export_brief_pdf_get(document_id: str) -> Response:
    brief = await brief_service.generate_brief(
        document_id=document_id,
        document=None,
    )
    pdf_bytes = ExportService.generate_brief_pdf(brief)
    safe_name = "LexGuard_Executive_Brief.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{safe_name}"',
            "Cache-Control": "no-cache",
        },
    )


@router.post(
    "/{document_id}/brief/export/docx",
    status_code=status.HTTP_200_OK,
    summary="Export Counsel Preparation Brief as DOCX",
    description="Generates and streams a structured Microsoft Word (.docx) brief dossier.",
    responses={
        404: {"model": APIErrorResponse, "description": "Document not found"},
        500: {"model": APIErrorResponse, "description": "DOCX generation failed"},
    },
)
async def export_brief_docx_post(
    document_id: str,
    request: Optional[LawyerBriefRequest] = None,
) -> Response:
    if request and request.brief:
        brief = request.brief
    else:
        doc_payload = request.document if request else None
        brief = await brief_service.generate_brief(
            document_id=document_id,
            document=doc_payload,
        )
    docx_bytes = ExportService.generate_brief_docx(brief)
    safe_name = "LexGuard_Word_Checklist.docx"
    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": f'attachment; filename="{safe_name}"',
            "Cache-Control": "no-cache",
        },
    )


@router.get(
    "/{document_id}/brief/export/docx",
    status_code=status.HTTP_200_OK,
    summary="Download Counsel Preparation Brief DOCX via GET",
    description="Direct browser download endpoint for DOCX export.",
)
async def export_brief_docx_get(document_id: str) -> Response:
    brief = await brief_service.generate_brief(
        document_id=document_id,
        document=None,
    )
    docx_bytes = ExportService.generate_brief_docx(brief)
    safe_name = f"LexGuard-Brief-{document_id[:16]}.docx"
    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": f'attachment; filename="{safe_name}"',
            "Cache-Control": "no-cache",
        },
    )
