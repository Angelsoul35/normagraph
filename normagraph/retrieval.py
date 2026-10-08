"""Retrieve relevant norms by text, then expand along the graph.

A plain text search finds the norms that match a query; the graph then adds their
neighbours (what they reference, what references them). Regulation is highly
cross-referential, so the norms around a match are often as important as the match
itself. This is retrieval that uses structure, not just keywords.
"""

from __future__ import annotations

from dataclasses import dataclass

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .graph import NormGraph


@dataclass(frozen=True)
class Hit:
    norm_id: str
    title: str
    score: float
    via: str  # "match" or "graph"


class NormRetriever:
    def __init__(self, graph: NormGraph) -> None:
        self.graph = graph
        self._ids = [n.id for n in graph.norms]
        corpus = [f"{n.title}. {n.text}" for n in graph.norms]
        self._vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
        self._matrix = self._vectorizer.fit_transform(corpus)

    def search(self, query: str, k: int = 3) -> list[Hit]:
        q = self._vectorizer.transform([query])
        sims = cosine_similarity(q, self._matrix).ravel()
        order = sims.argsort()[::-1][:k]
        hits: list[Hit] = []
        for i in order:
            if sims[int(i)] <= 0:
                continue
            norm = self.graph.norms[int(i)]
            hits.append(
                Hit(
                    norm_id=norm.id,
                    title=norm.title,
                    score=round(float(sims[int(i)]), 4),
                    via="match",
                )
            )
        return hits

    def retrieve(self, query: str, k: int = 3, hops: int = 1) -> list[Hit]:
        """Text matches plus their graph neighbours, matches first."""
        matches = self.search(query, k)
        seen = {h.norm_id for h in matches}
        expanded: list[Hit] = list(matches)
        for hit in matches:
            for neighbor in self.graph.neighbors(hit.norm_id, hops=hops):
                if neighbor in seen:
                    continue
                seen.add(neighbor)
                norm = self.graph.norm(neighbor)
                if norm is not None:
                    expanded.append(Hit(norm_id=norm.id, title=norm.title, score=0.0, via="graph"))
        return expanded
