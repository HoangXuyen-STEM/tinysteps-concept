-- SRS review support.
--
-- 1. learning_steps column: part of the ts-fsrs Card state (v5.3+). It tracks the
--    card's position within the intraday learning/relearning step sequence
--    (default ["1m","10m"]). Without persisting it, a card reloaded mid-learning
--    would restart at step 0 and be rescheduled with the wrong short interval.
alter table public.srs_cards
  add column learning_steps integer not null default 0;

-- 2. DML grants that migration 000001 left off. In this project the authenticated
--    role only received the default REFERENCES/TRIGGER/TRUNCATE on these tables, so
--    RLS never even got a chance — every read/write was denied at the grant layer.
--    srs_cards is read/written by the review flow; profiles.current_level is read to
--    pick the level new cards are drawn from (and display_name by the dashboard).
grant select, insert, update on public.srs_cards to authenticated;
grant select on public.profiles to authenticated;

-- 3. Atomic per-day review counter for the streak rule. Increments the caller's
--    daily_activity row for the current Asia/Ho_Chi_Minh day and flips learning_day
--    once the criterion is met: a full batch of 5 reviews in the day, OR the session
--    emptied the due queue (p_queue_emptied) with no cards still due. Vietnam has no
--    DST, so the tz is a fixed +07. security invoker → RLS applies, auth.uid() acts.
create or replace function public.record_review_activity(p_queue_emptied boolean)
returns void
language plpgsql
security invoker
as $$
declare
    v_user_id uuid := auth.uid();
    v_date date := (now() at time zone 'Asia/Ho_Chi_Minh')::date;
    v_reviewed integer;
    v_due_remaining integer;
begin
    if v_user_id is null then
        raise exception 'Not authenticated';
    end if;

    insert into public.daily_activity (user_id, activity_date, cards_reviewed, updated_at)
    values (v_user_id, v_date, 1, now())
    on conflict (user_id, activity_date) do update set
        cards_reviewed = public.daily_activity.cards_reviewed + 1,
        updated_at = now()
    returning cards_reviewed into v_reviewed;

    -- Counted AFTER the reviewed card's due has been pushed forward by the caller, so
    -- the just-answered card is not counted as still due.
    select count(*) into v_due_remaining
    from public.srs_cards
    where user_id = v_user_id and due <= now();

    if v_reviewed >= 5 or (coalesce(p_queue_emptied, false) and v_due_remaining = 0) then
        update public.daily_activity
        set learning_day = true, updated_at = now()
        where user_id = v_user_id
          and activity_date = v_date
          and learning_day = false;
    end if;
end;
$$;

revoke execute on function public.record_review_activity(boolean) from public, anon;
grant execute on function public.record_review_activity(boolean) to authenticated;
