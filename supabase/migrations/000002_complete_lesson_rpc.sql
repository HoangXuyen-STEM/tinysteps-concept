-- Migration 02: Add complete_lesson_rpc function

-- Add check constraint for score to be between 0 and 100
alter table public.lesson_progress 
  add constraint check_score_range check (score >= 0 and score <= 100);

create or replace function public.complete_lesson_rpc(
    p_lesson_id text,
    p_score smallint
) returns void
language plpgsql
security invoker
as $$
declare
    v_user_id uuid;
    v_old_status text;
    v_activity_date date;
begin
    v_user_id := auth.uid();
    if v_user_id is null then
        raise exception 'Not authenticated';
    end if;

    -- Explicit NULL checks first: `x < 0` / `x > 100` evaluate to NULL (not TRUE) when
    -- x is NULL, so the range check below would silently let a NULL score through
    -- (and GREATEST() would then ignore it rather than reject it). lesson_id is NOT
    -- NULL on the table, but an empty string would still pass that constraint.
    if p_lesson_id is null or length(trim(p_lesson_id)) = 0 then
        raise exception 'lesson_id must not be null or empty';
    end if;

    if p_score is null then
        raise exception 'score must not be null';
    end if;

    if p_score < 0 or p_score > 100 then
        raise exception 'Score must be between 0 and 100';
    end if;

    -- Obtain a transaction-level advisory lock based on user_id and lesson_id
    -- to prevent race conditions where two simultaneous requests both read 
    -- the old status as not completed and then both increment daily_activity.
    perform pg_advisory_xact_lock(
        hashtext(v_user_id::text), 
        hashtext(p_lesson_id)
    );

    -- Calculate the activity date in Asia/Ho_Chi_Minh timezone
    v_activity_date := (now() at time zone 'Asia/Ho_Chi_Minh')::date;

    -- Get old status if it exists to prevent double-counting daily activity
    select status into v_old_status
    from public.lesson_progress
    where user_id = v_user_id and lesson_id = p_lesson_id;

    -- Upsert lesson progress
    insert into public.lesson_progress (user_id, lesson_id, status, score, completed_at, updated_at)
    values (v_user_id, p_lesson_id, 'completed', p_score, now(), now())
    on conflict (user_id, lesson_id)
    do update set
        status = 'completed',
        score = greatest(coalesce(public.lesson_progress.score, 0), excluded.score),
        completed_at = coalesce(public.lesson_progress.completed_at, excluded.completed_at),
        updated_at = now();

    -- Upsert daily activity only if it wasn't already completed
    if v_old_status is distinct from 'completed' then
        insert into public.daily_activity (user_id, activity_date, lessons_completed, learning_day, updated_at)
        values (v_user_id, v_activity_date, 1, true, now())
        on conflict (user_id, activity_date)
        do update set
            lessons_completed = public.daily_activity.lessons_completed + 1,
            learning_day = true,
            updated_at = now();
    end if;
end;
$$;

-- Revoke default public execution rights to secure the RPC
revoke execute on function public.complete_lesson_rpc(text, smallint) from public, anon;
grant execute on function public.complete_lesson_rpc(text, smallint) to authenticated;
