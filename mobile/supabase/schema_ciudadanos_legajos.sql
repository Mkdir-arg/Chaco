-- Esquema minimo para mobile (crear/editar ciudadano + legajo)
-- Ejecutar en SQL Editor de Supabase.

create extension if not exists pgcrypto;

create table if not exists public.ciudadanos (
  id uuid primary key default gen_random_uuid(),
  nombre text not null,
  apellido text not null,
  dni text not null unique,
  telefono text,
  domicilio text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.legajos (
  id uuid primary key default gen_random_uuid(),
  ciudadano_id uuid not null references public.ciudadanos(id) on delete cascade,
  via_ingreso text not null default 'ESPONTANEA',
  nivel_riesgo text not null default 'BAJO',
  estado text not null default 'EN_SEGUIMIENTO',
  notas text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists idx_legajos_ciudadano on public.legajos(ciudadano_id);
create index if not exists idx_legajos_riesgo on public.legajos(nivel_riesgo);

create or replace function public.set_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

drop trigger if exists ciudadanos_set_updated_at on public.ciudadanos;
create trigger ciudadanos_set_updated_at
before update on public.ciudadanos
for each row execute function public.set_updated_at();

drop trigger if exists legajos_set_updated_at on public.legajos;
create trigger legajos_set_updated_at
before update on public.legajos
for each row execute function public.set_updated_at();

-- RLS
alter table public.ciudadanos enable row level security;
alter table public.legajos enable row level security;

-- Politicas temporales para desarrollo con anon key.
-- Ajustar antes de produccion.
drop policy if exists ciudadanos_all_dev on public.ciudadanos;
create policy ciudadanos_all_dev on public.ciudadanos
for all
to anon, authenticated
using (true)
with check (true);

drop policy if exists legajos_all_dev on public.legajos;
create policy legajos_all_dev on public.legajos
for all
to anon, authenticated
using (true)
with check (true);
