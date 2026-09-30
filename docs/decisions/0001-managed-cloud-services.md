# ADR 0001: Use Managed Cloud Data Services

## Status

Accepted.

## Context

Sift needs relational data, private document storage, authentication, vector
search, and reliable background workflows. Operating PostgreSQL, object
storage, Redis, a vector database, and workers locally through Docker would
create unnecessary deployment complexity for a portfolio project.

## Decision

- Use Supabase for Auth, managed Postgres, private Storage, migrations, and
  row-level security.
- Use Qdrant Cloud for semantic vector retrieval.
- Use Inngest Cloud for durable document ingestion workflows.
- Use managed application deployments rather than self-hosting infrastructure.

## Consequences

Benefits:

- Development and production use the same managed-service architecture.
- No local Docker database is required.
- Storage and relational data have mature access-control primitives.
- Qdrant provides dedicated vector indexes and metadata filtering.

Trade-offs:

- The project depends on external service availability and quotas.
- Environment configuration and service credentials require careful handling.
- Integration tests need isolated development resources or controlled test
  fixtures rather than disposable local containers.

## Rejected Alternatives

- Docker Compose PostgreSQL + pgvector + MinIO + Redis: operationally useful,
  but unnecessarily complex for the intended deployment path.
- A single managed Postgres vector extension: viable, but Qdrant is selected to
  demonstrate dedicated vector infrastructure and payload filtering.
