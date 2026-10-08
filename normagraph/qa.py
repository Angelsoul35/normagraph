"""Answer a question about the regulations, grounded in retrieved norms.

The retriever gathers the relevant norms and their graph neighbours; this layer
asks the LLM to answer using only that context and to cite the norm ids it used.
If the LLM is unreachable, it falls back to returning the top matching norm's
text — correct and traceable, if less polished.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .graph import NormGraph
from .llm.base import LLMClient, LLMError
from .retrieval import NormRetriever

_SYSTEM = (
    "You are a regulatory analyst. Answer the question using ONLY the provided "
    "norms. Cite the norm ids you rely on in brackets. If the norms do not cover "
    "the question, say so. Keep the answer to a few sentences."
)


@dataclass
class QAResult:
    question: str
    answer: str
    cited_norms: list[str] = field(default_factory=list)
    source: str = "retrieval"


class RegulationQA:
    def __init__(
        self,
        graph: NormGraph,
        retriever: NormRetriever,
        llm: LLMClient | None = None,
        max_tokens: int = 400,
    ) -> None:
        self.graph = graph
        self.retriever = retriever
        self.llm = llm
        self.max_tokens = max_tokens

    def _context(self, norm_ids: list[str]) -> str:
        lines = []
        for nid in norm_ids:
            norm = self.graph.norm(nid)
            if norm is not None:
                lines.append(f"[{norm.id}] {norm.title}: {norm.text}")
        return "\n".join(lines)

    def answer(self, question: str, k: int = 3, hops: int = 1) -> QAResult:
        hits = self.retriever.retrieve(question, k=k, hops=hops)
        norm_ids = [h.norm_id for h in hits]
        context = self._context(norm_ids)

        if self.llm is not None and context:
            try:
                prompt = f"Norms:\n{context}\n\nQuestion: {question}\n\nAnswer:"
                result = self.llm.complete(_SYSTEM, prompt, max_tokens=self.max_tokens)
                text = result.text.strip()
                if text:
                    return QAResult(
                        question=question, answer=text, cited_norms=norm_ids, source="llm"
                    )
            except LLMError:
                pass

        if hits:
            top = self.graph.norm(hits[0].norm_id)
            answer = f"{top.title}: {top.text}" if top else "No relevant norm found."
            return QAResult(
                question=question,
                answer=answer,
                cited_norms=[hits[0].norm_id],
                source="retrieval",
            )
        return QAResult(question=question, answer="No relevant norm found.", source="retrieval")
