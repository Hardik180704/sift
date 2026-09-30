# ADR 0003: Hybrid Retrieval With Citation-Gated Answers

## Status

Accepted.

## Context

Pure vector similarity often misses exact policy numbers, dates, legal terms,
and clause language. A document assistant must show users where its answer
came from and should avoid unsupported inferences.

## Decision

- Use Qdrant Cloud for semantic vector search.
- Use Supabase Postgres Full Text Search for keyword retrieval.
- Fuse ranked results with Reciprocal Rank Fusion and optionally rerank the
  highest candidates.
- Store page, section, chunk, and document metadata for every source.
- Require typed citations from grounded answer generation.
- Run a LangGraph reflection node that verifies citation support and may retry
  retrieval once.
- Return an insufficient-evidence response instead of unsupported claims.

## Consequences

- Retrieval has more moving parts than a simple vector search but provides
  better coverage of both semantic questions and exact text queries.
- Citation records become first-class persisted data rather than markdown-only
  decorations.
- Evaluation can measure retrieval quality and faithfulness independently.

## Rejected Alternatives

- Plain vector search only: weak for exact clauses, values, and dates.
- Answers without source citations: unacceptable for personal paperwork.
- Unlimited self-reflection loops: costly and unpredictable; one retry is the
  bounded default.
