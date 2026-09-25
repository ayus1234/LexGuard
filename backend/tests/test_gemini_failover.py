import pytest
import asyncio
import logging
from unittest.mock import patch, MagicMock, AsyncMock

try:
    from backend.app.core.credentials import (
        GeminiCredentialManager,
        CredentialItem,
        is_retryable_gemini_error,
    )
    from backend.app.services.gemini_service import GoogleGeminiService
    from backend.app.services.embedding_service import GeminiEmbeddingService
    from backend.app.utils.file_validation import (
        GeminiQuotaExceededException,
        GeminiServiceUnavailableException,
        AnalysisValidationException,
        EmbeddingServiceException,
    )
    from backend.app.main import app
    from fastapi.testclient import TestClient
except ImportError:
    from app.core.credentials import (
        GeminiCredentialManager,
        CredentialItem,
        is_retryable_gemini_error,
    )
    from app.services.gemini_service import GoogleGeminiService
    from app.services.embedding_service import GeminiEmbeddingService
    from app.utils.file_validation import (
        GeminiQuotaExceededException,
        GeminiServiceUnavailableException,
        AnalysisValidationException,
        EmbeddingServiceException,
    )
    from app.main import app
    from fastapi.testclient import TestClient


# Helper mock class for simulating Google GenerativeModel response
class MockGenerateResponse:
    def __init__(self, text: str):
        self.text = text


# TEST 1: Primary succeeds without activating fallback
@pytest.mark.anyio
async def test_primary_succeeds_without_fallback():
    mgr = GeminiCredentialManager(
        primary_key="test_primary_key_abc123",
        fallback_key="test_fallback_key_xyz789",
    )
    service = GoogleGeminiService(cred_manager=mgr)

    calls = []

    async def mock_execute(client, prompt, sys_inst):
        # Determine which key the client is bound to
        calls.append("primary" if client == mgr.get_generative_client(mgr.get_candidate_credentials()[0]) else "fallback")
        return {"executive_summary": "Document passed legal check"}

    with patch.object(service, "_execute_generation", side_effect=mock_execute):
        result = await service.generate_structured_analysis("prompt", "system instruction")
        assert result == {"executive_summary": "Document passed legal check"}
        assert calls == ["primary"]


# TEST 2: Primary returns retryable 429 -> Fallback succeeds
@pytest.mark.anyio
async def test_primary_429_triggers_fallback_success():
    mgr = GeminiCredentialManager(
        primary_key="test_primary_key_abc123",
        fallback_key="test_fallback_key_xyz789",
    )
    service = GoogleGeminiService(cred_manager=mgr)

    calls = []

    async def mock_execute(client, prompt, sys_inst):
        primary_client = mgr.get_generative_client(mgr.get_candidate_credentials()[0])
        if client == primary_client:
            calls.append("primary")
            raise GeminiQuotaExceededException("429 ResourceExhausted: rate limit exceeded")
        else:
            calls.append("fallback")
            return {"status": "recovered_with_fallback"}

    with patch.object(service, "_execute_generation", side_effect=mock_execute):
        result = await service.generate_structured_analysis("prompt", "system instruction")
        assert result == {"status": "recovered_with_fallback"}
        assert calls == ["primary", "fallback"]


# TEST 3: Primary returns retryable 503 -> Fallback succeeds
@pytest.mark.anyio
async def test_primary_503_triggers_fallback_success():
    mgr = GeminiCredentialManager(
        primary_key="test_primary_key_abc123",
        fallback_key="test_fallback_key_xyz789",
    )
    service = GoogleGeminiService(cred_manager=mgr)

    calls = []

    async def mock_execute(client, prompt, sys_inst):
        primary_client = mgr.get_generative_client(mgr.get_candidate_credentials()[0])
        if client == primary_client:
            calls.append("primary")
            raise GeminiServiceUnavailableException("503 Service Unavailable: upstream model down")
        else:
            calls.append("fallback")
            return {"status": "recovered_from_503"}

    with patch.object(service, "_execute_generation", side_effect=mock_execute):
        result = await service.generate_structured_analysis("prompt", "system instruction")
        assert result == {"status": "recovered_from_503"}
        assert calls == ["primary", "fallback"]


