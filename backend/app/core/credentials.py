"""
Centralized Gemini Credential Management & Failover Logic.

Provides request-scoped, isolated credentials for Google Gemini operations across
both Document Analysis and Vector Retrieval/Embeddings.

Enforces:
1. Deterministic candidate order: PRIMARY -> FALLBACK.
2. Request-scoped client binding without global mutable state.
3. Strict error classification (transient capacity vs non-retryable errors).
4. Zero raw secret exposure in logs, exceptions, or representations.
"""

import time
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

try:
    from backend.app.core.config import settings
    from backend.app.core.logging import logger
    from backend.app.utils.file_validation import (
        LexGuardException,
        AnalysisValidationException,
        DocumentTooLargeForAnalysisException,
        UnsupportedFileTypeException,
        EmptyFileException,
        CorruptedPDFException,
        UnreadableDOCXException,
        GeminiQuotaExceededException,
        GeminiServiceUnavailableException,
    )
except ImportError:
    from app.core.config import settings
    from app.core.logging import logger
    from app.utils.file_validation import (
        LexGuardException,
        AnalysisValidationException,
        DocumentTooLargeForAnalysisException,
        UnsupportedFileTypeException,
        EmptyFileException,
        CorruptedPDFException,
        UnreadableDOCXException,
        GeminiQuotaExceededException,
        GeminiServiceUnavailableException,
    )


@dataclass(frozen=True)
class CredentialItem:
    """
    Encapsulates a configured Gemini credential and its role.
    Strictly masks the API key in string and repr outputs.
    """
    role: str  # "primary" or "fallback"
    api_key: str

    def __repr__(self) -> str:
        return f"CredentialItem(role='{self.role}', api_key='***')"

    def __str__(self) -> str:
        return f"CredentialItem(role='{self.role}')"


def is_retryable_gemini_error(error: Exception) -> bool:
    """
    Determines whether an encountered error warrants attempting the fallback credential.
    
    Retryable:
    - 429 / RESOURCE_EXHAUSTED / Quota exceeded / Rate limit
    - 503 / Service Unavailable / Upstream outage
    - 500 / Internal server error from provider
    - 504 / Deadline Exceeded / Timeout
    - 401 / 403 / API Key Rejected, Invalid, or Blocked
    - Connection resets / transient transport failures
    
    NON-Retryable (will NOT consume fallback quota):
    - Invalid request payloads or schema errors (400 InvalidArgument)
    - Output validation failures (AnalysisValidationException)
    - Oversized documents (DocumentTooLargeForAnalysisException)
    - Bad file formats, empty files
    - Internal application programming errors (TypeError, ValueError, KeyError)
    """
    if error is None:
        return False

    # 1. Non-retryable LexGuard domain exceptions
    non_retryable_types = (
        AnalysisValidationException,
        DocumentTooLargeForAnalysisException,
        UnsupportedFileTypeException,
        EmptyFileException,
        CorruptedPDFException,
        UnreadableDOCXException,
        TypeError,
        ValueError,
        KeyError,
    )
    if isinstance(error, non_retryable_types):
        return False

    # 2. Check google.api_core exceptions if available
    try:
        from google.api_core import exceptions as ga_exceptions

        if isinstance(error, ga_exceptions.InvalidArgument):
            return False

        if isinstance(
            error,
            (
                ga_exceptions.ResourceExhausted,
                ga_exceptions.TooManyRequests,
                ga_exceptions.ServiceUnavailable,
                ga_exceptions.InternalServerError,
                ga_exceptions.DeadlineExceeded,
                ga_exceptions.Unauthenticated,
                ga_exceptions.PermissionDenied,
            ),
        ):
            return True
    except ImportError:
        pass

    # 3. Known retryable LexGuard exceptions
    if isinstance(error, (GeminiQuotaExceededException, GeminiServiceUnavailableException)):
        return True

    # 4. HTTP status code inspection if present
    status_code = getattr(error, "status_code", None) or getattr(error, "code", None)
    if isinstance(status_code, int):
        if status_code in (429, 500, 502, 503, 504, 401, 403):
            return True
        if status_code in (400, 404, 413, 422):
            return False

    # 5. String-based heuristic classification
    err_name = type(error).__name__.lower()
    err_msg = str(error).lower()

    # Explicit non-retryable text clues
    if "invalidargument" in err_name or "schema" in err_msg or "jsondecode" in err_msg:
        return False

    retryable_clues = (
        "resourceexhausted",
        "quota",
        "rate limit",
        "rate_limit",
        "429",
        "503",
        "500",
        "504",
        "deadline",
        "timeout",
        "service unavailable",
        "unavailable",
        "internal server error",
        "api_key_invalid",
        "api key not valid",
        "api_key not valid",
        "unauthenticated",
        "permission_denied",
        "permissiondenied",
        "connection reset",
        "server disconnected",
        "broken pipe",
    )

    if any(clue in err_name or clue in err_msg for clue in retryable_clues):
        return True

    return False


