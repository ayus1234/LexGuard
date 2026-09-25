from abc import ABC, abstractmethod
from typing import List, Tuple, TYPE_CHECKING
from pydantic import BaseModel

if TYPE_CHECKING:
    from app.schemas.retrieval import DocumentChunk
else:
    try:
        from backend.app.schemas.retrieval import DocumentChunk
    except ImportError:
        from app.schemas.retrieval import DocumentChunk


class BaseVectorStore(ABC):
    """
    Abstract interface for vector database storage and similarity retrieval.
    Enables swapping between ChromaDB, pgvector, or in-memory test doubles.
    """

    @abstractmethod
    def add_chunks(
        self, document_id: str, chunks: List[DocumentChunk], embeddings: List[List[float]]
    ) -> None:
        pass

    @abstractmethod
    def search(
        self, document_id: str, query_embedding: List[float], top_k: int = 5
    ) -> List[Tuple[DocumentChunk, float]]:
        pass

    @abstractmethod
    def delete_document(self, document_id: str) -> bool:
        pass

    @abstractmethod
    def is_indexed(self, document_id: str) -> bool:
        pass

    @abstractmethod
    def health_check(self) -> bool:
        pass