# TEST 4: Primary returns invalid/unauthorized credential error -> Fallback succeeds
@pytest.mark.anyio
async def test_primary_auth_failure_triggers_fallback_success():
    mgr = GeminiCredentialManager(
        primary_key="test_invalid_primary_key",
        fallback_key="test_valid_fallback_key",
    )
    service = GoogleGeminiService(cred_manager=mgr)

    calls = []

    async def mock_execute(client, prompt, sys_inst):
        primary_client = mgr.get_generative_client(mgr.get_candidate_credentials()[0])
        if client == primary_client:
            calls.append("primary")
            raise Exception("API_KEY_INVALID: 401 Unauthorized API key not valid")
        else:
            calls.append("fallback")
            return {"status": "authorized_fallback_success"}

    with patch.object(service, "_execute_generation", side_effect=mock_execute):
        result = await service.generate_structured_analysis("prompt", "system instruction")
        assert result == {"status": "authorized_fallback_success"}
        assert calls == ["primary", "fallback"]


# TEST 5: Primary returns non-retryable validation error -> Fallback NOT called
@pytest.mark.anyio
async def test_non_retryable_validation_error_skips_fallback():
    mgr = GeminiCredentialManager(
        primary_key="test_primary_key_abc123",
        fallback_key="test_fallback_key_xyz789",
    )
    service = GoogleGeminiService(cred_manager=mgr)

    calls = []

    async def mock_execute(client, prompt, sys_inst):
        calls.append("primary")
        raise AnalysisValidationException("Expected JSON root object from Gemini, received string.")

    with patch.object(service, "_execute_generation", side_effect=mock_execute):
        with pytest.raises(AnalysisValidationException):
            await service.generate_structured_analysis("prompt", "system instruction")
        assert calls == ["primary"]  # Fallback was NOT consumed


# TEST 6: Primary fails retryably, Fallback also fails -> Standardized AI service error, no secret leakage
@pytest.mark.anyio
async def test_both_credentials_fail_returns_clean_error():
    mgr = GeminiCredentialManager(
        primary_key="test_primary_key_secret123",
        fallback_key="test_fallback_key_secret456",
    )
    service = GoogleGeminiService(cred_manager=mgr)

    calls = []

    async def mock_execute(client, prompt, sys_inst):
        if len(calls) == 0:
            calls.append("primary")
            raise GeminiQuotaExceededException("429 ResourceExhausted on primary")
        else:
            calls.append("fallback")
            raise GeminiQuotaExceededException("429 ResourceExhausted on fallback")

    with patch.object(service, "_execute_generation", side_effect=mock_execute):
        with pytest.raises(GeminiQuotaExceededException) as exc_info:
            await service.generate_structured_analysis("prompt", "system instruction")

        error_msg = str(exc_info.value)
        assert "secret123" not in error_msg
        assert "secret456" not in error_msg
        assert calls == ["primary", "fallback"]


# TEST 7: No primary key, fallback exists -> Fallback is used
@pytest.mark.anyio
async def test_fallback_only_configuration():
    mgr = GeminiCredentialManager(
        primary_key=None,
        fallback_key="test_fallback_key_only",
    )
    candidates = mgr.get_candidate_credentials()
    assert len(candidates) == 1
    assert candidates[0].role == "fallback"
    assert candidates[0].api_key == "test_fallback_key_only"

    service = GoogleGeminiService(cred_manager=mgr)
    calls = []

    async def mock_execute(client, prompt, sys_inst):
        calls.append("fallback")
        return {"status": "fallback_only_success"}

    with patch.object(service, "_execute_generation", side_effect=mock_execute):
        result = await service.generate_structured_analysis("prompt", "system instruction")
        assert result == {"status": "fallback_only_success"}
        assert calls == ["fallback"]


# TEST 8: Only legacy GEMINI_API_KEY exists -> Works transparently as primary
@pytest.mark.anyio
async def test_legacy_gemini_api_key_compatibility():
    mgr = GeminiCredentialManager(
        primary_key=None,
        fallback_key=None,
        legacy_key="legacy_test_api_key_777",
    )
    candidates = mgr.get_candidate_credentials()
    assert len(candidates) == 1
    assert candidates[0].role == "primary"
    assert candidates[0].api_key == "legacy_test_api_key_777"


