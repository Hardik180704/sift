# Sift

Sift is a document intelligence application for the paperwork people avoid
reading: leases, insurance policies, warranties, invoices, contracts, and
similar records. It will let users securely upload documents, ask grounded
questions, inspect page-level citations, and review suggested deadlines or
action items.

> **Project status:** Phase 1 foundation is complete. The eight-phase plan is
> documented in `docs/roadmap.md`.

## Product Principles

- Answers are grounded in uploaded documents, not generic model confidence.
- Every document-based factual answer carries inspectable citations.
- Documents, conversations, retrieval, and storage are isolated per user.
- Suggested deadlines require user confirmation.
- Managed cloud services reduce operational complexity without compromising
  engineering rigor.

## Target Stack

- Next.js 16 / React 19 / TypeScript
- FastAPI / Python / LangGraph
- Supabase Auth, Postgres, and private Storage
- Qdrant Cloud for vectors
- Inngest Cloud for background ingestion workflows
- Vercel and Render/Railway deployments

## Repository Context

Read these before implementation:

- `AGENTS.md` — persistent engineering and security rules
- `docs/architecture.md` — system design and data flows
- `docs/roadmap.md` — phased delivery plan and completion gates
- `docs/progress.md` — current project state
- `docs/decisions/` — architectural decision records

## Local Development

Prerequisites: Node.js 22+, npm 10+, Python 3.12+, and uv.

```bash
npm install
cp apps/web/.env.example apps/web/.env.local
npm run dev:web
```

```bash
cd apps/api
uv sync --group dev
cp .env.example .env
uv run uvicorn sift_api.main:app --reload
```

Run the Inngest Dev Server in a separate terminal after the API is available:

```bash
npm run dev:inngest
```

Local ingestion requires `SIFT_INNGEST_API_BASE_URL=http://127.0.0.1:8288`
in `apps/api/.env`. The script pins the CLI version, persists its local state,
and registers the FastAPI workflow endpoint. Do not point Inngest Cloud at a
localhost URL.

The web health endpoint is `http://localhost:3000/api/health`. The API health
endpoint is `http://localhost:8000/health`. Environment templates contain only
placeholders; do not commit populated environment files.

For browser authentication, configure the development Supabase project URL and
publishable key in `apps/web/.env.local`. Configure the same project URL and
the `authenticated` JWT audience in `apps/api/.env`. The API validates bearer
tokens against Supabase JWKS and derives the user ID only from the verified
token subject.

## Quality Checks

```bash
npm run format:check
npm run check
npm run test
npm run build
```

```bash
cd apps/api
uv run ruff check .
uv run ruff format --check .
uv run mypy src tests
uv run pytest
```

## License

To be selected before the first public release.
