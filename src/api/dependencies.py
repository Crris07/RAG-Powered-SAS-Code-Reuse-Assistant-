"""Dependency injection for API"""

from src.embeddings.vector_store import VectorStore
from src.embeddings.embedding_model import EmbeddingGenerator
from src.rag.retriever import CodeRetriever
from src.llm.code_generator import CodeGenerator


def get_vector_store() -> VectorStore:
    """Get vector store instance"""
    return VectorStore()


def get_embedding_generator() -> EmbeddingGenerator:
    """Get embedding generator instance"""
    return EmbeddingGenerator()


def get_retriever(vector_store: VectorStore = None) -> CodeRetriever:
    """Get retriever instance"""
    if vector_store is None:
        vector_store = get_vector_store()
    return CodeRetriever(vector_store)


def get_code_generator() -> CodeGenerator:
    """Get code generator instance"""
    return CodeGenerator()
