-- Admin-driven paid-access management with NO service-role key in the application.
--
-- Previously every grant/revoke went through a service-role client that bypasses RLS.
-- That key is a root password and must not live on the frontend host. Instead, the admin
-- identity is an owner-managed row in `admin_users`, and all reads/writes go through
-- SECURITY DEFINER functions that (a) re-check the caller is an admin as their first
-- statement — defence in depth, never relying on GRANT alone — and (b) pin search_path so
-- an attacker cannot shadow `auth`/`public` objects. The functions are owned by the role
-- that applies this migration (the project owner), so they bypass RLS on `paid_access` for
-- their one narrow operation while callers hold only the anon/authenticated grant.

-- Static allow-list of admins. Not a live secret path: RLS with no policies denies all
-- access to anon/authenticated, so the only way to add/remove an admin is the owner running
-- SQL in the dashboard (service role / superuser bypasses RLS). Seeded once by email — see
-- docs/manual-activation-sop.md.
create table admin_users (
  user_id uuid primary key references auth.users (id) on delete cascade,
  email text not null,                            -- for human readability in the dashboard
  added_at timestamptz not null default now(),
  note text
);

alter table admin_users enable row level security;
-- No policy exists, so RLS denies select/insert/update/delete to anon and authenticated
-- regardless of table grants. Revoke grants too, so even the check is unambiguous.
revoke all on public.admin_users from anon, authenticated;

-- Is the CURRENT calling user an admin? SECURITY DEFINER so it can read admin_users (which
-- is RLS-locked to callers) while running as the owner. Every admin function calls this as
-- its first statement rather than trusting the EXECUTE grant alone.
create or replace function public.is_current_user_admin()
returns boolean
language sql
security definer
set search_path = public, pg_temp
stable
as $$
  select exists (
    select 1 from public.admin_users where user_id = auth.uid()
  );
$$;

-- Look up a learner by exact (case-insensitive) email plus their current access row.
-- Returns 0 rows when no user matches (caller reads that as "not found"); 1 row otherwise,
-- with the paid_access columns left null and access_exists false when no grant was ever
-- written. Gated on admin identity so this can never become a directory of every account.
create or replace function public.admin_search_learner(p_email text)
returns table (
  user_id uuid,
  email text,
  granted_at timestamptz,
  amount_vnd integer,
  transfer_ref text,
  note text,
  revoked_at timestamptz,
  access_exists boolean
)
language plpgsql
security definer
set search_path = public, pg_temp
as $$
begin
  if not public.is_current_user_admin() then
    raise exception 'not authorized' using errcode = '42501';
  end if;

  if p_email is null or length(trim(p_email)) = 0 then
    raise exception 'email must not be null or empty';
  end if;

  return query
  select
    u.id,
    u.email::text,
    pa.granted_at,
    pa.amount_vnd,
    pa.transfer_ref,
    pa.note,
    pa.revoked_at,
    (pa.user_id is not null) as access_exists
  from auth.users u
  left join public.paid_access pa on pa.user_id = u.id
  where lower(u.email) = lower(trim(p_email))
  limit 1;
end;
$$;

-- Grant (or re-grant) paid access. Upserts on the user_id primary key, so re-activating a
-- previously revoked learner UPDATES their existing row — clearing revoked_at and refreshing
-- granted_at — rather than inserting a duplicate the primary key would reject. Returns the
-- resulting row.
create or replace function public.admin_activate_paid_access(
  p_user_id uuid,
  p_amount_vnd integer,
  p_transfer_ref text,
  p_note text
)
returns public.paid_access
language plpgsql
security definer
set search_path = public, pg_temp
as $$
declare
  v_row public.paid_access;
begin
  if not public.is_current_user_admin() then
    raise exception 'not authorized' using errcode = '42501';
  end if;

  if p_user_id is null then
    raise exception 'user_id must not be null';
  end if;

  insert into public.paid_access (user_id, granted_at, amount_vnd, transfer_ref, note, revoked_at)
  values (p_user_id, now(), p_amount_vnd, p_transfer_ref, nullif(trim(p_note), ''), null)
  on conflict (user_id) do update set
    granted_at = now(),
    amount_vnd = excluded.amount_vnd,
    transfer_ref = excluded.transfer_ref,
    note = excluded.note,
    revoked_at = null
  returning * into v_row;

  return v_row;
end;
$$;

-- Revoke an existing grant (refund). Sets revoked_at and appends the reason into note, the
-- same shape as the previous TypeScript logic. Fails gracefully via a status object rather
-- than an exception: {ok:false, reason:'not_found'} when no grant exists, 'already_revoked'
-- when it is already revoked, and {ok:true, access:<row>} on success.
create or replace function public.admin_revoke_paid_access(
  p_user_id uuid,
  p_reason text
)
returns jsonb
language plpgsql
security definer
set search_path = public, pg_temp
as $$
declare
  v_existing public.paid_access;
  v_updated public.paid_access;
  v_note text;
begin
  if not public.is_current_user_admin() then
    raise exception 'not authorized' using errcode = '42501';
  end if;

  if p_user_id is null then
    raise exception 'user_id must not be null';
  end if;
  if p_reason is null or length(trim(p_reason)) = 0 then
    raise exception 'reason must not be null or empty';
  end if;

  select * into v_existing from public.paid_access where user_id = p_user_id;
  if not found then
    return jsonb_build_object('ok', false, 'reason', 'not_found');
  end if;
  if v_existing.revoked_at is not null then
    return jsonb_build_object('ok', false, 'reason', 'already_revoked');
  end if;

  -- Match the prior append semantics: keep the existing note when present, else start fresh.
  if v_existing.note is not null and length(trim(v_existing.note)) > 0 then
    v_note := v_existing.note || ' | revoked: ' || p_reason;
  else
    v_note := 'revoked: ' || p_reason;
  end if;

  update public.paid_access
  set revoked_at = now(), note = v_note
  where user_id = p_user_id
  returning * into v_updated;

  return jsonb_build_object('ok', true, 'access', to_jsonb(v_updated));
end;
$$;

-- Defence in depth on top of the in-body admin check: only authenticated may execute, never
-- anon or the implicit PUBLIC grant.
revoke execute on function public.is_current_user_admin() from public, anon;
grant execute on function public.is_current_user_admin() to authenticated;

revoke execute on function public.admin_search_learner(text) from public, anon;
grant execute on function public.admin_search_learner(text) to authenticated;

revoke execute on function public.admin_activate_paid_access(uuid, integer, text, text) from public, anon;
grant execute on function public.admin_activate_paid_access(uuid, integer, text, text) to authenticated;

revoke execute on function public.admin_revoke_paid_access(uuid, text) from public, anon;
grant execute on function public.admin_revoke_paid_access(uuid, text) to authenticated;
