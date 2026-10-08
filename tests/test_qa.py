from __future__ import annotations

from normagraph.data import NORMS, RELATIONS
from normagraph.graph import NormGraph
from normagraph.llm.fake import FailingLLM, FakeLLM
from normagraph.qa import RegulationQA
from normagraph.retrieval import NormRetriever


def _qa(llm):
    graph = NormGraph(NORMS, RELATIONS)
    return RegulationQA(graph, NormRetriever(graph), llm=llm)


def test_llm_path_cites_norms():
    qa = _qa(FakeLLM("A breach must be reported within 72 hours [ART-7]."))
    result = qa.answer("breach reporting deadline", k=2, hops=1)
    assert result.source == "llm"
    assert "72 hours" in result.answer
    assert result.cited_norms  # retrieved norm ids attached


def test_fallback_returns_top_norm():
    qa = _qa(FailingLLM())
    result = qa.answer("how long to report a data breach", k=3, hops=1)
    assert result.source == "retrieval"
    assert result.cited_norms == ["ART-7"]
    assert "72 hours" in result.answer


def test_no_match_returns_not_found():
    qa = _qa(FailingLLM())
    result = qa.answer("zzzz qqqq nonexistent", k=3, hops=0)
    assert result.source == "retrieval"
    assert "No relevant norm" in result.answer
