"""RAG pipeline - Retriever"""

from typing import Dict, List

from src.core.logger import get_logger
from src.embeddings.embedding_model import EmbeddingGenerator
from src.embeddings.vector_store import VectorStore
from src.rag.keyword_retriever import KeywordRetriever
from src.rag.reranker import RetrievalReranker

logger = get_logger(__name__)


class CodeRetriever:
    """Retrieve relevant code snippets from vector store"""

    def __init__(
        self,
        vector_store: VectorStore,
        embedding_generator: EmbeddingGenerator = None,
        reranker: RetrievalReranker = None,
    ):
        self.vector_store = vector_store
        self.embedding_generator = embedding_generator or EmbeddingGenerator()
        self.reranker = reranker or RetrievalReranker()

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
        similarity_threshold: float = 0.0,
    ) -> List[Dict[str, str]]:
        """
        Retrieve top-K similar code snippets
        
        Args:
            query: Requirement or query text
            top_k: Number of results to retrieve
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of retrieved code snippets with metadata
        """
        try:
            candidate_k = max(top_k * 5, 20)
            query_embedding = self.embedding_generator.encode([query])[0]

            vector_results = self.vector_store.query(
                query_embedding=query_embedding,
                top_k=candidate_k,
            )
            vector_candidates = self._format_vector_results(vector_results, similarity_threshold)

            keyword_candidates = KeywordRetriever(
                self.vector_store.get_all_documents()
            ).retrieve(query, top_k=candidate_k)

            merged = self._merge_candidates(vector_candidates, keyword_candidates)
            reranked = self.reranker.rerank(query, merged, top_k=top_k)

            logger.debug(f"Retrieved {len(reranked)} reranked snippets for query")
            return reranked

        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            raise

    def _format_vector_results(self, results: dict, similarity_threshold: float) -> List[Dict]:
        candidates = []
        ids = results.get("ids", [[]])[0]
        documents = results.get("documents", [[]])[0]
        distances = results.get("distances", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0] if results.get("metadatas") else []

        for i, chunk_id in enumerate(ids):
            distance = distances[i] if i < len(distances) else 1.0
            similarity = 1 - distance
            if similarity < similarity_threshold:
                continue

            candidates.append(
                {
                    "id": chunk_id,
                    "code": documents[i],
                    "distance": distance,
                    "similarity": similarity,
                    "vector_score": similarity,
                    "metadata": metadatas[i] if i < len(metadatas) else {},
                }
            )

        return candidates

    def _merge_candidates(
        self,
        vector_candidates: List[Dict],
        keyword_candidates: List[Dict],
    ) -> List[Dict]:
        merged: Dict[str, Dict] = {}

        for candidate in vector_candidates:
            item = dict(candidate)
            item.setdefault("keyword_score_normalized", 0.0)
            item["retrieval_sources"] = ["vector"]
            merged[item["id"]] = item

        for candidate in keyword_candidates:
            if candidate["id"] in merged:
                merged[candidate["id"]]["keyword_score"] = candidate.get("keyword_score", 0.0)
                merged[candidate["id"]]["keyword_score_normalized"] = candidate.get(
                    "keyword_score_normalized", 0.0
                )
                merged[candidate["id"]]["retrieval_sources"].append("keyword")
            else:
                item = dict(candidate)
                item.setdefault("similarity", 0.0)
                item.setdefault("vector_score", 0.0)
                item["retrieval_sources"] = ["keyword"]
                merged[item["id"]] = item

        for item in merged.values():
            item["hybrid_score"] = (
                0.7 * item.get("vector_score", 0.0)
                + 0.3 * item.get("keyword_score_normalized", 0.0)
            )

        return sorted(merged.values(), key=lambda item: item["hybrid_score"], reverse=True)

    def format_context(self, retrieved_snippets: List[Dict]) -> str:
        """
        Format retrieved snippets into context string for LLM
        
        Args:
            retrieved_snippets: List of retrieved snippets
            
        Returns:
            Formatted context string
        """
        context = "## Retrieved Code Examples:\n\n"

        for i, snippet in enumerate(retrieved_snippets, 1):
            similarity = snippet.get("similarity", 0)
            context += f"### Example {i} (Similarity: {similarity:.2%})\n"
            context += f"```sas\n{snippet['code']}\n```\n\n"

        return context
