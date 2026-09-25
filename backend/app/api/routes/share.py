from typing import Optional, TYPE_CHECKING
from fastapi import APIRouter, Request, status

if TYPE_CHECKING:
    from app.schemas.share import CreateShareRequest, CreateShareResponse, SharedDossierResponse
    from app.schemas.document import APIErrorResponse
    from app.services.share_service import share_service
else:
    try:
        from backend.app.schemas.share import CreateShareRequest, CreateShareResponse, SharedDossierResponse
        from backend.app.schemas.document import APIErrorResponse
        from backend.app.services.share_service import share_service
    except ImportError:
        from app.schemas.share import CreateShareRequest, CreateShareResponse, SharedDossierResponse
        from app.schemas.document import APIErrorResponse
        from app.services.share_service import share_service

router = APIRouter(prefix="/share", tags=["Share"])


@router.post(
    "/dossier",
    response_model=CreateShareResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a secure, time-limited shared dossier link",
    description=(
        "Generates a cryptographically random, unguessable share token for an executive dossier. "
        "Respects zero-retention standards with auto-expiration and never exposes internal secrets."
    ),
    responses={
        400: {"model": APIErrorResponse, "description": "Invalid brief payload"},
        500: {"model": APIErrorResponse, "description": "Internal server error"},
    },
)
async def create_shared_dossier(
    payload: CreateShareRequest,
    http_request: Request,
) -> CreateShareResponse:
    # Determine client origin from headers or payload
    origin_header = http_request.headers.get("origin") or http_request.headers.get("referer")
    if origin_header:
        # Strip path from referer if needed
        from urllib.parse import urlparse
        parsed = urlparse(origin_header)
        client_origin = f"{parsed.scheme}://{parsed.netloc}"
    else:
        client_origin = None

    return share_service.create_share(payload, client_origin=client_origin)


@router.get(
    "/dossier/{share_id}",
    response_model=SharedDossierResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve shared dossier by secure token",
    description="Fetches read-only dossier content for authenticated share token if not expired.",
    responses={
        404: {"model": APIErrorResponse, "description": "Share link not found or revoked"},
        410: {"model": APIErrorResponse, "description": "Share link has expired"},
    },
)
async def get_shared_dossier(share_id: str) -> SharedDossierResponse:
    return share_service.get_share(share_id)
