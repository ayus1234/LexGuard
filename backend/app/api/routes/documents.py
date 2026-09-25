from typing import TYPE_CHECKING
from fastapi import APIRouter, UploadFile, File, status

if TYPE_CHECKING:
    from app.schemas.document import DocumentResponse, APIErrorResponse
    from app.schemas.qa import DocumentAskRequest, DocumentAskResponse
    from app.services.document_service import document_service
    from app.services.qa_service import qa_service
    from app.utils.file_validation import EmptyFileException
else:
    try:
        from backend.app.schemas.document import DocumentResponse, APIErrorResponse
        from backend.app.schemas.qa import DocumentAskRequest, DocumentAskResponse
        from backend.app.services.document_service import document_service
        from backend.app.services.qa_service import qa_service
        from backend.app.utils.file_validation import EmptyFileException
    except ImportError:
        from app.schemas.document import DocumentResponse, APIErrorResponse
        from app.schemas.qa import DocumentAskRequest, DocumentAskResponse
        from app.services.document_service import document_service
        from app.services.qa_service import qa_service
        from app.utils.file_validation import EmptyFileException

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload and ingest legal document",
    description="Validates and extracts structured text, page boundaries, and section outlines from PDF, DOCX, or TXT documents.",
    responses={
        400: {"model": APIErrorResponse, "description": "Invalid file format, empty file, or corrupt content"},
        413: {"model": APIErrorResponse, "description": "File exceeds 50MB maximum size limit"},
        500: {"model": APIErrorResponse, "description": "Internal parsing or extraction error"},
    },
)
async def upload_document(
    file: UploadFile = File(..., description="Legal document file (.pdf, .docx, .txt)"),
) -> DocumentResponse:
    if not file.filename:
        raise EmptyFileException("Filename must not be empty.")

    content = await file.read()
    if len(content) == 0:
        raise EmptyFileException("Uploaded file is empty (0 bytes).")

    response = await document_service.process_uploaded_document(
        file_bytes=content,
        original_filename=file.filename,
        mime_type=file.content_type,
    )
    return response


@router.post(
    "/ask",
    response_model=DocumentAskResponse,
    status_code=status.HTTP_200_OK,
    summary="Ask document-grounded legal question",
    description="Performs semantic pgvector retrieval, citation verification, and Gemini synthesis to return a grounded legal Q&A response.",
    responses={
        400: {"model": APIErrorResponse, "description": "Invalid query parameters"},
        404: {"model": APIErrorResponse, "description": "Document not found or not indexed"},
        500: {"model": APIErrorResponse, "description": "Internal retrieval or generation failure"},
        502: {"model": APIErrorResponse, "description": "Upstream AI model unavailable"},
    },
)
async def ask_document(request: DocumentAskRequest) -> DocumentAskResponse:
    return await qa_service.ask_document(request)
