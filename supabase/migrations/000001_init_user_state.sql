-- Per-user application state. Content (vocab/lessons) stays static in the app bundle;
-- only user-scoped progress lives here. Every table is RLS-protected and keyed to auth.uid().

create table profiles (
  id uuid primary key references auth.users (id) on delete cascade,
  display_name text,
  current_level text default 'starters',        -- starters|movers|flyers|ket|pet
  created_at timestamptz not null default now()
);

create table lesson_progress (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  lesson_id text not null,                       -- e.g. starters_lesson_001
  status text not null default 'not_started',    -- not_started|in_progress|completed
  score smallint,                                -- 0..100
  completed_at timestamptz,
  updated_at timestamptz not null default now(),
  unique (user_id, lesson_id)
);

create table srs_cards (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  vocab_id text not null,                        -- e.g. starters_vocab_001
  due timestamptz not null,
  stability double precision not null default 0,
  difficulty double precision not null default 0,
  elapsed_days integer not null default 0,
  scheduled_days integer not null default 0,
  reps integer not null default 0,
  lapses integer not null default 0,
  state smallint not null default 0,             -- 0 New, 1 Learning, 2 Review, 3 Relearning
  last_review timestamptz,
  created_at timestamptz not null default now(),
  unique (user_id, vocab_id)
);

-- Per-local-day activity counters. Needed because srs_cards.last_review is overwritten
-- each review and cannot reconstruct historical per-day counts for the streak rule.
-- activity_date is the calendar day in Asia/Ho_Chi_Minh, computed server-side.
create table daily_activity (
  user_id uuid not null references auth.users (id) on delete cascade,
  activity_date date not null,
  lessons_completed integer not null default 0,
  cards_reviewed integer not null default 0,
  learning_day boolean not null default false,   -- true once the streak criterion is met that day
  updated_at timestamptz not null default now(),
  primary key (user_id, activity_date)
);

create index idx_srs_cards_user_due on srs_cards (user_id, due);
create index idx_srs_cards_user_state on srs_cards (user_id, state);
create index idx_lesson_progress_user on lesson_progress (user_id);

-- Row Level Security: a user may touch only their own rows. The (select auth.uid())
-- wrapper lets Postgres cache the value once per query instead of per row.
alter table profiles enable row level security;
create policy "own_select" on profiles for select using ((select auth.uid()) = id);
create policy "own_insert" on profiles for insert with check ((select auth.uid()) = id);
create policy "own_update" on profiles for update using ((select auth.uid()) = id) with check ((select auth.uid()) = id);
create policy "own_delete" on profiles for delete using ((select auth.uid()) = id);

alter table lesson_progress enable row level security;
create policy "own_select" on lesson_progress for select using ((select auth.uid()) = user_id);
create policy "own_insert" on lesson_progress for insert with check ((select auth.uid()) = user_id);
create policy "own_update" on lesson_progress for update using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
create policy "own_delete" on lesson_progress for delete using ((select auth.uid()) = user_id);

alter table srs_cards enable row level security;
create policy "own_select" on srs_cards for select using ((select auth.uid()) = user_id);
create policy "own_insert" on srs_cards for insert with check ((select auth.uid()) = user_id);
create policy "own_update" on srs_cards for update using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
create policy "own_delete" on srs_cards for delete using ((select auth.uid()) = user_id);

alter table daily_activity enable row level security;
create policy "own_select" on daily_activity for select using ((select auth.uid()) = user_id);
create policy "own_insert" on daily_activity for insert with check ((select auth.uid()) = user_id);
create policy "own_update" on daily_activity for update using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
create policy "own_delete" on daily_activity for delete using ((select auth.uid()) = user_id);

-- Grants
grant select, insert, update on public.lesson_progress to authenticated;
grant select, insert, update on public.daily_activity to authenticated;

-- Auto-create a profile row for every new auth user, including accounts created
-- manually in the dashboard for the pilot. security definer bypasses RLS for the insert.
create function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
begin
  insert into public.profiles (id) values (new.id);
  return new;
end;
$$;

create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();
