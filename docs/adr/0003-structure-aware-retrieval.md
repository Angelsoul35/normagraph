# ADR 0003: Retrieval that expands along the graph

## Status

Accepted.

## Context

To answer a question about the regulations, we first have to find the relevant
norms. Plain text retrieval (TF-IDF) finds norms whose words match the query. But
in a regulatory corpus, the norm that matches is often not enough on its own: an
article about consent is meaningless without the definitions it relies on, and an
article may have been amended by another that shares little vocabulary with the
query.

## Decision

Retrieve in two stages:

1. **Text match.** TF-IDF + cosine similarity over each norm's title and text
   returns the top-k matches.
2. **Graph expansion.** For each match, add its graph neighbours (bounded by a hop
   count) — the norms it references, the ones that reference it, and so on.

Each returned norm is tagged with how it arrived (`match` or `graph`).

## Consequences

- **More complete context.** The answer includes the norms around a match, which
  are frequently what the reader needs (definitions, amendments, implementing
  rules).
- **Explainable.** The text scores explain the matches; the `via` tag explains why
  each neighbour is present.
- **Better grounding for QA.** The LLM answers over a connected neighbourhood of
  norms, not an isolated article, so its answers reflect how the rules actually
  interlock.
- **Trade-off.** Expansion adds norms with a zero text score, which could dilute
  relevance if the hop count were large. Keeping expansion shallow (one hop by
  default) adds the directly-connected context without flooding the result, and
  the hop count is configurable.