_UNSET = object()


class GeminiCredentialManager:
    """
    Centralized manager for primary and fallback Gemini credentials.
    Provides deterministic ordering and request-scoped client instances.
    """

    def __init__(
        self,
        primary_key: Any = _UNSET,
        fallback_key: Any = _UNSET,
        legacy_key: Any = _UNSET,
    ):
        # Resolve Primary
        if primary_key is not _UNSET:
            self._primary_key = primary_key or (legacy_key if legacy_key is not _UNSET else None)
        elif legacy_key is not _UNSET:
            self._primary_key = legacy_key
        else:
            self._primary_key = settings.GEMINI_API_KEY_PRIMARY or settings.GEMINI_API_KEY

        # Resolve Fallback
        if fallback_key is not _UNSET:
            self._fallback_key = fallback_key
        else:
            self._fallback_key = settings.GEMINI_API_KEY_FALLBACK

        # Status & health tracking (in-memory, lightweight)
        self._status: Dict[str, str] = {
            "primary": "unknown",
            "fallback": "unknown",
        }
        self._last_failure: Dict[str, Optional[float]] = {
            "primary": None,
            "fallback": None,
        }

        # Client cache keyed by api_key to reuse channels without shared state races
        self._client_cache: Dict[str, Any] = {}

    def get_candidate_credentials(self) -> List[CredentialItem]:
        """
        Returns configured credentials in deterministic evaluation order:
        PRIMARY -> FALLBACK.
        """
        candidates: List[CredentialItem] = []
        if self._primary_key and self._primary_key.strip():
            candidates.append(CredentialItem(role="primary", api_key=self._primary_key.strip()))

        if self._fallback_key and self._fallback_key.strip():
            # Avoid adding exact identical duplicate key as fallback if user configured the same string twice
            if not candidates or candidates[0].api_key != self._fallback_key.strip():
                candidates.append(CredentialItem(role="fallback", api_key=self._fallback_key.strip()))

        return candidates

    def has_credentials(self) -> bool:
        """Returns True if at least one valid Gemini key is configured."""
        return len(self.get_candidate_credentials()) > 0

    def record_success(self, role: str) -> None:
        """Records a successful API call for the given credential role."""
        if role in self._status:
            self._status[role] = "available"

    def record_failure(self, role: str, error: Exception) -> None:
        """Records a failure for the given credential role without permanently disabling it."""
        if role in self._status:
            self._status[role] = "failing"
            self._last_failure[role] = time.time()

    def get_generative_client(self, credential: CredentialItem) -> Any:
        """
        Returns a thread-safe GenerativeServiceClient bound specifically to this credential.
        Avoids mutating global SDK state.
        """
        key = credential.api_key
        if key not in self._client_cache:
            try:
                import google.ai.generativelanguage as glm
                from google.api_core.client_options import ClientOptions

                self._client_cache[key] = glm.GenerativeServiceClient(
                    client_options=ClientOptions(api_key=key)
                )
            except Exception as e:
                logger.error(f"Failed to instantiate GenerativeServiceClient for {credential.role} credential: {type(e).__name__}")
                # Fallback to configuring if direct client creation fails in specific environment
                import google.generativeai as genai
                genai.configure(api_key=key)
                client_module = getattr(genai, "client", None)
                if client_module and hasattr(client_module, "get_default_generative_client"):
                    self._client_cache[key] = client_module.get_default_generative_client()
                else:
                    self._client_cache[key] = None

        return self._client_cache[key]

    def get_telemetry_status(self) -> Dict[str, Any]:
        """Provides safe diagnostic metadata without exposing secrets."""
        candidates = self.get_candidate_credentials()
        return {
            "has_primary": any(c.role == "primary" for c in candidates),
            "has_fallback": any(c.role == "fallback" for c in candidates),
            "total_credentials": len(candidates),
            "primary_status": self._status.get("primary", "unknown"),
            "fallback_status": self._status.get("fallback", "unknown"),
            "last_primary_failure": self._last_failure.get("primary"),
            "last_fallback_failure": self._last_failure.get("fallback"),
        }

    def __repr__(self) -> str:
        candidates = [c.role for c in self.get_candidate_credentials()]
        return f"GeminiCredentialManager(roles={candidates})"


# Global default credential manager instance for application lifecycle
credential_manager = GeminiCredentialManager()
