-- Separate progress for listening fill-in-the-blank practice (audio + gapped passage).
-- Mirrors 000006_writing_progress.sql exactly: same shape, same RLS, same
-- advisory-lock/best-score/streak semantics — just a different exercise family so a
-- learner's Writing and Listening stats never collide or double-count.
create table public.listening_progress (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  listening_id text not null,
  status text not null default 'in_progress' check (status in ('in_progress', 'completed')),
  best_score smallint check (best_score between 0 and 100),
  completed_at timestamptz,
  updated_at timestamptz not null default now(),
  unique (user_id, listening_id)
);

create index idx_listening_progress_user on public.listening_progress (user_id);

alter table public.listening_progress enable row level security;
create policy "own_select" on public.listening_progress for select using ((select auth.uid()) = user_id);
create policy "own_insert" on public.listening_progress for insert with check ((select auth.uid()) = user_id);
create policy "own_update" on public.listening_progress for update using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);

grant select, insert, update on public.listening_progress to authenticated;

alter table public.daily_activity
  add column listening_completed integer not null default 0;

create or replace function public.record_listening_attempt(
  p_listening_id text,
  p_score smallint
) returns void
language plpgsql
security invoker
as $$
declare
  v_user_id uuid := auth.uid();
  v_old_status text;
  v_passed boolean;
  v_activity_date date := (now() at time zone 'Asia/Ho_Chi_Minh')::date;
begin
  if v_user_id is null then
    raise exception 'Not authenticated';
  end if;
  if p_listening_id is null or length(trim(p_listening_id)) = 0 then
    raise exception 'listening_id must not be null or empty';
  end if;
  if p_score is null or p_score < 0 or p_score > 100 then
    raise exception 'Score must be between 0 and 100';
  end if;

  v_passed := p_score >= 80;
  perform pg_advisory_xact_lock(hashtext(v_user_id::text), hashtext(p_listening_id));

  select status into v_old_status
  from public.listening_progress
  where user_id = v_user_id and listening_id = p_listening_id;

  insert into public.listening_progress (user_id, listening_id, status, best_score, completed_at, updated_at)
  values (
    v_user_id,
    p_listening_id,
    case when v_passed then 'completed' else 'in_progress' end,
    p_score,
    case when v_passed then now() else null end,
    now()
  )
  on conflict (user_id, listening_id) do update set
    status = case
      when public.listening_progress.status = 'completed' or v_passed then 'completed'
      else 'in_progress'
    end,
    best_score = greatest(coalesce(public.listening_progress.best_score, 0), excluded.best_score),
    completed_at = case
      when v_passed then coalesce(public.listening_progress.completed_at, now())
      else public.listening_progress.completed_at
    end,
    updated_at = now();

  if v_passed and v_old_status is distinct from 'completed' then
    insert into public.daily_activity (user_id, activity_date, listening_completed, learning_day, updated_at)
    values (v_user_id, v_activity_date, 1, true, now())
    on conflict (user_id, activity_date) do update set
      listening_completed = public.daily_activity.listening_completed + 1,
      learning_day = true,
      updated_at = now();
  end if;
end;
$$;

revoke execute on function public.record_listening_attempt(text, smallint) from public, anon;
grant execute on function public.record_listening_attempt(text, smallint) to authenticated;
