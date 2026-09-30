# ADR 0004: Use OpenAI Embeddings for Initial Indexing

## Status

Accepted.

## Decision

Use OpenAI `text-embedding-3-small` with 1,536 dimensions for Phase 3
document chunk embeddings. Configure the model, dimension, and API key through
the API environment; do not expose them to the browser.

## Consequences

- Qdrant collections use a 1,536-dimensional cosine vector configuration.
- Ingestion depends on OpenAI availability and reports a retryable workflow
  failure when embeddings cannot be generated.
- Future provider changes remain configuration and adapter changes, with a
  collection migration for a different vector dimension.
