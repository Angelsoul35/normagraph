# ADR 0001: Model the corpus as a typed directed graph

## Status

Accepted.

## Context

A regulatory corpus is usually stored as documents or a flat list of articles.
That representation answers "what does Article 7 say?" but not the questions that
matter most in practice: what does this article depend on, what depends on it,
what changes it, and what has been repealed. Those questions are about the
**relationships** between norms, which a flat store does not capture.

## Decision

Model the corpus as a **typed directed graph**: norms are nodes (each with a
status), and relationships are directed edges with a type — `references`,
`amends`, `repeals`, `implements`. Build it on NetworkX as a `MultiDiGraph` (two
norms may be connected by more than one kind of relationship), and express every
useful operation as a graph query.

## Consequences

- **The important questions become queries.** Dependencies, impact, amendment
  lineage, and integrity are traversals, not text searches.
- **Impact analysis falls out naturally.** "What breaks if this changes?" is
  reverse reachability over dependency edges.
- **Extensible.** New relationship types are new edge labels; new questions are
  new traversals. The model does not need reshaping.
- **Trade-off.** The corpus must be modelled as discrete norms and explicit edges,
  which means an ingestion step (here, hand-authored data) to extract
  cross-references from prose. That extraction is the real-world cost, but it is a
  one-time, improvable pipeline, and everything downstream benefits from the
  structure.
