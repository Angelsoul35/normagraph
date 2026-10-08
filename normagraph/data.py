"""A synthetic regulatory corpus: a fictional Data Protection Act and friends.

It is realistic enough to show the graph at work — cross-references, an
implementing regulation, a repealed article and its replacement — and it embeds a
few deliberate defects (a reference to a non-existent norm, an in-force article
that still points at a repealed one, an orphan guidance note) so the integrity
checks have something to find.
"""

from __future__ import annotations

from .norms import Norm, Relation, RelationType, Status

NORMS: list[Norm] = [
    Norm(
        "LAW-2018",
        "Data Protection Act 2018",
        "Establishes the framework for processing personal data.",
    ),
    Norm(
        "ART-1",
        "Scope",
        "This Act applies to the processing of personal data by controllers and processors.",
    ),
    Norm(
        "ART-2",
        "Definitions",
        "Defines personal data, processing, controller, processor and consent.",
    ),
    Norm(
        "ART-3",
        "Lawful basis for processing",
        "Processing is lawful only if a lawful basis under this Article applies.",
    ),
    Norm("ART-4", "Consent", "Consent must be freely given, specific, informed and unambiguous."),
    Norm(
        "ART-5",
        "Rights of the data subject",
        "Data subjects have rights of access, rectification and objection.",
    ),
    Norm(
        "ART-6",
        "Right to erasure",
        "A data subject may request erasure of personal data without undue delay.",
    ),
    Norm(
        "ART-7",
        "Personal data breach notification",
        "A personal data breach must be notified to the authority within 72 hours.",
    ),
    Norm(
        "ART-8",
        "International transfers",
        "Transfers of personal data outside the country require adequate safeguards.",
    ),
    Norm(
        "ART-8-OLD",
        "International transfers (former)",
        "Former rules governing international data transfers.",
        Status.REPEALED,
    ),
    Norm(
        "REG-2019",
        "Implementing Regulation 2019",
        "Technical and organisational measures implementing the Act.",
    ),
    Norm(
        "DECREE-5",
        "Decree 5 on the controllers registry",
        "Creates and governs the national registry of data controllers.",
    ),
    Norm(
        "NOTE-1",
        "Guidance note on cookies",
        "Non-binding guidance on cookie consent banners and trackers.",
    ),
]

RELATIONS: list[Relation] = [
    Relation("ART-1", "LAW-2018", RelationType.REFERENCES),
    Relation("ART-3", "ART-2", RelationType.REFERENCES),
    Relation("ART-4", "ART-2", RelationType.REFERENCES),
    Relation("ART-4", "ART-3", RelationType.REFERENCES),
    Relation("ART-5", "ART-4", RelationType.REFERENCES),
    Relation("ART-6", "ART-5", RelationType.REFERENCES),
    Relation("ART-6", "ART-8-OLD", RelationType.REFERENCES),  # depends on a repealed norm
    Relation("ART-7", "ART-2", RelationType.REFERENCES),
    Relation("ART-8", "ART-2", RelationType.REFERENCES),
    Relation("ART-8", "ART-8-OLD", RelationType.REPEALS),
    Relation("REG-2019", "LAW-2018", RelationType.IMPLEMENTS),
    Relation("REG-2019", "ART-7", RelationType.REFERENCES),
    Relation("DECREE-5", "MISSING-9", RelationType.REFERENCES),  # dangling reference
    # NOTE-1 has no relations -> orphan.
]
