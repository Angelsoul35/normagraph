# ADR 0004: Integrity checks as graph queries

## Status

Accepted.

## Context

Regulatory corpora drift into inconsistency over time: a reference survives to a
norm that was repealed or renumbered away, an in-force article still points at a
repealed one, an amendment loop is introduced by mistake, a norm ends up
connected to nothing. These defects are hard to spot by reading, because each one
lives in the relationship between two norms, not in a single text.

## Decision

Express each consistency rule as a **query over the graph**, and collect the
results as typed findings:

- **dangling_reference** — an edge whose target norm is not in the corpus;
- **depends_on_repealed** — an in-force norm with a dependency edge to a repealed
  norm;
- **repealed_still_in_force** — a norm that a `repeals` edge points at but whose
  status is still in force;
- **amendment_cycle** — a cycle in the `amends` subgraph (found with NetworkX);
- **orphan** — a norm with degree zero.

Each finding carries a kind, the norm it concerns, and a human-readable detail.

## Consequences

- **Defects become visible and specific.** A maintainer gets a concrete list to
  fix, each pointing at a norm and explaining the problem.
- **Cheap and exhaustive.** Each check is a single pass over nodes or edges; they
  run over the whole corpus in one call.
- **Composable.** New rules are new passes that append findings; they do not
  interact.
- **Trade-off.** The checks are structural: they catch inconsistencies in the
  recorded graph, not errors of legal substance (a reference that exists but is to
  the wrong norm). Structural integrity is a necessary foundation, and keeping the
  checks purely structural keeps them objective and false-positive-free.
