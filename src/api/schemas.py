"""Pydantic schemas for API"""

from typing import List, Optional

from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    """Request for code generation"""

    requirement: str = Field(..., description="Code requirement or query")
    top_k: int = Field(3, ge=1, le=10, description="Number of similar snippets to retrieve")
    temperature: Optional[float] = Field(0.2, ge=0.0, le=1.0)
    max_tokens: Optional[int] = Field(1024, ge=100, le=4000)


class RetrievedSnippet(BaseModel):
    """Retrieved code snippet"""

    id: str
    code: str
    similarity: Optional[float] = None
    rerank_score: Optional[float] = None
    final_score: Optional[float] = None
    hybrid_score: Optional[float] = None
    keyword_score: Optional[float] = None
    retrieval_sources: List[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


class GenerateResponse(BaseModel):
    """Response from code generation"""

    requirement: str
    generated_code: str
    retrieved_snippets: List[RetrievedSnippet]
    assumptions: List[str] = Field(default_factory=list)
    status: str


class RetrievalResponse(BaseModel):
    """Response from retrieval"""

    query: str
    snippets: List[RetrievedSnippet]
    count: int
    status: str
