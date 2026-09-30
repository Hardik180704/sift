# Sift Architecture

## Status

This document defines the approved target architecture. It is not evidence
that a component is already implemented. Consult `docs/progress.md` for the
current delivery state.

## System Overview

```mermaid
flowchart LR
    U[User] --> W[Next.js 16 Web Application]
    W -->|Supabase session cookie| P[Next.js proxy.ts]
    P -->|authenticated API requests| A[FastAPI API]
    A --> G[LangGraph RAG Workflow]
    A --> S[(Supabase Auth / Postgres / Storage)]
    A --> I[Inngest Cloud]
    I --> J[Document Ingestion Function]
    J --> S
    J --> Q[(Qdrant Cloud)]
    G --> S
    G --> Q
    G --> L[LLM / Embedding Provider]
    G --> O[LangSmith or Langfuse]
```

## Component Responsibilities

| Component | Responsibility |
| --- | --- |
| Next.js web application | Authentication UI, document library, upload UX, streaming chat, citation/source viewer, action-item review UI. |
| Next.js `proxy.ts` | Redirects unauthenticated browser users away from protected routes. This is a UX guard, not the sole authorization boundary. |
| FastAPI | Validates Supabase JWTs, owns API contracts, creates signed storage URLs, enforces authorization, starts workflows, and streams graph output. |
| Supabase Auth | Managed email/password identity and session lifecycle. |
| Supabase Postgres | Source of truth for metadata, conversations, citations, action items, ingestion jobs, audit events, and LangGraph checkpoint state. |
| Supabase Storage | Private storage for original uploaded files. Database rows store object keys, not file blobs. |
| Inngest Cloud | Durable, retry-safe document parsing, extraction, chunking, and embedding workflows. |
| Qdrant Cloud | Semantic vector search with mandatory `user_id` payload filtering. |
| LangGraph | Explicit agent state graph for routing, retrieval, grounded generation, reflection, and persistence. |
| LLM provider | Structured extraction, query rewriting, grounded answer generation, and embeddings. Provider/model names remain configuration values. |

## Security Boundary

```mermaid
flowchart TD
    R[Browser request] --> N{Next.js proxy.ts\nvalid Supabase session?}
    N -- No --> L[Redirect to login]
    N -- Yes --> F[FastAPI endpoint]
    F --> V[Verify JWT via Supabase JWKS]
    V --> X{Token valid?}
    X -- No --> U[401 response]
    X -- Yes --> C[Derive user_id from JWT subject]
    C --> D[Scope database / storage / Qdrant request by user_id]
```

The backend never accepts a user identity from request JSON, query parameters,
and data filtering enforce security.

## Document Ingestion Workflow

```mermaid
sequenceDiagram
    participant User
    participant Web as Next.js
    participant API as FastAPI
    participant Storage as Supabase Storage
    participant DB as Supabase Postgres
    participant Jobs as Inngest
    participant Vector as Qdrant Cloud

    User->>Web: Choose document
    Web->>API: Request signed upload URL
    API->>DB: Create document (UPLOADED)
    API-->>Web: Signed upload URL + document ID
    Web->>Storage: Upload file directly
    Web->>API: Confirm upload
    API->>Jobs: Emit document.ingest event
    Jobs->>Storage: Download private object
    Jobs->>Jobs: Parse, OCR fallback, extract, chunk
    Jobs->>DB: Store document metadata and chunks
    Jobs->>Vector: Upsert embeddings + user/document payload
    Jobs->>DB: Mark document READY or FAILED
```

Document lifecycle:

```text
UPLOADED → QUEUED → PARSING → EXTRACTING → EMBEDDING → READY
                                                      └→ FAILED
```

The workflow is idempotent by document version/checksum. Retrying an ingestion
job must not create duplicate chunks or Qdrant points.

## Query and Answer Workflow

```mermaid
flowchart TD
    A[User question] --> B[Load conversation + validate user]
    B --> C{Intent router}
    C -->|Document question| D[Generate retrieval queries]
    C -->|Action items| E[Retrieve action-item and source data]
    C -->|Non-document chat| F[Safe direct response]
    D --> G[Hybrid retrieval]
    G --> H[Qdrant semantic search\nuser_id filter required]
    G --> I[Supabase FTS keyword search\nuser_id filter required]
    H --> J[RRF fusion + rerank]
    I --> J
    J --> K[Grounded answer + typed citations]
    E --> K
    K --> L[Citation reflection]
    L -->|Unsupported claim, max once| D
    L -->|Verified| M[Persist message, citations, checkpoint]
    F --> M
    M --> N[Stream response to client]
```

All document-derived claims must map to a stored chunk. If retrieval does not
provide enough evidence, the answer explicitly says so.

## Data Model

| Table | Purpose | Key access constraint |
| --- | --- | --- |
| `profiles` | Application metadata for Supabase Auth users | User reads/updates only their row. |
| `documents` | File metadata, state, checksum, storage key | `user_id` ownership. |
| `document_versions` | Re-ingestion/history for a document | Parent document ownership. |
| `document_jobs` | Ingestion attempts and failures | Parent document ownership. |
| `chunks` | Page/section text and retrieval metadata | `user_id` ownership; linked to document. |
| `conversations` | User chat sessions | `user_id` ownership. |
| `messages` | User/assistant messages | Inherits conversation ownership. |
| `message_citations` | Message-to-source evidence mapping | Inherits message ownership. |
| `document_extractions` | Typed dates, parties, amounts, renewal terms | Parent document ownership. |
| `action_items` | Suggested/confirmed user actions | `user_id` ownership and source citation. |
| `audit_events` | Security and product activity trail | Server-written, user-readable only where appropriate. |
| `evaluation_runs` | Offline quality metrics | Internal/admin-only. |

Qdrant points contain the vector and only minimal retrieval payload:
`user_id`, `document_id`, `chunk_id`, `page`, `section`, and document type.
The authoritative full chunk text and citation metadata remain in Supabase.

## Managed Environments

| Environment | Supabase | Qdrant | Inngest | Deployment |
| --- | --- | --- | --- | --- |
| Development | Dedicated `sift-dev` project | Dev collection | Dev app | Local Next/FastAPI or preview deployments |
| Production | Separate `sift-prod` project | Production collection | Production app | Vercel + Render/Railway |

Supabase MCP is allowed only for the development project. Production schema
changes run through reviewed migrations in the deployment workflow.
