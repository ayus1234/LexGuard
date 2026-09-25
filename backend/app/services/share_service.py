"""
Secure Dossier Sharing Service.
Generates cryptographically random, unguessable tokens with expiration timestamps
and environment-aware public URLs for cross-device dossier review.
"""

import secrets
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, TYPE_CHECKING
import threading

if TYPE_CHECKING:
    from app.core.config import settings
    from app.core.logging import logger
    from app.schemas.share import CreateShareRequest, CreateShareResponse, SharedDossierResponse
    from app.utils.file_validation import ShareNotFoundException, ShareExpiredException
else:
    try:
        from backend.app.core.config import settings
        from backend.app.core.logging import logger
        from backend.app.schemas.share import CreateShareRequest, CreateShareResponse, SharedDossierResponse
        from backend.app.utils.file_validation import ShareNotFoundException, ShareExpiredException
    except ImportError:
        from app.core.config import settings
        from app.core.logging import logger
        from app.schemas.share import CreateShareRequest, CreateShareResponse, SharedDossierResponse
        from app.utils.file_validation import ShareNotFoundException, ShareExpiredException


class ShareService:
    def __init__(self):
        self._shares: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def create_share(
        self,
        request: CreateShareRequest,
        client_origin: Optional[str] = None,
    ) -> CreateShareResponse:
        """
        Creates a cryptographically secure, time-limited share token for a LawyerBrief.
        Never stores API credentials, DB connection strings, or filesystem paths.
        """
        with self._lock:
            # 192 bits of entropy (24 bytes urlsafe => 32 chars)
            share_id = secrets.token_urlsafe(24)
            now = datetime.now(timezone.utc)
            ttl = request.ttl_hours or settings.SHARE_TOKEN_TTL_HOURS
            expires_at = now + timedelta(hours=ttl)

            title = request.title or request.brief.document_title or f"Document {request.document_id}"

            # Environment-aware URL construction
            # Prioritize client_origin if provided by frontend, fallback to configured settings.APP_URL
            app_origin = client_origin or settings.APP_URL or "http://localhost:3000"
            app_origin = app_origin.rstrip("/")
            share_url = f"{app_origin}/share/{share_id}"

            is_localhost = "localhost" in app_origin or "127.0.0.1" in app_origin

            # Store the shared dossier payload
            self._shares[share_id] = {
                "share_id": share_id,
                "document_id": request.document_id,
                "title": title,
                "created_at": now,
                "expires_at": expires_at,
                "brief": request.brief,
            }

            logger.info(
                f"Generated secure share token {share_id[:8]}... (expires_at={expires_at.isoformat()}, is_localhost={is_localhost})"
            )

            return CreateShareResponse(
                share_id=share_id,
                expires_at=expires_at,
                share_url=share_url,
                title=title,
                is_localhost=is_localhost,
            )

    def get_share(self, share_id: str) -> SharedDossierResponse:
        """
        Retrieves a shared dossier by token if valid and not expired.
        """
        with self._lock:
            if not share_id or share_id not in self._shares:
                raise ShareNotFoundException(
                    "The requested shared dossier was not found or has expired."
                )

            data = self._shares[share_id]
            now = datetime.now(timezone.utc)

            if now > data["expires_at"]:
                # Clean up expired token
                del self._shares[share_id]
                raise ShareExpiredException(
                    "The shared dossier link has expired. Please request a new share link."
                )

            return SharedDossierResponse(
                share_id=data["share_id"],
                document_id=data["document_id"],
                title=data["title"],
                created_at=data["created_at"],
                expires_at=data["expires_at"],
                brief=data["brief"],
            )

    def purge_expired_shares(self) -> int:
        """
        Purges expired share records to maintain zero-retention standards.
        """
        with self._lock:
            now = datetime.now(timezone.utc)
            expired_keys = [k for k, v in self._shares.items() if now > v["expires_at"]]
            for k in expired_keys:
                del self._shares[k]
            return len(expired_keys)


share_service = ShareService()
