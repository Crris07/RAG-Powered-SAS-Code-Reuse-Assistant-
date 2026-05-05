"""Vector store operations"""

from typing import List, Optional

try:
    import chromadb
except ImportError:
    chromadb = None

from src.core.logger import get_logger

logger = get_logger(__name__)


class VectorStore:
    """Interface for vector database operations"""

    def __init__(self, db_path: str = "./data/vector_db"):
        self.db_path = db_path
        self._initialize_client()

    def _initialize_client(self):
        """Initialize ChromaDB client"""
        if chromadb is None:
            raise ImportError("chromadb not installed. Run: pip install chromadb")

        self.client = chromadb.PersistentClient(path=self.db_path)
        self.collection = self.client.get_or_create_collection(
            name="sas_code",
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(f"Initialized ChromaDB at {self.db_path}")

    def add_documents(
        self,
        ids: List[str],
        documents: List[str],
        embeddings: Optional[List[List[float]]] = None,
        metadatas: Optional[List[dict]] = None,
    ) -> None:
        """Add documents to vector store"""
        try:
            payload = {
                "ids": ids,
                "documents": documents,
                "metadatas": metadatas or [{}] * len(ids),
            }
            if embeddings is not None:
                payload["embeddings"] = embeddings

            self.collection.add(**payload)
            logger.info(f"Added {len(ids)} documents to vector store")
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise

    def query(
        self,
        query_text: Optional[str] = None,
        query_embedding: Optional[List[float]] = None,
        top_k: int = 3,
        where: Optional[dict] = None,
    ) -> dict:
        """Query vector store for similar documents"""
        try:
            if query_text is None and query_embedding is None:
                raise ValueError("query_text or query_embedding is required")

            payload = {"n_results": top_k}
            if where is not None:
                payload["where"] = where
            if query_embedding is not None:
                payload["query_embeddings"] = [query_embedding]
            else:
                payload["query_texts"] = [query_text]

            results = self.collection.query(**payload)
            return results
        except Exception as e:
            logger.error(f"Query failed: {e}")
            raise

    def get_all_documents(self) -> List[dict]:
        """Return all stored documents with metadata for keyword retrieval."""
        results = self.collection.get(include=["documents", "metadatas"])
        documents = results.get("documents") or []
        metadatas = results.get("metadatas") or []
        ids = results.get("ids") or []
        return [
            {
                "id": ids[i],
                "code": documents[i],
                "metadata": metadatas[i] if i < len(metadatas) else {},
            }
            for i in range(len(ids))
        ]

    def get_collection_size(self) -> int:
        """Get number of documents in collection"""
        return self.collection.count()

    def clear_collection(self) -> None:
        """Clear all documents from collection"""
        try:
            # Delete collection and recreate
            self.client.delete_collection(name="sas_code")
            self.collection = self.client.get_or_create_collection(
                name="sas_code",
                metadata={"hnsw:space": "cosine"},
            )
            logger.info("Cleared vector store")
        except Exception as e:
            logger.error(f"Failed to clear collection: {e}")
            raise
