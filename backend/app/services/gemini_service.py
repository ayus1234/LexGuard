import json
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.core.config import settings
    from app.core.logging import logger
    from app.core.credentials import (
        GeminiCredentialManager,
        CredentialItem,
        credential_manager,
        is_retryable_gemini_error,
    )
    from app.utils.file_validation import (
        GeminiServiceUnavailableException,
        GeminiQuotaExceededException,
        AnalysisValidationException,
    )
else:
    try:
        from backend.app.core.config import settings
        from backend.app.core.logging import logger
        from backend.app.core.credentials import (
            GeminiCredentialManager,
            CredentialItem,
            credential_manager,
            is_retryable_gemini_error,
        )
        from backend.app.utils.file_validation import (
            GeminiServiceUnavailableException,
            GeminiQuotaExceededException,
            AnalysisValidationException,
        )
    except ImportError:
        from app.core.config import settings
        from app.core.logging import logger
        from app.core.credentials import (
            GeminiCredentialManager,
            CredentialItem,
            credential_manager,
            is_retryable_gemini_error,
        )
        from app.utils.file_validation import (
            GeminiServiceUnavailableException,
            GeminiQuotaExceededException,
            AnalysisValidationException,
        )


class BaseGeminiService(ABC):
    """
    Abstract interface for Gemini model interactions.
    Enables clean dependency injection, local testing, and multi-model swappability.
    """

    @abstractmethod
    async def generate_structured_analysis(
        self, prompt: str, system_instruction: str
    ) -> Dict[str, Any]:
        """
        Executes prompt against Gemini and returns parsed JSON dictionary.
        """
        pass


class GoogleGeminiService(BaseGeminiService):
    """
    Production implementation leveraging the google-generativeai SDK.
    Supports request-scoped credential execution and automated primary-to-fallback key failover.
    Uses JSON mode (response_mime_type="application/json") and low temperature for deterministic extraction.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        cred_manager: Optional[GeminiCredentialManager] = None,
    ):
        if cred_manager is not None:
            self._credential_mgr = cred_manager
        elif api_key:
            self._credential_mgr = GeminiCredentialManager(primary_key=api_key)
        else:
            self._credential_mgr = credential_manager

        self._model_name = model_name or settings.GEMINI_MODEL

    def _raise_mapped_exception(self, e: Exception) -> None:
        """Translates upstream exceptions into clean LexGuardException instances without leaking keys."""
        if isinstance(
            e,
            (
                AnalysisValidationException,
                GeminiServiceUnavailableException,
                GeminiQuotaExceededException,
            ),
        ):
            raise e

        err_name = type(e).__name__
        err_msg = str(e).lower()

        if "resourceexhausted" in err_name.lower() or "429" in err_msg or "quota" in err_msg:
            raise GeminiQuotaExceededException("Gemini API rate limit or quota exceeded.")
        elif "deadline" in err_name.lower() or "timeout" in err_msg:
            raise GeminiServiceUnavailableException("Gemini API request timed out.")
        else:
            raise GeminiServiceUnavailableException(f"Upstream Gemini service error: {err_name}")

    async def _execute_generation(
        self, client: Any, prompt: str, system_instruction: str
    ) -> Dict[str, Any]:
        """Executes the generation call on a GenerativeModel bound to the specified client."""
        import google.generativeai as genai

        model = genai.GenerativeModel(
            model_name=self._model_name,
            system_instruction=system_instruction,
        )
        model._client = client

        # JSON mode with low temperature for deterministic legal factual extraction
        import google.generativeai as genai

        generation_config = genai.types.GenerationConfig(
            response_mime_type="application/json",
            temperature=0.1,
        )

        response = await asyncio.to_thread(
            model.generate_content,
            prompt,
            generation_config=generation_config,
        )

        if not response or not response.text:
            raise AnalysisValidationException("Gemini returned an empty response.")

        raw_text = response.text.strip()
        # Clean common markdown code fence wrappers if present
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.startswith("```"):
            raw_text = raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        raw_text = raw_text.strip()

        try:
            parsed_json = json.loads(raw_text)
        except json.JSONDecodeError as json_err:
            logger.error(f"Failed to decode Gemini JSON response: {str(json_err)}")
            raise AnalysisValidationException("Gemini model output could not be parsed as valid JSON.")

        if not isinstance(parsed_json, dict):
            raise AnalysisValidationException("Expected JSON root object from Gemini, received non-dictionary.")

        return parsed_json

    async def generate_structured_analysis(
        self, prompt: str, system_instruction: str
    ) -> Dict[str, Any]:
        candidates: List[CredentialItem] = self._credential_mgr.get_candidate_credentials()

        if not candidates:
            logger.error("Attempted Gemini API invocation without configured credentials")
            raise GeminiServiceUnavailableException(
                "Gemini API key is not configured in backend environment. Please set GEMINI_API_KEY_PRIMARY in .env."
            )

        last_error: Optional[Exception] = None

        for idx, candidate in enumerate(candidates):
            has_fallback = (idx + 1) < len(candidates)
            logger.info(f"Gemini analysis requested using {candidate.role} credential")

            try:
                client = self._credential_mgr.get_generative_client(candidate)
                parsed_json = await self._execute_generation(client, prompt, system_instruction)

                self._credential_mgr.record_success(candidate.role)
                logger.info(
                    f"Gemini request succeeded using {candidate.role} credential"
                    + (" (failover activated)" if candidate.role == "fallback" else "")
                )
                return parsed_json

            except Exception as e:
                last_error = e
                self._credential_mgr.record_failure(candidate.role, e)
                err_type = type(e).__name__

                if has_fallback and is_retryable_gemini_error(e):
                    logger.warning(
                        f"Gemini primary credential failed with retryable error ({err_type}); attempting fallback"
                    )
                    continue

                # Non-retryable error or all credentials exhausted
                if not has_fallback and len(candidates) > 1:
                    logger.error(
                        f"Gemini request failed with both configured credentials. Final error: {err_type}"
                    )
                else:
                    logger.error(
                        f"Gemini analysis failed using {candidate.role} credential with non-retryable or fatal error: {err_type}"
                    )

                self._raise_mapped_exception(e)

        if last_error:
            self._raise_mapped_exception(last_error)

        raise GeminiServiceUnavailableException("No credentials available to process Gemini request.")


gemini_service: BaseGeminiService = GoogleGeminiService()
