-- Paid access grants. Deliberately NOT a column on `profiles`: profiles carries an
-- own_update RLS policy, so a learner could grant themselves access by PATCHing their
-- own row through the public API. Access lives in its own table that `authenticated`
-- can only read — every write goes through the dashboard/service role after a bank
-- transfer has been reconciled by hand.

create table paid_access (
  user_id uuid primary key references auth.users (id) on delete cascade,
  granted_at timestamptz not null default now(),
  amount_vnd integer,                            -- what was actually received
  transfer_ref text,                             -- bank reference, for reconciliation
  note text,                                     -- e.g. early-bird, refunded, comp
  revoked_at timestamptz                         -- set on refund; a row with this set grants nothing
);

alter table paid_access enable row level security;

-- Read-only for the owner. No insert/update/delete policy exists, so RLS denies those
-- to anon and authenticated regardless of table grants.
create policy "own_select" on paid_access for select using ((select auth.uid()) = user_id);

revoke all on public.paid_access from anon, authenticated;
grant select on public.paid_access to authenticated;
