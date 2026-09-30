# Sift Delivery Roadmap

## Delivery Principle

Sift is delivered in eight meaningful engineering phases. Do not skip phase
completion gates and do not expand scope before the active phase is stable.

## Phase 1 — Foundation and Cloud Boundaries

Set up the Next.js 16 and FastAPI applications, dependency management,
formatters, type checking, CI, configuration validation, health endpoints, and
development cloud-service configuration. Establish deployment shells for
Vercel and Render/Railway.

**Gate:** clean repository, validated environment configuration, CI baseline,
and independently deployable web/API health checks.

## Phase 2 — Identity, Authorization, and Data Foundation

Integrate Supabase Auth and JWT validation, build protected frontend routes,
create Supabase migrations, implement RLS policies, private storage paths, and
the core document/conversation schema.

**Gate:** cross-user access fails at API, database, storage, and vector-query
boundaries.

## Phase 3 — Reliable Document Ingestion

Implement direct signed upload, Inngest workflows, PDF/DOCX/text parsing, OCR
fallback, structure-aware chunking, typed metadata extraction, embeddings, and
idempotent Qdrant indexing.

**Gate:** documents reach READY asynchronously with page-level chunks and
safe retry behavior.

## Phase 4 — Hybrid Retrieval and Source Evidence

Implement Qdrant semantic search, Supabase FTS, reciprocal-rank fusion,
optional reranking, metadata filtering, page-level citations, and retrieval
quality evaluation.

**Gate:** a user can search only their own documents and inspect all returned
source evidence.

## Phase 5 — LangGraph Grounded Assistant

Implement graph state, intent routing, query rewriting, retrieval, grounded
structured responses, citation reflection, checkpointing, SSE streaming, and
prompt-injection defenses.

**Gate:** factual answers are cited; unsupported claims are rejected or marked
low-confidence; graph runs are traceable.

## Phase 6 — Premium Product Experience

Build the Next.js application shell, responsive document library, streaming
chat, citation chips, PDF source panel, highlighted evidence, keyboard
navigation, dark/light theme, and accessible loading/error states.

**Gate:** upload-to-cited-answer is smooth, mobile-safe, and visually polished.

## Phase 7 — Action Items, Guardrails, and Operations

Build extracted deadline/action-item suggestions with confirmation workflow,
audit events, quotas, rate limits, input validation, cost controls, error
monitoring, and resilience for external-service outages.

**Gate:** no user-visible action becomes active without confirmation; security
and operational controls are tested.

## Phase 8 — Evaluation, Deployment, and Final Audit

Create a curated evaluation set, run RAGAS and regression tests, add Playwright
end-to-end coverage, deploy production environments, write complete docs,
perform threat-model review, and publish a portfolio-ready release.

**Gate:** CI is green, quality metrics are documented, production deployment
works, and no secrets or real private documents are present in the repository.
