"""Keyword retrieval for SAS code chunks."""

import math
import re
from collections import Counter
from typing import Dict, List


class KeywordRetriever:
    """Small BM25 implementation for keyword-based SAS retrieval."""

    TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")

    def __init__(self, documents: List[dict], k1: float = 1.5, b: float = 0.75):
        self.documents = documents
        self.k1 = k1
        self.b = b
        self.doc_tokens = [self._tokenize(doc["code"]) for doc in documents]
        self.doc_lengths = [len(tokens) for tokens in self.doc_tokens]
        self.avg_doc_length = (
            sum(self.doc_lengths) / len(self.doc_lengths) if self.doc_lengths else 0.0
        )
        self.doc_freqs = self._build_doc_freqs()

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict]:
        """Return top keyword matches using BM25 scoring."""
        query_terms = self._tokenize(query)
        if not query_terms or not self.documents:
            return []

        scored = []
        for index, document in enumerate(self.documents):
            score = self._score(query_terms, index)
            if score > 0:
                scored.append(
                    {
                        "id": document["id"],
                        "code": document["code"],
                        "metadata": document.get("metadata", {}),
                        "keyword_score": score,
                    }
                )

        max_score = max((item["keyword_score"] for item in scored), default=0.0)
        for item in scored:
            item["keyword_score_normalized"] = (
                item["keyword_score"] / max_score if max_score else 0.0
            )

        return sorted(scored, key=lambda item: item["keyword_score"], reverse=True)[:top_k]

    def _score(self, query_terms: List[str], doc_index: int) -> float:
        term_counts = Counter(self.doc_tokens[doc_index])
        doc_length = self.doc_lengths[doc_index]
        score = 0.0

        for term in query_terms:
            if term not in term_counts:
                continue

            doc_freq = self.doc_freqs.get(term, 0)
            idf = math.log(1 + (len(self.documents) - doc_freq + 0.5) / (doc_freq + 0.5))
            term_frequency = term_counts[term]
            denominator = term_frequency + self.k1 * (
                1 - self.b + self.b * doc_length / max(self.avg_doc_length, 1.0)
            )
            score += idf * (term_frequency * (self.k1 + 1)) / denominator

        return score

    def _build_doc_freqs(self) -> Counter:
        doc_freqs = Counter()
        for tokens in self.doc_tokens:
            doc_freqs.update(set(tokens))
        return doc_freqs

    def _tokenize(self, text: str) -> List[str]:
        return [token.lower() for token in self.TOKEN_RE.findall(text)]
