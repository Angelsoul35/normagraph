from __future__ import annotations

from normagraph.data import NORMS, RELATIONS
from normagraph.graph import NormGraph
from normagraph.norms import Norm, Relation, RelationType


def _graph() -> NormGraph:
    return NormGraph(NORMS, RELATIONS)


def test_references_and_referenced_by():
    g = _graph()
    assert "ART-2" in g.references_of("ART-4")
    assert "ART-3" in g.references_of("ART-4")
    # ART-5 references ART-4, so ART-5 is among the norms that reference ART-4.
    assert "ART-5" in g.referenced_by("ART-4")
    # ART-6 references ART-5, so ART-6 is among the norms that reference ART-5.
    assert "ART-6" in g.referenced_by("ART-5")


def test_impact_is_transitive():
    g = _graph()
    impact = g.impact_of("ART-2")
    # Direct dependents and transitive ones.
    assert {"ART-3", "ART-4", "ART-7", "ART-8"} <= set(impact)
    assert "ART-5" in impact and "ART-6" in impact  # via ART-4 -> ART-5 -> ART-6
    assert "REG-2019" in impact  # via ART-7


def test_impact_respects_max_hops():
    g = _graph()
    one_hop = g.impact_of("ART-2", max_hops=1)
    assert set(one_hop) == {"ART-3", "ART-4", "ART-7", "ART-8"}


def test_neighbors_are_undirected():
    g = _graph()
    neighbors = g.neighbors("ART-4", hops=1)
    assert "ART-2" in neighbors  # ART-4 -> ART-2
    assert "ART-5" in neighbors  # ART-5 -> ART-4


def test_amendment_chain():
    norms = [
        Norm("A", "A", "x"),
        Norm("B", "B", "x"),
        Norm("C", "C", "x"),
    ]
    rels = [
        Relation("A", "B", RelationType.AMENDS),
        Relation("B", "C", RelationType.AMENDS),
    ]
    g = NormGraph(norms, rels)
    assert g.amendment_chain("A") == ["B", "C"]


def test_in_force():
    g = _graph()
    assert g.in_force("ART-2") is True
    assert g.in_force("ART-8-OLD") is False
    assert g.in_force("UNKNOWN") is False
