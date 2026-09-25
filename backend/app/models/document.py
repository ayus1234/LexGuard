"""
SQLAlchemy ORM models for Documents and Document Chunks with pgvector support.
Preserves existing LexGuard document_id semantics, 3072-dim embeddings, and citation metadata.
"""

from datetime import datetime, timezone
from dataclasses import dataclass
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector

from typing import TYPE_CHECKING, Any, Dict, List, Optional
from sqlalchemy.orm import relationship, Mapped, mapped_column

if TYPE_CHECKING:
    from app.core.config import settings
    from app.db.base import Base
else:
    try:
        from backend.app.core.config import settings
        from backend.app.db.base import Base
    except ImportError:
        from app.core.config import settings
        from app.db.base import Base


@dataclass
class PageData:
    page_number: int
    text: str
    character_start: int
    character_end: int
    word_count: int


@dataclass
class SectionData:
    title: str
    page_number: int
    character_offset: int


class DocumentModel(Base):
    __tablename__ = "documents"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    document_type: Mapped[str] = mapped_column(String(16), nullable=False)  # 'pdf', 'docx', 'txt'
    source_type: Mapped[str] = mapped_column(String(32), default="upload", nullable=False)
    mime_type: Mapped[str] = mapped_column(String(64), nullable=False)
    word_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    character_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    page_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), index=True, nullable=False)  # SHA-256
    processing_status: Mapped[str] = mapped_column(String(32), default="uploaded", nullable=False)  # 'uploaded', 'indexed', 'deleted'
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    chunks: Mapped[List["DocumentChunkModel"]] = relationship(
        "DocumentChunkModel",
        back_populates="document",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"<DocumentModel(document_id='{self.document_id}', filename='{self.filename}', status='{self.processing_status}')>"


class DocumentChunkModel(Base):
    __tablename__ = "document_chunks"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("documents.document_id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    chunk_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[Any] = mapped_column(Vector(settings.EMBEDDING_DIMENSION), nullable=False)
    
    # Grounding & citation anchor metadata
    page_start: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    page_end: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    char_start: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    char_end: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    section: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    heading: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    chunk_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    token_estimate: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    chunk_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    document: Mapped[Optional["DocumentModel"]] = relationship("DocumentModel", back_populates="chunks")

    def __repr__(self) -> str:
        return f"<DocumentChunkModel(chunk_id='{self.chunk_id}', document_id='{self.document_id}', page={self.page_start})>"
