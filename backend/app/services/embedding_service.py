from abc import ABC, abstractmethod
from typing import List, Optional, Any
import asyncio

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
        EmbeddingServiceException,
        GeminiServiceUnavailableException,
        GeminiQuotaExceededException,
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
        EmbeddingServiceException,
        GeminiServiceUnavailableException,
        GeminiQuotaExceededException,
    )


class BaseEmbeddingService(ABC):
    """
    Abstract interface for generating vector embeddings.
    Allows swappable embedding providers and offline test mocking.
    """

    @abstractmethod
    async def embed_text(self, text: str, task_type: str = "retrieval_document") -> List[float]:
        pass

    @abstractmethod
    async def embed_batch(
        self, texts: List[str], task_type: str = "retrieval_document"
    ) -> List[List[float]]:
        pass


class GeminiEmbeddingService(BaseEmbeddingService):
    """
    Production embedding service utilizing Google's Gemini text-embedding-004 model.
    Supports request-scoped credential execution, primary-to-fallback key failover,
    and batched execution with task-type differentiation.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        batch_size: Optional[int] = None,
        cred_manager: Optional[GeminiCredentialManager] = None,
    ):
        if cred_manager is not None:
            self._credential_mgr = cred_manager
        elif api_key:
            self._credential_mgr = GeminiCredentialManager(primary_key=api_key)
        else:
            self._credential_mgr = credential_manager

        self._model_name = model_name or settings.GEMINI_EMBEDDING_MODEL
        self._batch_size = batch_size or settings.EMBEDDING_BATCH_SIZE
        self._initialized: bool = True

    def _call_gemini_embed(
        self, texts: List[str], task_type: str, client: Any = None
    ) -> List[List[float]]:
        import google.generativeai as genai

        kwargs = {
            "model": self._model_name,
            "content": texts,
            "task_type": task_type,
        }
        if client is not None:
            kwargs["client"] = client

        result = genai.embed_content(**kwargs)

        embeddings = result.get("embedding", [])
        # If single text, API may return a single list of floats
        if embeddings and isinstance(embeddings[0], (int, float)):
            return [embeddings]
        return embeddings

    def _raise_mapped_exception(self, e: Exception) -> None:
        """Translates upstream exceptions into clean LexGuardException instances without leaking keys."""
        if isinstance(
            e,
            (
                EmbeddingServiceException,
                GeminiServiceUnavailableException,
                GeminiQuotaExceededException,
            ),
        ):
            raise e

        err_name = type(e).__name__
        err_msg = str(e).lower()

        if "resourceexhausted" in err_name.lower() or "429" in err_msg or "quota" in err_msg:
            raise GeminiQuotaExceededException("Gemini Embedding API quota or rate limit exceeded.")
        elif "deadline" in err_name.lower() or "timeout" in err_msg:
            raise GeminiServiceUnavailableException("Embedding API request timed out.")
        else:
            raise EmbeddingServiceException(f"Failed to generate embeddings: {err_name}")

    async def _embed_batch_with_client(
        self, client: Any, texts: List[str], task_type: str
    ) -> List[List[float]]:
        all_embeddings: List[List[float]] = []
        for i in range(0, len(texts), self._batch_size):
            batch = texts[i : i + self._batch_size]
            batch_res = await asyncio.to_thread(
                self._call_gemini_embed, batch, task_type, client
            )
            if not batch_res or len(batch_res) != len(batch):
                raise EmbeddingServiceException(
                    f"Expected {len(batch)} embeddings, received {len(batch_res) if batch_res else 0}"
                )
            all_embeddings.extend(batch_res)
        return all_embeddings

    async def embed_text(self, text: str, task_type: str = "retrieval_document") -> List[float]:
        results = await self.embed_batch([text], task_type=task_type)
        if not results:
            raise EmbeddingServiceException("Embedding API returned empty embedding vector.")
        return results[0]

    async def embed_batch(
        self, texts: List[str], task_type: str = "retrieval_document"
    ) -> List[List[float]]:
        if not texts:
            return []

        candidates: List[CredentialItem] = self._credential_mgr.get_candidate_credentials()

        if not candidates:
            logger.error("Attempted embedding generation without configured credentials")
            raise GeminiServiceUnavailableException(
                "Gemini API key is not configured for embeddings. Please set GEMINI_API_KEY_PRIMARY in .env."
            )

        last_error: Optional[Exception] = None

        for idx, candidate in enumerate(candidates):
            has_fallback = (idx + 1) < len(candidates)

            try:
                client = self._credential_mgr.get_generative_client(candidate)
                all_embeddings = await self._embed_batch_with_client(client, texts, task_type)

                self._credential_mgr.record_success(candidate.role)
                logger.info(
                    f"Gemini embedding succeeded using {candidate.role} credential"
                    + (" (failover activated)" if candidate.role == "fallback" else "")
                )
                return all_embeddings

            except Exception as e:
                last_error = e
                self._credential_mgr.record_failure(candidate.role, e)
                err_type = type(e).__name__

                if has_fallback and is_retryable_gemini_error(e):
                    logger.warning(
                        f"Gemini embedding primary credential failed with retryable error ({err_type}); attempting fallback"
                    )
                    continue

                if not has_fallback and len(candidates) > 1:
                    logger.error(
                        f"Gemini embedding failed with both configured credentials. Final error: {err_type}"
                    )
                else:
                    logger.error(
                        f"Gemini embedding failed using {candidate.role} credential: {err_type}"
                    )

                self._raise_mapped_exception(e)

        if last_error:
            self._raise_mapped_exception(last_error)

        raise GeminiServiceUnavailableException("No credentials available for embedding generation.")


embedding_service: BaseEmbeddingService = GeminiEmbeddingService()
