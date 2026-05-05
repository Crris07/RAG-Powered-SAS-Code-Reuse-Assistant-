"""Unit tests for retriever"""

import pytest
from unittest.mock import Mock, MagicMock

from src.rag.retriever import CodeRetriever


@pytest.fixture
def mock_vector_store():
    """Create mock vector store"""
    store = Mock()
    store.query.return_value = {
        "ids": [["chunk_1", "chunk_2", "chunk_3"]],
        "documents": [
            ["code 1", "code 2", "code 3"],
        ],
        "distances": [[0.1, 0.2, 0.3]],
        "metadatas": [[
            {"code_id": "doc1"},
            {"code_id": "doc2"},
            {"code_id": "doc3"},
        ]],
    }
    store.get_all_documents.return_value = [
        {"id": "chunk_1", "code": "code 1", "metadata": {"code_id": "doc1"}},
        {"id": "chunk_4", "code": "adsl safety flags", "metadata": {"code_id": "doc4"}},
    ]
    return store


@pytest.fixture
def mock_embedding_generator():
    generator = Mock()
    generator.encode.return_value = [[0.1, 0.2, 0.3]]
    return generator


@pytest.fixture
def mock_reranker():
    reranker = Mock()
    reranker.rerank.side_effect = lambda query, candidates, top_k: candidates[:top_k]
    return reranker


def test_retrieve_basic(mock_vector_store, mock_embedding_generator, mock_reranker):
    """Test basic retrieval"""
    retriever = CodeRetriever(mock_vector_store, mock_embedding_generator, mock_reranker)
    results = retriever.retrieve("test query", top_k=3)

    assert len(results) == 3
    assert all("id" in r for r in results)
    assert all("code" in r for r in results)
    assert all("similarity" in r for r in results)
    mock_vector_store.query.assert_called_once()
    assert "query_embedding" in mock_vector_store.query.call_args.kwargs
    mock_reranker.rerank.assert_called_once()


def test_format_context(mock_vector_store, mock_embedding_generator, mock_reranker):
    """Test context formatting"""
    retriever = CodeRetriever(mock_vector_store, mock_embedding_generator, mock_reranker)
    results = retriever.retrieve("test query")

    context = retriever.format_context(results)

    assert "Retrieved Code Examples" in context
    assert "code 1" in context
    assert "Similarity:" in context
