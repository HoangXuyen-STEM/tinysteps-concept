-- Admin overview of all registered learners and their learning progress.
--
-- Security boundary: SECURITY DEFINER, re-checking admin_users via is_current_user_admin().
-- Non-admin callers receive permission_denied error regardless of table grants.

create or replace function public.admin_list_learner_progress()
returns table (
  user_id uuid,
  email text,
  last_sign_in_at timestamptz,
  created_at timestamptz,
  is_paid boolean,
  lessons_completed bigint,
  lessons_in_progress bigint,
  days_active bigint
)
language plpgsql
security definer
set search_path = public
as $$
begin
  if not public.is_current_user_admin() then
    raise exception 'permission_denied'
      using hint = 'Admin user privileges required';
  end if;

  return query
  select
    u.id as user_id,
    u.email::text as email,
    u.last_sign_in_at as last_sign_in_at,
    u.created_at as created_at,
    (pa.user_id is not null and pa.revoked_at is null) as is_paid,
    coalesce(count(lp.id) filter (where lp.status = 'completed'), 0) as lessons_completed,
    coalesce(count(lp.id) filter (where lp.status = 'in_progress'), 0) as lessons_in_progress,
    coalesce(count(distinct da.activity_date), 0) as days_active
  from auth.users u
  left join public.paid_access pa on pa.user_id = u.id
  left join public.lesson_progress lp on lp.user_id = u.id
  left join public.daily_activity da on da.user_id = u.id
  group by u.id, u.email, u.last_sign_in_at, u.created_at, pa.user_id, pa.revoked_at
  order by u.last_sign_in_at desc nulls last, u.created_at desc;
end;
$$;

revoke all on function public.admin_list_learner_progress() from public;
grant execute on function public.admin_list_learner_progress() to authenticated;
