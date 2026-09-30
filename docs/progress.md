# Sift Progress

## Current Status

**Active phase:** Phase 2 complete — Identity, Authorization, and Data Foundation.

## Completed

- Created the public `Hardik180704/sift` GitHub repository.
- Defined the product: document intelligence with grounded answers, citations,
  and user-confirmed action items.
- Approved managed-service direction: Supabase, Qdrant Cloud, Inngest Cloud.
- Approved frontend direction: Next.js 16 premium/minimal experience.
- Defined the eight-phase delivery roadmap.
- Created durable architecture, decision, and agent-context documentation.
- Created the monorepo layout with `apps/web`, `apps/api`, and
  `packages/contracts`.
- Scaffolded a strict TypeScript Next.js 16 web application with a tested
  `GET /api/health` endpoint.
- Scaffolded a typed FastAPI service with a tested `GET /health` endpoint and
  fail-fast managed-service configuration validation.
- Added safe environment templates, npm and uv lockfiles, GitHub Actions CI,
  and Vercel/Render deployment declarations.
- Validated web formatting, linting, type checking, tests, and production
  build; validated API formatting, linting, strict mypy, and tests.
- Prepared the Phase 2 Supabase migration with core data tables, profile
  creation trigger, RLS, private document storage policies, and indexes. It is
  awaiting manual application to the development project.
- Added Supabase cookie-auth scaffolding and protected browser routes, plus
  FastAPI JWKS JWT verification that derives identity only from the token
  subject.
- Verified configured development environments without exposing credentials;
  web/API health checks succeed, protected web routes redirect unauthenticated
  users, and protected API routes reject requests without bearer tokens.

## Current Constraints

- Do not use Docker-managed PostgreSQL or other self-hosted data services.
- Supabase MCP must target the development project only.
- No production Supabase project should be created or connected through MCP.
- No source documents, API keys, or Supabase credentials may enter Git.
- Supabase schema changes begin in Phase 2 and must be applied as reviewed
  migrations. Because Supabase MCP is unavailable, provide paste-ready SQL for
  the development project's SQL Editor before recording migration files.

## Next Execution Target

Start **Phase 3 — Reliable Document Ingestion**.

Expected first deliverables:

1. Implement direct signed uploads to the private `documents` bucket.
2. Add Inngest ingestion events and retry-safe document lifecycle processing.
3. Parse PDF, DOCX, and text documents; add OCR fallback and safe failures.
4. Create structure-aware chunks and idempotently index user/document-scoped
   embeddings in Qdrant Cloud.

## Handoff Prompt for a New Kilo Session

```text
We are building Sift, a production-quality major project.

Read AGENTS.md, docs/progress.md, docs/roadmap.md,
docs/architecture.md, and every file in docs/decisions before making changes.

Phase 2 is complete. Start Phase 3 only when ready to implement reliable,
retry-safe document ingestion. Do not skip phases or add unapproved
infrastructure. Use Supabase, Qdrant Cloud, and Inngest Cloud; do not use a
Docker-managed database. Supabase MCP is unavailable, so prepare reviewed,
paste-ready SQL for manual execution only against the development project.
```
