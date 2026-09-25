import re
import uuid
from pathlib import Path
try:
    from backend.app.core.config import settings
except ImportError:
    from app.core.config import settings


def generate_document_id() -> str:
    """Generate a collision-resistant unique identifier for an ingested document."""
    return f"doc_{uuid.uuid4().hex}"


def sanitize_filename(filename: str) -> str:
    """
    Sanitizes user-provided filenames to prevent path traversal,
    null byte injection, or unexpected filesystem interactions.
    """
    if not filename:
        return "unnamed_document"
    
    # Strip path elements
    cleaned = Path(filename).name
    # Remove null bytes and non-printable characters
    cleaned = cleaned.replace("\x00", "").strip()
    # Replace dangerous filesystem characters
    cleaned = re.sub(r'[^a-zA-Z0-9_\-\. ]', '_', cleaned)
    # Ensure no leading dots (hidden files)
    cleaned = cleaned.lstrip(".")

    return cleaned or "document"


def create_safe_temp_filepath(suffix: str) -> Path:
    """
    Generates a secure temporary file path using an internal UUID
    rather than trusting any client-supplied name.
    """
    clean_suffix = suffix.lower() if suffix.startswith(".") else f".{suffix.lower()}"
    filename = f"{uuid.uuid4().hex}{clean_suffix}"
    return settings.temp_storage_dir / filename
