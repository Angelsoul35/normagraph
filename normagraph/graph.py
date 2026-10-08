"""The knowledge graph: norms as nodes, typed relationships as directed edges.

Built on NetworkX. An edge ``source --type--> target`` reads naturally: a norm
*references* / *amends* / *repeals* / *implements* another. On top of the graph
sit the queries that make it useful — what a norm cites, what cites it, its
amendment chain, and the impact of changing it (everything that depends on it).
"""

from __future__ import annotations

from collections import deque

import networkx as nx

from .norms import Norm, Relation, RelationType, Status

# Relationships through which a dependency flows: if T changes, everything that
# references or implements T is potentially affected.
DEPENDENCY_TYPES = (RelationType.REFERENCES, RelationType.IMPLEMENTS)


class NormGraph:
    def __init__(self, norms: list[Norm], relations: list[Relation]) -> None:
        self._norms = {n.id: n for n in norms}
        self.g = nx.MultiDiGraph()
        for norm in norms:
            self.g.add_node(norm.id, title=norm.title, status=norm.status)
        self._relations = list(relations)
        for rel in relations:
            self.g.add_edge(rel.source, rel.target, type=rel.type)

    # --- basic access -------------------------------------------------------
    def norm(self, norm_id: str) -> Norm | None:
        return self._norms.get(norm_id)

    @property
    def norms(self) -> list[Norm]:
        return list(self._norms.values())

    @property
    def relations(self) -> list[Relation]:
        return list(self._relations)

    def _out(self, norm_id: str, rtype: RelationType) -> list[str]:
        if norm_id not in self.g:
            return []
        return sorted(
            {t for _, t, d in self.g.out_edges(norm_id, data=True) if d["type"] == rtype}
        )

    def _in(self, norm_id: str, rtype: RelationType) -> list[str]:
        if norm_id not in self.g:
            return []
        return sorted(
            {s for s, _, d in self.g.in_edges(norm_id, data=True) if d["type"] == rtype}
        )

    # --- queries ------------------------------------------------------------
    def references_of(self, norm_id: str) -> list[str]:
        """Norms this norm cites."""
        return self._out(norm_id, RelationType.REFERENCES)

    def referenced_by(self, norm_id: str) -> list[str]:
        """Norms that cite this norm."""
        return self._in(norm_id, RelationType.REFERENCES)

    def amendment_chain(self, norm_id: str) -> list[str]:
        """Follow AMENDS edges forward from this norm (what it amends, and so on)."""
        chain: list[str] = []
        seen = {norm_id}
        current = norm_id
        while True:
            nxt = self._out(current, RelationType.AMENDS)
            nxt = [n for n in nxt if n not in seen]
            if not nxt:
                break
            current = nxt[0]
            seen.add(current)
            chain.append(current)
        return chain

    def impact_of(self, norm_id: str, max_hops: int | None = None) -> list[str]:
        """Every norm that depends (transitively) on this one.

        Follows dependency edges backwards: if X references or implements the
        target, X is impacted when the target changes.
        """
        affected: set[str] = set()
        queue: deque[tuple[str, int]] = deque([(norm_id, 0)])
        while queue:
            node, hops = queue.popleft()
            if max_hops is not None and hops >= max_hops:
                continue
            for s, _, d in self.g.in_edges(node, data=True):
                if d["type"] in DEPENDENCY_TYPES and s not in affected:
                    affected.add(s)
                    queue.append((s, hops + 1))
        return sorted(affected)

    def neighbors(self, norm_id: str, hops: int = 1) -> list[str]:
        """Ids within ``hops`` of this norm, ignoring edge direction and type."""
        if norm_id not in self.g:
            return []
        undirected = self.g.to_undirected(as_view=True)
        found: set[str] = set()
        frontier = {norm_id}
        for _ in range(hops):
            nxt: set[str] = set()
            for node in frontier:
                nxt |= set(undirected.neighbors(node))
            found |= nxt
            frontier = nxt
        found.discard(norm_id)
        return sorted(found)

    def in_force(self, norm_id: str) -> bool:
        norm = self.norm(norm_id)
        return norm is not None and norm.status is Status.IN_FORCE
