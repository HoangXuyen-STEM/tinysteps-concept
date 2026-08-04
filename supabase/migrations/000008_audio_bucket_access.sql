-- Split audio storage along the paywall.
--
-- A single public "audio" bucket served every recording to anyone who guessed a
-- filename, and the names are sequential (starters_listening_002.mp3), so the whole
-- library was enumerable without an account. Trial recordings move to a public bucket
-- that is meant to be given away; everything else stays in "audio", now private, where
-- reads are signed and gated on an active paid grant.

-- Trial content: the free lessons, the free listening exercise, and the words they
-- teach. Public on purpose — these are what a parent listens to before paying.
insert into storage.buckets (id, name, public)
values ('audio-free', 'audio-free', true)
on conflict (id) do update set public = true;

-- Everything, including the paid recordings. Private from here on.
insert into storage.buckets (id, name, public)
values ('audio', 'audio', false)
on conflict (id) do update set public = false;

-- storage.objects has RLS on by default; without a policy no anon-key client can sign a
-- URL for this bucket. Service-role uploads bypass RLS and are unaffected.
drop policy if exists "paid_audio_read" on storage.objects;
create policy "paid_audio_read"
on storage.objects for select
to authenticated
using (
  bucket_id = 'audio'
  and exists (
    select 1 from public.paid_access
    where user_id = (select auth.uid())
      and revoked_at is null
  )
);
