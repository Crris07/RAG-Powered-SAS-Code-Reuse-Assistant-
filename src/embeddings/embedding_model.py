"""Embedding generation"""

from typing import Any, List, Optional, Type

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

from src.core.logger import get_logger

logger = get_logger(__name__)


class EmbeddingGenerator:
    """Generate embeddings for code snippets"""

    def __init__(self, model_name: str = "intfloat/e5-small-v2"):
        self.model_name = model_name
        self.model: Any = None
        self._load_model()

    def _load_model(self):
        """Load sentence transformer model"""
        sentence_transformer: Optional[Type[Any]] = SentenceTransformer
        if sentence_transformer is None:
            raise ImportError(
                "sentence-transformers not installed. "
                "Run: pip install sentence-transformers"
        )

        try:
            self.model = sentence_transformer(self.model_name, local_files_only=True)
            logger.info(f"Loaded embedding model: {self.model_name}")
        except Exception as e:
            logger.warning(f"Embedding model not found in local cache, trying download: {e}")
            try:
                self.model = sentence_transformer(self.model_name)
                logger.info(f"Downloaded and loaded embedding model: {self.model_name}")
            except Exception as download_error:
                logger.error(f"Failed to load embedding model: {download_error}")
                raise

    def encode(self, texts: List[str]) -> List[List[float]]:
        """
        Encode texts to embeddings
        
        Args:
            texts: List of text strings
            
        Returns:
            List of embedding vectors
        """
        try:
            embeddings = self.model.encode(texts, convert_to_tensor=False)
            return embeddings.tolist() if hasattr(embeddings, "tolist") else embeddings
        except Exception as e:
            logger.error(f"Encoding failed: {e}")
            raise

    def get_embedding_dimension(self) -> int:
        """Get dimension of embeddings"""
        return self.model.get_sentence_embedding_dimension()
