# ADR 0002: Define impact as reverse reachability over dependency edges

## Status

Accepted.

## Context

The most valuable question a regulatory graph can answer is: *if we change (or
repeal) this norm, what else is affected?* We needed a precise, defensible
definition of "affected" rather than a vague notion of "related".

Not every edge carries a dependency. If A *references* B, then A relies on B — A
is affected when B changes. The same holds for *implements*. But *amends* and
*repeals* describe what a norm does to another, not a standing dependency on it.

## Decision

Define **impact** as everything reachable by walking **dependency edges**
(`references`, `implements`) **backwards** from the target norm. Concretely: start
at the norm, follow incoming reference/implement edges to the norms that depend on
it, then repeat from each of those, transitively. A hop limit is available to
bound the blast radius to direct or near dependents.

## Consequences

- **A precise definition.** "Affected" means "transitively depends on, via
  references or implementations" — easy to explain and to audit.
- **Correct edge semantics.** Only edges that represent a real dependency count;
  amendment and repeal edges drive other queries, not impact.
- **Bounded when needed.** The hop limit answers "direct dependents only" versus
  "the whole blast radius".
- **Trade-off.** Impact is as complete as the recorded references. A dependency
  that exists in the text but was never captured as an edge will not appear — so
  the quality of impact analysis rests on the quality of the extracted graph,
  which is exactly where effort should go.
