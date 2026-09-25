from datetime import datetime
from typing import Optional, TYPE_CHECKING
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from app.schemas.brief import LawyerBrief
else:
    try:
        from backend.app.schemas.brief import LawyerBrief
    except ImportError:
        from app.schemas.brief import LawyerBrief


class CreateShareRequest(BaseModel):
    document_id: str = Field(..., description="Target document identifier")
    title: Optional[str] = Field(None, description="Optional custom document title")
    brief: LawyerBrief = Field(..., description="Full synthesized Lawyer Preparation Brief")
    ttl_hours: Optional[int] = Field(default=48, ge=1, le=168, description="Time to live in hours (default 48h, max 7 days)")


class CreateShareResponse(BaseModel):
    share_id: str = Field(..., description="Cryptographically secure opaque share identifier")
    expires_at: datetime = Field(..., description="UTC expiration timestamp")
    share_url: str = Field(..., description="Full environment-aware URL to view shared dossier")
    title: str = Field(..., description="Dossier title")
    is_localhost: bool = Field(..., description="True if sharing from a local development origin")


class SharedDossierResponse(BaseModel):
    share_id: str = Field(..., description="Share token identifier")
    document_id: str = Field(..., description="Source document identifier")
    title: str = Field(..., description="Document title")
    created_at: datetime = Field(..., description="Creation UTC timestamp")
    expires_at: datetime = Field(..., description="Expiration UTC timestamp")
    brief: LawyerBrief = Field(..., description="Read-only Lawyer Preparation Brief")
    disclaimer: str = Field(
        default="LexGuard Shared Counsel Preparation Dossier is an educational document intelligence resource. It does not constitute formal legal advice or create an attorney-client relationship.",
        description="Mandatory educational legal disclaimer",
    )
