-- Idempotency hardening for mobile outbox sync.
-- Adds a stable client_uuid key for upsert(on conflict) from app clients.

create extension if not exists pgcrypto;

alter table public.relevamientos
  add column if not exists client_uuid uuid;

do $$
begin
  if exists (
    select 1
    from information_schema.columns
    where table_schema = 'public'
      and table_name = 'relevamientos'
      and column_name = 'client_uid'
  ) then
    execute $sql$
      update public.relevamientos
      set client_uuid = case
        when client_uuid is not null then client_uuid
        when client_uid is null or btrim(client_uid) = '' then gen_random_uuid()
        when client_uid ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$' then client_uid::uuid
        else gen_random_uuid()
      end
      where client_uuid is null
    $sql$;
  else
    update public.relevamientos
    set client_uuid = coalesce(client_uuid, gen_random_uuid())
    where client_uuid is null;
  end if;
end $$;

alter table public.relevamientos
  alter column client_uuid set default gen_random_uuid();

create unique index if not exists uq_relevamientos_client_uuid
  on public.relevamientos (client_uuid);

alter table public.relevamientos
  alter column client_uuid set not null;
