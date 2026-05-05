"""API routes"""

from functools import lru_cache

from fastapi import APIRouter, HTTPException

from src.core.logger import get_logger
from src.api.schemas import GenerateRequest, GenerateResponse, RetrievalResponse
from src.embeddings.vector_store import VectorStore
from src.embeddings.embedding_model import EmbeddingGenerator
from src.rag.retriever import CodeRetriever
from src.llm.code_generator import CodeGenerator

logger = get_logger(__name__)

router = APIRouter()


@lru_cache(maxsize=1)
def get_vector_store() -> VectorStore:
    """Create the vector store only when an endpoint needs it."""
    return VectorStore()


@lru_cache(maxsize=1)
def get_embedding_generator() -> EmbeddingGenerator:
    """Create the embedding model lazily because it may download model weights."""
    return EmbeddingGenerator()


@lru_cache(maxsize=1)
def get_retriever() -> CodeRetriever:
    """Create the retriever from the cached vector store."""
    return CodeRetriever(get_vector_store())


@lru_cache(maxsize=1)
def get_code_generator() -> CodeGenerator:
    """Create the LLM provider only for generation requests."""
    return CodeGenerator()


def format_snippet(snippet: dict, truncate: bool = False) -> dict:
    """Format internal retrieval output for API responses."""
    code = snippet.get("code", "")
    if truncate and len(code) > 500:
        code = code[:500] + "..."

    return {
        "id": snippet.get("id", ""),
        "code": code,
        "similarity": snippet.get("similarity"),
        "rerank_score": snippet.get("rerank_score"),
        "final_score": snippet.get("final_score"),
        "hybrid_score": snippet.get("hybrid_score"),
        "keyword_score": snippet.get("keyword_score"),
        "retrieval_sources": snippet.get("retrieval_sources", []),
        "metadata": snippet.get("metadata", {}),
    }


def extract_assumptions(generated_code: str) -> list[str]:
    """Extract assumption bullets from generated demo output when present."""
    assumptions = []
    in_assumptions = False

    for line in generated_code.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith("assumptions:"):
            in_assumptions = True
            continue
        if in_assumptions and stripped.startswith("-"):
            assumptions.append(stripped.lstrip("-").strip())
            continue
        if in_assumptions and stripped and not stripped.startswith("-"):
            break

    return assumptions


@router.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest) -> GenerateResponse:
    """
    Generate adapted SAS code for a requirement
    
    Args:
        request: GenerateRequest with requirement and optional parameters
        
    Returns:
        GenerateResponse with adapted code and metadata
    """
    try:
        logger.info(f"Generate request: {request.requirement[:100]}...")

        retriever = get_retriever()
        code_gen = get_code_generator()

        # Retrieve similar code snippets
        retrieved = retriever.retrieve(
            query=request.requirement,
            top_k=request.top_k,
        )

        if not retrieved:
            logger.warning("No similar code found")
            # Still generate code without context
            adapted_code = code_gen.generate_code(request.requirement)
        else:
            # Format retrieved code as context
            context = retriever.format_context(retrieved)

            # Adapt retrieved code
            adapted_code = code_gen.adapt_code(
                context=context,
                requirement=request.requirement,
            )

        return GenerateResponse(
            requirement=request.requirement,
            generated_code=adapted_code,
            retrieved_snippets=[format_snippet(snippet, truncate=True) for snippet in retrieved],
            assumptions=extract_assumptions(adapted_code),
            status="success",
        )

    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Generation failed",
                "error": str(e),
                "hint": "Confirm the vector DB is ingested and required local models are cached.",
            },
        )


@router.post("/retrieve", response_model=RetrievalResponse)
async def retrieve(query: str, top_k: int = 3) -> RetrievalResponse:
    """
    Retrieve similar code snippets without generation
    
    Args:
        query: Search query
        top_k: Number of results to return
        
    Returns:
        RetrievalResponse with retrieved snippets
    """
    try:
        logger.info(f"Retrieve request: {query[:100]}...")

        retriever = get_retriever()
        retrieved = retriever.retrieve(query=query, top_k=top_k)

        return RetrievalResponse(
            query=query,
            snippets=[format_snippet(snippet) for snippet in retrieved],
            count=len(retrieved),
            status="success",
        )

    except Exception as e:
        logger.error(f"Retrieval failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Retrieval failed",
                "error": str(e),
                "hint": "Run ingestion first and confirm embedding/reranker models are cached.",
            },
        )


@router.get("/stats")
async def stats():
    """Get API statistics"""
    try:
        vector_store = get_vector_store()
        collection_size = vector_store.get_collection_size()

        response = {
            "vector_db_documents": collection_size,
            "status": "healthy",
        }

        try:
            response["embedding_dimension"] = get_embedding_generator().get_embedding_dimension()
        except Exception as e:
            response["embedding_dimension"] = None
            response["embedding_model_status"] = f"unavailable: {e}"

        return response
    except Exception as e:
        logger.error(f"Stats retrieval failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Stats retrieval failed",
                "error": str(e),
            },
        )
