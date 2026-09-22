-- Run this once in the Supabase SQL Editor if you already created your
-- tables before the admin feature was added (adds the is_admin column
-- without touching any existing data).

alter table public.users add column if not exists is_admin boolean not null default false;

-- Promote your own account to admin - replace the email with the one you
-- registered with in the app, then run just this line.
update public.users set is_admin = true where email = 'you@example.com';
