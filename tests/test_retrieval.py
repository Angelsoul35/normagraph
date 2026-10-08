from __future__ import annotations

from normagraph.data import NORMS, RELATIONS
from normagraph.graph import NormGraph
from normagraph.retrieval import NormRetriever


def _retriever() -> NormRetriever:
    return NormRetriever(NormGraph(NORMS, RELATIONS))


def test_search_finds_relevant_norm():
    hits = _retriever().search("breach notification within 72 hours", k=3)
    assert hits[0].norm_id == "ART-7"
    assert hits[0].via == "match"


def test_retrieve_expands_along_graph():
    retriever = _retriever()
    hits = retriever.retrieve("consent must be informed", k=1, hops=1)
    vias = {h.via for h in hits}
    assert "match" in vias and "graph" in vias
    # ART-4 (consent) references ART-2 and ART-3; those should appear via graph.
    ids = {h.norm_id for h in hits}
    assert "ART-4" in ids
    assert ids & {"ART-2", "ART-3", "ART-5"}


def test_search_returns_nothing_for_irrelevant_query():
    hits = _retriever().search("zzzzz nonexistent topic qqqq", k=3)
    assert hits == []
