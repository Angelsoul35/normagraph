from __future__ import annotations

from normagraph.analysis import analyze
from normagraph.data import NORMS, RELATIONS
from normagraph.graph import NormGraph
from normagraph.norms import Norm, Relation, RelationType, Status


def test_default_corpus_findings():
    report = analyze(NormGraph(NORMS, RELATIONS))
    assert not report.ok
    kinds = {f.kind for f in report.findings}
    assert "dangling_reference" in kinds
    assert "depends_on_repealed" in kinds
    assert "orphan" in kinds
    assert report.by_kind("dangling_reference")[0].norm_id == "DECREE-5"


def test_clean_graph_is_ok():
    norms = [Norm("A", "A", "x"), Norm("B", "B", "y")]
    rels = [Relation("A", "B", RelationType.REFERENCES)]
    assert analyze(NormGraph(norms, rels)).ok


def test_repealed_still_in_force():
    norms = [
        Norm("NEW", "New rule", "x"),
        Norm("OLD", "Old rule", "y", Status.IN_FORCE),  # should be repealed
    ]
    rels = [Relation("NEW", "OLD", RelationType.REPEALS)]
    report = analyze(NormGraph(norms, rels))
    assert report.by_kind("repealed_still_in_force")[0].norm_id == "OLD"


def test_amendment_cycle():
    norms = [Norm("A", "A", "x"), Norm("B", "B", "y")]
    rels = [
        Relation("A", "B", RelationType.AMENDS),
        Relation("B", "A", RelationType.AMENDS),
    ]
    report = analyze(NormGraph(norms, rels))
    assert report.by_kind("amendment_cycle")
