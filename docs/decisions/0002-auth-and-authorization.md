# ADR 0002: Supabase Auth With Backend-Enforced Ownership

## Status

Accepted.

## Context

Sift stores highly personal documents. Browser-only route checks or client
supplied user IDs are not sufficient authorization controls.

## Decision

- Use Supabase Auth for password-based identity and session management.
- Use secure, httpOnly Supabase session cookies in the Next.js application.
- Use Next.js `proxy.ts` only as a browser route guard.
- Have FastAPI verify Supabase JWTs using the issuer's JWKS.
- Derive `user_id` exclusively from the verified JWT subject.
- Apply Supabase RLS for user-owned data and private storage policies.
- Require `user_id` filtering in every Qdrant query and workflow operation.

## Consequences

- A compromised frontend cannot choose another user's identity in an API call.
- Authorization is enforced at multiple layers: API, database, storage, and
  vector retrieval.
- Background jobs use privileged credentials only after loading a specific,
  scoped job/document record; they must not run broad user queries.

## Rejected Alternatives

- Custom JWT/password implementation: duplicates mature Supabase security
  features without adding project value.
- Relying on frontend-only authorization: insufficient for private documents.
