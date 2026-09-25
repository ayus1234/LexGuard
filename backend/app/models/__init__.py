try:
    from backend.app.db.base import Base
    from backend.app.models.document import DocumentModel, PageData, SectionData
    from backend.app.models.chunk import DocumentChunkModel
except ImportError:
    from app.db.base import Base
    from app.models.document import DocumentModel, PageData, SectionData
    from app.models.chunk import DocumentChunkModel

__all__ = ["Base", "DocumentModel", "DocumentChunkModel", "PageData", "SectionData"]