# TEST 9: No keys configured -> Controlled AI_SERVICE_UNAVAILABLE, FastAPI app still starts
@pytest.mark.anyio
async def test_no_keys_configured_graceful_handling():
    mgr = GeminiCredentialManager(primary_key=None, fallback_key=None, legacy_key=None)
    # Ensure empty candidate list
    mgr._primary_key = None
    mgr._fallback_key = None

    service = GoogleGeminiService(cred_manager=mgr)
    with pytest.raises(GeminiServiceUnavailableException) as exc_info:
        await service.generate_structured_analysis("prompt", "system instruction")

    assert "Gemini API key is not configured" in str(exc_info.value)

    # Verify FastAPI application boots and health check functions without keys
    client = TestClient(app)
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


# TEST 10: Concurrent requests do not mutate shared global state or leak credential selection
@pytest.mark.anyio
async def test_concurrent_requests_isolation():
    mgr = GeminiCredentialManager(
        primary_key="primary_key_shared",
        fallback_key="fallback_key_shared",
    )
    service = GoogleGeminiService(cred_manager=mgr)

    async def mock_execute(client, prompt, sys_inst):
        primary_client = mgr.get_generative_client(mgr.get_candidate_credentials()[0])
        if "fail_primary" in prompt:
            if client == primary_client:
                await asyncio.sleep(0.01)
                raise GeminiQuotaExceededException("429 ResourceExhausted")
            return {"role": "fallback_result", "prompt": prompt}
        else:
            await asyncio.sleep(0.01)
            return {"role": "primary_result", "prompt": prompt}

    with patch.object(service, "_execute_generation", side_effect=mock_execute):
        tasks = [
            service.generate_structured_analysis("req_ok_1", "sys"),
            service.generate_structured_analysis("req_fail_primary_2", "sys"),
            service.generate_structured_analysis("req_ok_3", "sys"),
            service.generate_structured_analysis("req_fail_primary_4", "sys"),
        ]
        results = await asyncio.gather(*tasks)

        assert results[0]["role"] == "primary_result"
        assert results[1]["role"] == "fallback_result"
        assert results[2]["role"] == "primary_result"
        assert results[3]["role"] == "fallback_result"


# TEST 11: Embedding operation fails on primary and succeeds on fallback
@pytest.mark.anyio
async def test_embedding_service_failover():
    mgr = GeminiCredentialManager(
        primary_key="test_embed_primary_key",
        fallback_key="test_embed_fallback_key",
    )
    service = GeminiEmbeddingService(cred_manager=mgr)

    calls = []

    def mock_call_gemini_embed(texts, task_type, client=None):
        primary_client = mgr.get_generative_client(mgr.get_candidate_credentials()[0])
        if client == primary_client:
            calls.append("primary")
            raise GeminiQuotaExceededException("Embedding 429 Quota Exceeded")
        else:
            calls.append("fallback")
            return [[0.2] * 8 for _ in texts]

    with patch.object(service, "_call_gemini_embed", side_effect=mock_call_gemini_embed):
        results = await service.embed_batch(["text 1", "text 2"])
        assert len(results) == 2
        assert len(results[0]) == 8
        assert calls == ["primary", "fallback"]


# TEST 12: Privacy & zero secret leakage in logs, exceptions, and representations
@pytest.mark.anyio
async def test_zero_secret_leakage_in_logs_and_errors(caplog):
    secret_p = "AQ.SuperSecretPrimaryApiKeyXYZ999"
    secret_f = "AQ.SuperSecretFallbackApiKeyABC888"

    mgr = GeminiCredentialManager(primary_key=secret_p, fallback_key=secret_f)

    # Representation checks
    item_p = mgr.get_candidate_credentials()[0]
    assert secret_p not in repr(item_p)
    assert secret_p not in str(item_p)
    assert secret_p not in repr(mgr)

    service = GoogleGeminiService(cred_manager=mgr)

    async def mock_execute(client, prompt, sys_inst):
        raise GeminiServiceUnavailableException("503 Service Unavailable: upstream provider down")

    with caplog.at_level(logging.DEBUG):
        with patch.object(service, "_execute_generation", side_effect=mock_execute):
            with pytest.raises(GeminiServiceUnavailableException):
                await service.generate_structured_analysis("test_prompt", "sys")

    # Assert secrets do NOT appear anywhere in the captured log records
    for record in caplog.records:
        assert secret_p not in record.message
        assert secret_f not in record.message
