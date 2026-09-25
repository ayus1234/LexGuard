"""
Re-export DocumentChunkModel from backend.app.models.document.
"""

try:
    from backend.app.models.document import DocumentChunkModel
except ImportError:
    from app.models.document import DocumentChunkModel

__all__ = ["DocumentChunkModel"]
