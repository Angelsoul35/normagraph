"""Integrity checks over the norm graph.

A regulatory corpus accumulates defects: a reference to a norm that was repealed
or never existed, an amendment cycle, a norm nothing connects to, or a norm that
has been repealed yet is still marked in force. These checks surface those issues
so a maintainer can fix the corpus.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import networkx as nx

from .graph import DEPENDENCY_TYPES, NormGraph
from .norms import RelationType, Status


@dataclass
class Finding:
    kind: str
    norm_id: str
    detail: str


@dataclass
class IntegrityReport:
    findings: list[Finding] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.findings

    def by_kind(self, kind: str) -> list[Finding]:
        return [f for f in self.findings if f.kind == kind]


def analyze(graph: NormGraph) -> IntegrityReport:
    findings: list[Finding] = []
    known = {n.id for n in graph.norms}

    # 1. Dangling references: an edge to a norm that does not exist.
    for rel in graph.relations:
        if rel.target not in known:
            findings.append(
                Finding(
                    kind="dangling_reference",
                    norm_id=rel.source,
                    detail=f"{rel.source} {rel.type.value} unknown norm {rel.target}",
                )
            )

    # 2. In-force norm depending on a repealed norm.
    for rel in graph.relations:
        if rel.type not in DEPENDENCY_TYPES:
            continue
        target = graph.norm(rel.target)
        if target is None or not graph.in_force(rel.source):
            continue
        if target.status is Status.REPEALED:
            findings.append(
                Finding(
                    kind="depends_on_repealed",
                    norm_id=rel.source,
                    detail=f"{rel.source} {rel.type.value} repealed norm {rel.target}",
                )
            )

    # 3. A norm that has been repealed by another but is still marked in force.
    for rel in graph.relations:
        if rel.type is not RelationType.REPEALS:
            continue
        target = graph.norm(rel.target)
        if target is not None and target.status is Status.IN_FORCE:
            findings.append(
                Finding(
                    kind="repealed_still_in_force",
                    norm_id=rel.target,
                    detail=f"{rel.target} is repealed by {rel.source} but marked in_force",
                )
            )

    # 4. Amendment cycles.
    amends = nx.DiGraph()
    for rel in graph.relations:
        if rel.type is RelationType.AMENDS and rel.source in known and rel.target in known:
            amends.add_edge(rel.source, rel.target)
    for cycle in nx.simple_cycles(amends):
        ordered = sorted(cycle)
        findings.append(
            Finding(
                kind="amendment_cycle",
                norm_id=ordered[0],
                detail="amendment cycle: " + " -> ".join(cycle + [cycle[0]]),
            )
        )

    # 5. Orphan norms: no relationships at all.
    for norm in graph.norms:
        if graph.g.degree(norm.id) == 0:
            findings.append(
                Finding(
                    kind="orphan",
                    norm_id=norm.id,
                    detail=f"{norm.id} has no relationships",
                )
            )

    return IntegrityReport(findings=findings)
