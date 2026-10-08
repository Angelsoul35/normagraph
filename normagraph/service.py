"""Tie the pieces together: graph, retrieval, integrity analysis, and QA."""

from __future__ import annotations

from dataclasses import asdict

from .analysis import IntegrityReport, analyze
from .config import Settings, get_settings
from .data import NORMS, RELATIONS
from .graph import NormGraph
from .llm.base import LLMClient
from .llm.factory import build_llm
from .norms import Norm, Relation
from .qa import RegulationQA
from .retrieval import NormRetriever


class NormaGraphService:
    def __init__(
        self,
        settings: Settings | None = None,
        norms: list[Norm] | None = None,
        relations: list[Relation] | None = None,
        llm: LLMClient | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.graph = NormGraph(
            norms if norms is not None else NORMS,
            relations if relations is not None else RELATIONS,
        )
        self.retriever = NormRetriever(self.graph)
        self.llm = llm if llm is not None else build_llm(self.settings.llm_spec)
        self.qa = RegulationQA(
            self.graph, self.retriever, llm=self.llm, max_tokens=self.settings.llm_max_tokens
        )

    def search(self, query: str) -> list[dict]:
        hits = self.retriever.retrieve(query, k=self.settings.top_k, hops=self.settings.expand_hops)
        return [
            {"norm_id": h.norm_id, "title": h.title, "score": h.score, "via": h.via} for h in hits
        ]

    def norm_detail(self, norm_id: str) -> dict | None:
        norm = self.graph.norm(norm_id)
        if norm is None:
            return None
        return {
            "id": norm.id,
            "title": norm.title,
            "text": norm.text,
            "status": norm.status.value,
            "references": self.graph.references_of(norm_id),
            "referenced_by": self.graph.referenced_by(norm_id),
            "amendment_chain": self.graph.amendment_chain(norm_id),
            "impact": self.graph.impact_of(norm_id),
        }

    def integrity(self) -> IntegrityReport:
        return analyze(self.graph)

    def integrity_as_dict(self) -> dict:
        report = self.integrity()
        return {
            "ok": report.ok,
            "findings": [asdict(f) for f in report.findings],
        }

    def ask(self, question: str) -> dict:
        result = self.qa.answer(question, k=self.settings.top_k, hops=self.settings.expand_hops)
        return asdict(result)
