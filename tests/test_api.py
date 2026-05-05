"""Integration tests for API"""

import pytest
from fastapi.testclient import TestClient

import src.api.routes as routes
from src.api.app import app


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


def test_health_endpoint(client):
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_stats_endpoint(client, monkeypatch):
    """Test stats endpoint"""
    mock_vector_store = type("MockVectorStore", (), {"get_collection_size": lambda self: 49})()
    mock_embedding = type("MockEmbedding", (), {"get_embedding_dimension": lambda self: 384})()
    monkeypatch.setattr(routes, "get_vector_store", lambda: mock_vector_store)
    monkeypatch.setattr(routes, "get_embedding_generator", lambda: mock_embedding)

    response = client.get("/api/stats")
    assert response.status_code == 200
    assert response.json()["vector_db_documents"] == 49


def test_retrieve_endpoint_schema(client, monkeypatch):
    """Test retrieve endpoint accepts correct schema"""
    mock_retriever = type(
        "MockRetriever",
        (),
        {
            "retrieve": lambda self, query, top_k: [
                {"id": "chunk_1", "code": "data adsl; run;", "similarity": 0.9}
            ]
        },
    )()
    monkeypatch.setattr(routes, "get_retriever", lambda: mock_retriever)

    response = client.post(
        "/api/retrieve",
        params={"query": "test query", "top_k": 3},
    )
    assert response.status_code == 200
    assert response.json()["count"] == 1


def test_generate_endpoint_response_shape(client, monkeypatch):
    """Test generate endpoint returns code, snippets, scores, and assumptions."""
    mock_retriever = type(
        "MockRetriever",
        (),
        {
            "retrieve": lambda self, query, top_k: [
                {
                    "id": "chunk_1",
                    "code": "data adsl; run;",
                    "similarity": 0.9,
                    "hybrid_score": 0.8,
                    "rerank_score": 1.2,
                    "final_score": 2.8,
                    "retrieval_sources": ["vector", "keyword"],
                    "metadata": {"code_id": "adsl", "start_line": 1, "end_line": 2},
                }
            ],
            "format_context": lambda self, snippets: "```sas\ndata adsl; run;\n```",
        },
    )()
    mock_generator = type(
        "MockGenerator",
        (),
        {
            "adapt_code": lambda self, context, requirement: (
                "/*\n"
                "Assumptions:\n"
                "- Input ADSL fields are available.\n"
                "*/\n"
                "data adam.adsl; run;"
            )
        },
    )()
    monkeypatch.setattr(routes, "get_retriever", lambda: mock_retriever)
    monkeypatch.setattr(routes, "get_code_generator", lambda: mock_generator)

    response = client.post(
        "/api/generate",
        json={"requirement": "Create ADSL with safety flags", "top_k": 1},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["requirement"] == "Create ADSL with safety flags"
    assert data["generated_code"].startswith("/*")
    assert data["assumptions"] == ["Input ADSL fields are available."]
    assert data["retrieved_snippets"][0]["rerank_score"] == 1.2
    assert data["retrieved_snippets"][0]["final_score"] == 2.8
    assert data["retrieved_snippets"][0]["retrieval_sources"] == ["vector", "keyword"]
