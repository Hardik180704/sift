-- Phase 2: Identity, authorization, and data foundation.
-- Apply this migration only to the sift-dev Supabase project.

create extension if not exists pgcrypto;

create type public.document_state as enum (
  'UPLOADED', 'QUEUED', 'PARSING', 'EXTRACTING', 'EMBEDDING', 'READY', 'FAILED'
);
create type public.job_state as enum ('QUEUED', 'RUNNING', 'SUCCEEDED', 'FAILED');
create type public.message_role as enum ('USER', 'ASSISTANT', 'SYSTEM');
create type public.action_item_state as enum ('SUGGESTED', 'CONFIRMED', 'DISMISSED');

create table public.profiles (
  user_id uuid primary key references auth.users(id) on delete cascade,
  display_name text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.documents (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  original_filename text not null check (char_length(original_filename) between 1 and 512),
  mime_type text not null check (char_length(mime_type) between 1 and 255),
  size_bytes bigint not null check (size_bytes > 0),
  storage_key text not null unique check (storage_key like user_id::text || '/%'),
  state public.document_state not null default 'UPLOADED',
  document_type text,
  checksum_sha256 text check (checksum_sha256 is null or checksum_sha256 ~ '^[a-f0-9]{64}$'),
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (id, user_id)
);

create table public.document_versions (
  id uuid primary key default gen_random_uuid(),
  document_id uuid not null,
  user_id uuid not null,
  version_number integer not null check (version_number > 0),
  storage_key text not null unique check (storage_key like user_id::text || '/%'),
  checksum_sha256 text check (checksum_sha256 is null or checksum_sha256 ~ '^[a-f0-9]{64}$'),
  created_at timestamptz not null default now(),
  foreign key (document_id, user_id) references public.documents (id, user_id) on delete cascade,
  unique (document_id, version_number),
  unique (id, user_id)
);

create table public.document_jobs (
  id uuid primary key default gen_random_uuid(),
  document_id uuid not null,
  document_version_id uuid,
  user_id uuid not null,
  state public.job_state not null default 'QUEUED',
  attempt integer not null default 1 check (attempt > 0),
  error_code text,
  error_message text,
  started_at timestamptz,
  completed_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  foreign key (document_id, user_id) references public.documents (id, user_id) on delete cascade,
  foreign key (document_version_id, user_id) references public.document_versions (id, user_id) on delete set null (document_version_id),
  check (completed_at is null or started_at is not null),
  check (completed_at is null or completed_at >= started_at)
);

create table public.chunks (
  id uuid primary key default gen_random_uuid(),
  document_id uuid not null,
  document_version_id uuid,
  user_id uuid not null,
  chunk_index integer not null check (chunk_index >= 0),
  page_number integer check (page_number is null or page_number > 0),
  section text,
  content text not null check (char_length(content) > 0),
  metadata jsonb not null default '{}'::jsonb,
  search_vector tsvector generated always as (to_tsvector('english', content)) stored,
  created_at timestamptz not null default now(),
  foreign key (document_id, user_id) references public.documents (id, user_id) on delete cascade,
  foreign key (document_version_id, user_id) references public.document_versions (id, user_id) on delete cascade,
  unique (document_version_id, chunk_index),
  unique (id, user_id)
);

create table public.conversations (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  title text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (id, user_id)
);

create table public.messages (
  id uuid primary key default gen_random_uuid(),
  conversation_id uuid not null,
  user_id uuid not null,
  role public.message_role not null,
  content text not null,
  created_at timestamptz not null default now(),
  foreign key (conversation_id, user_id) references public.conversations (id, user_id) on delete cascade,
  unique (id, user_id)
);

create table public.message_citations (
  id uuid primary key default gen_random_uuid(),
  message_id uuid not null,
  chunk_id uuid not null,
  user_id uuid not null,
  citation_order integer not null check (citation_order >= 0),
  quote text,
  created_at timestamptz not null default now(),
  foreign key (message_id, user_id) references public.messages (id, user_id) on delete cascade,
  foreign key (chunk_id, user_id) references public.chunks (id, user_id) on delete cascade,
  unique (message_id, citation_order)
);

create table public.document_extractions (
  id uuid primary key default gen_random_uuid(),
  document_id uuid not null,
  chunk_id uuid,
  user_id uuid not null,
  extraction_type text not null,
  value jsonb not null,
  confidence numeric(4, 3) check (confidence is null or confidence between 0 and 1),
  created_at timestamptz not null default now(),
  foreign key (document_id, user_id) references public.documents (id, user_id) on delete cascade,
  foreign key (chunk_id, user_id) references public.chunks (id, user_id) on delete set null (chunk_id)
);

create table public.action_items (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  document_id uuid,
  chunk_id uuid,
  title text not null,
  details text,
  due_at timestamptz,
  state public.action_item_state not null default 'SUGGESTED',
  confirmed_at timestamptz,
  dismissed_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  foreign key (document_id, user_id) references public.documents (id, user_id) on delete set null (document_id),
  foreign key (chunk_id, user_id) references public.chunks (id, user_id) on delete set null (chunk_id),
  check (confirmed_at is null or state = 'CONFIRMED'),
  check (dismissed_at is null or state = 'DISMISSED')
);

create table public.audit_events (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete set null,
  event_type text not null,
  entity_type text,
  entity_id uuid,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table public.evaluation_runs (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  metrics jsonb not null,
  created_at timestamptz not null default now()
);

create index documents_user_created_at_idx on public.documents (user_id, created_at desc);
create index document_versions_document_idx on public.document_versions (document_id, version_number desc);
create index document_jobs_document_created_at_idx on public.document_jobs (document_id, created_at desc);
create index chunks_user_document_idx on public.chunks (user_id, document_id);
create index chunks_search_vector_idx on public.chunks using gin (search_vector);
create index conversations_user_updated_at_idx on public.conversations (user_id, updated_at desc);
create index messages_conversation_created_at_idx on public.messages (conversation_id, created_at);
create index message_citations_message_idx on public.message_citations (message_id, citation_order);
create index document_extractions_document_idx on public.document_extractions (document_id);
create index action_items_user_state_due_at_idx on public.action_items (user_id, state, due_at);
create index audit_events_user_created_at_idx on public.audit_events (user_id, created_at desc);

create function public.set_updated_at()
returns trigger
language plpgsql
set search_path = public
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create trigger profiles_set_updated_at before update on public.profiles
for each row execute function public.set_updated_at();
create trigger documents_set_updated_at before update on public.documents
for each row execute function public.set_updated_at();
create trigger document_jobs_set_updated_at before update on public.document_jobs
for each row execute function public.set_updated_at();
create trigger conversations_set_updated_at before update on public.conversations
for each row execute function public.set_updated_at();
create trigger action_items_set_updated_at before update on public.action_items
for each row execute function public.set_updated_at();

create function public.create_profile_for_new_user()
returns trigger
language plpgsql
security definer set search_path = public
as $$
begin
  insert into public.profiles (user_id, display_name)
  values (new.id, nullif(trim(new.raw_user_meta_data ->> 'display_name'), ''));
  return new;
end;
$$;

create trigger auth_user_created_profile
after insert on auth.users
for each row execute procedure public.create_profile_for_new_user();

insert into public.profiles (user_id, display_name)
select id, nullif(trim(raw_user_meta_data ->> 'display_name'), '')
from auth.users
on conflict (user_id) do nothing;

alter table public.profiles enable row level security;
alter table public.documents enable row level security;
alter table public.document_versions enable row level security;
alter table public.document_jobs enable row level security;
alter table public.chunks enable row level security;
alter table public.conversations enable row level security;
alter table public.messages enable row level security;
alter table public.message_citations enable row level security;
alter table public.document_extractions enable row level security;
alter table public.action_items enable row level security;
alter table public.audit_events enable row level security;
alter table public.evaluation_runs enable row level security;

create policy "profiles: users read their profile" on public.profiles
for select to authenticated using (user_id = auth.uid());
create policy "profiles: users update their profile" on public.profiles
for update to authenticated using (user_id = auth.uid()) with check (user_id = auth.uid());
create policy "documents: users manage their documents" on public.documents
for all to authenticated using (user_id = auth.uid()) with check (user_id = auth.uid());
create policy "document_versions: users manage their versions" on public.document_versions
for all to authenticated using (user_id = auth.uid()) with check (user_id = auth.uid());
create policy "document_jobs: users read their jobs" on public.document_jobs
for select to authenticated using (user_id = auth.uid());
create policy "chunks: users read their chunks" on public.chunks
for select to authenticated using (user_id = auth.uid());
create policy "conversations: users manage their conversations" on public.conversations
for all to authenticated using (user_id = auth.uid()) with check (user_id = auth.uid());
create policy "messages: users read their messages" on public.messages
for select to authenticated using (user_id = auth.uid());
create policy "message_citations: users read their citations" on public.message_citations
for select to authenticated using (user_id = auth.uid());
create policy "document_extractions: users read their extractions" on public.document_extractions
for select to authenticated using (user_id = auth.uid());
create policy "action_items: users manage their action items" on public.action_items
for all to authenticated using (user_id = auth.uid()) with check (user_id = auth.uid());
create policy "audit_events: users read their events" on public.audit_events
for select to authenticated using (user_id = auth.uid());

insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values (
  'documents',
  'documents',
  false,
  52428800,
  array['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain']
)
on conflict (id) do update set
  public = excluded.public,
  file_size_limit = excluded.file_size_limit,
  allowed_mime_types = excluded.allowed_mime_types;

create policy "documents bucket: users read their objects" on storage.objects
for select to authenticated using (
  bucket_id = 'documents' and (storage.foldername(name))[1] = auth.uid()::text
);
create policy "documents bucket: users upload to their path" on storage.objects
for insert to authenticated with check (
  bucket_id = 'documents' and (storage.foldername(name))[1] = auth.uid()::text
);
create policy "documents bucket: users update their objects" on storage.objects
for update to authenticated using (
  bucket_id = 'documents' and (storage.foldername(name))[1] = auth.uid()::text
) with check (
  bucket_id = 'documents' and (storage.foldername(name))[1] = auth.uid()::text
);
create policy "documents bucket: users delete their objects" on storage.objects
for delete to authenticated using (
  bucket_id = 'documents' and (storage.foldername(name))[1] = auth.uid()::text
);
