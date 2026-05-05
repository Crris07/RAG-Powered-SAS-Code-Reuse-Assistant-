"""Required reranking stage for retrieved SAS chunks."""

from typing import Dict, List

from src.core.logger import get_logger

logger = get_logger(__name__)

try:
    from sentence_transformers import CrossEncoder
except ImportError:
    CrossEncoder = None


class RetrievalReranker:
    """Rerank candidate chunks with a cross-encoder model."""

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        if CrossEncoder is None:
            raise ImportError("sentence-transformers is required for reranking")

        self.model_name = model_name
        try:
            self.model = CrossEncoder(model_name, local_files_only=True)
            logger.info(f"Loaded reranker model: {model_name}")
        except Exception as e:
            logger.warning(f"Reranker model not found in local cache, trying download: {e}")
            try:
                self.model = CrossEncoder(model_name)
                logger.info(f"Downloaded and loaded reranker model: {model_name}")
            except Exception as download_error:
                logger.error(f"Failed to load reranker model: {download_error}")
                raise

    def rerank(self, query: str, candidates: List[Dict], top_k: int = 3) -> List[Dict]:
        """Rerank candidates and return the final top K results."""
        if not candidates:
            return []

        pairs = [(query, candidate["code"]) for candidate in candidates]
        scores = self.model.predict(pairs)

        reranked = []
        for candidate, score in zip(candidates, scores):
            item = dict(candidate)
            item["rerank_score"] = float(score)
            item["final_score"] = self._final_score(item, query)
            reranked.append(item)

        return sorted(reranked, key=lambda item: item["final_score"], reverse=True)[:top_k]

    def _final_score(self, item: Dict, query: str) -> float:
        """Blend reranker score with retrieval scores and SAS block usefulness."""
        metadata = item.get("metadata", {})
        chunk_type = metadata.get("chunk_type", "")
        code = item.get("code", "").strip().lower()
        normalized_query = query.lower()

        block_boost = 0.0
        if chunk_type == "data_step" or code.startswith("data "):
            block_boost = 1.0
        elif chunk_type.startswith("proc_sql"):
            block_boost = 0.7
        elif chunk_type.startswith("proc_report") or code.startswith("proc report"):
            block_boost = 0.6
        elif self._is_setup_or_cleanup_chunk(code):
            block_boost = -2.5
        elif code.startswith("proc print"):
            block_boost = -0.5

        query_boost = 0.0
        if "adsl" in normalized_query and "data adsl" in code:
            query_boost += 2.0
        if "safety" in normalized_query and ("saffl" in code or "safety" in code):
            query_boost += 0.8
        if "demographic" in normalized_query and ("set adam.dm" in code or "age categorization" in code):
            query_boost += 1.0
        if "listing" in normalized_query and code.startswith("proc report"):
            query_boost += 0.8
        if "shift" in normalized_query and "basecat" in code and "postcat" in code:
            query_boost += 0.8
        if ("pfs" in normalized_query or "progression" in normalized_query) and "data adtte" in code:
            query_boost += 1.0

        short_chunk_penalty = -0.4 if len(code.split()) < 12 else 0.0

        return (
            item.get("rerank_score", 0.0)
            + (2.0 * item.get("hybrid_score", 0.0))
            + block_boost
            + query_boost
            + short_chunk_penalty
        )

    def _is_setup_or_cleanup_chunk(self, code: str) -> bool:
        """Identify housekeeping chunks that should not lead retrieval results."""
        cleanup_terms = (
            "proc datasets",
            "delete ",
            "proc delete",
            "libname ",
            "options ",
        )
        derivation_terms = (
            "\ndata ",
            "data ",
            "set adam.",
            "merge ",
            "proc sql",
            "proc report",
        )

        has_cleanup = any(term in code for term in cleanup_terms)
        has_derivation = any(term in code for term in derivation_terms)

        return has_cleanup and not has_derivation
