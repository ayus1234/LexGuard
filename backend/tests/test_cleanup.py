from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient

try:
    from backend.app.core.config import settings
    from backend.app.services.cleanup_service import cleanup_service
except ImportError:
    from app.core.config import settings
    from app.services.cleanup_service import cleanup_service


def test_cleanup_after_successful_upload(client: TestClient, sample_txt_bytes: bytes):
    """Verify that after a successful document processing cycle, no temporary files remain."""
    temp_dir = settings.temp_storage_dir
    files_before = set(temp_dir.glob("*"))

    files = {"file": ("cleanup_test.txt", sample_txt_bytes, "text/plain")}
    response = client.post("/api/v1/documents/upload", files=files)
    assert response.status_code == 200

    files_after = set(temp_dir.glob("*"))
    # Verify no newly created files linger in the temporary folder
    new_files = files_after - files_before
    assert len(new_files) == 0, f"Temporary files leaked on disk: {new_files}"


def test_cleanup_after_failed_extraction(client: TestClient, sample_txt_bytes: bytes):
    """Verify that even when an extraction exception occurs, the finally block cleans up."""
    temp_dir = settings.temp_storage_dir
    files_before = set(temp_dir.glob("*"))

    with patch(
        "backend.app.services.extraction_service.extraction_service.extract_document",
        side_effect=RuntimeError("Simulated engine crash"),
    ):
        files = {"file": ("crash_test.txt", sample_txt_bytes, "text/plain")}
        response = client.post("/api/v1/documents/upload", files=files)
        # Should catch and return 500
        assert response.status_code == 500

    files_after = set(temp_dir.glob("*"))
    new_files = files_after - files_before
    assert len(new_files) == 0, f"Temporary file was not cleaned up after error: {new_files}"


def test_cleanup_service_direct():
    """Verify CleanupService correctly removes existing file and handles non-existent file."""
    temp_file = settings.temp_storage_dir / "direct_cleanup_test.tmp"
    temp_file.write_text("transient customer data")
    assert temp_file.exists()

    result = cleanup_service.cleanup_file(temp_file)
    assert result is True
    assert not temp_file.exists()

    # Second call on non-existent file must not crash
    result_missing = cleanup_service.cleanup_file(temp_file)
    assert result_missing is False
