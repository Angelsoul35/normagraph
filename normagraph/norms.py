"""The domain model: norms and the relationships between them.

A *norm* is an atomic piece of regulation — an article, a section, a decree. Norms
relate to one another: one *references* another, one *amends* or *repeals*
another, a regulation *implements* a law. These typed relationships are the edges
of the knowledge graph.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Status(StrEnum):
    IN_FORCE = "in_force"
    REPEALED = "repealed"
    DRAFT = "draft"


class RelationType(StrEnum):
    REFERENCES = "references"  # cites another norm
    AMENDS = "amends"  # modifies another norm
    REPEALS = "repeals"  # revokes another norm
    IMPLEMENTS = "implements"  # a regulation implementing a higher norm


@dataclass(frozen=True)
class Norm:
    id: str
    title: str
    text: str
    status: Status = Status.IN_FORCE


@dataclass(frozen=True)
class Relation:
    source: str  # norm id
    target: str  # norm id
    type: RelationType
