-- AI Gym & Fitness Assistant - Supabase (Postgres) schema
-- Run this once in your Supabase project's SQL Editor (Dashboard -> SQL Editor -> New query)
-- before starting the backend.

create extension if not exists pgcrypto;

-- ---------- Users (custom auth - not Supabase Auth) ----------
create table if not exists users (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  email text unique not null,
  password text not null,           -- bcrypt hash, never plaintext
  age integer,
  height_cm double precision,
  weight_kg double precision,
  goal text default 'maintain',
  created_at timestamptz not null default now()
);

-- ---------- Module 1 & 6: workout sessions / pose scoring ----------
create table if not exists workout_sessions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references users(id) on delete cascade,
  exercise text not null,
  reps jsonb not null default '[]',
  duration_seconds double precision not null,
  form_issues jsonb not null default '[]',
  rep_count integer not null default 0,
  feedback jsonb not null default '[]',
  form_score double precision not null default 0,
  tempo_consistency double precision not null default 0,
  created_at timestamptz not null default now()
);
create index if not exists idx_workout_sessions_user_created
  on workout_sessions (user_id, created_at desc);

-- ---------- Module 2: diet plans (one current plan per user) ----------
create table if not exists diet_plans (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null unique references users(id) on delete cascade,
  bmi double precision,
  bmi_category text,
  bmr double precision,
  target_calories double precision,
  macros jsonb,
  meal_plan jsonb,
  grocery_list jsonb,
  updated_at timestamptz not null default now()
);

-- ---------- Module 3: simulated IoT readings ----------
create table if not exists iot_readings (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references users(id) on delete cascade,
  heart_rate integer,
  equipment text,
  current_resistance integer,
  reps_completed integer,
  recommended_resistance integer,
  recommended_rest_seconds integer,
  intensity_status text,
  message text,
  created_at timestamptz not null default now()
);

-- ---------- Module 4: habit tracker (one row per user per day) ----------
create table if not exists habit_logs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references users(id) on delete cascade,
  date date not null,
  workout_completed boolean not null default false,
  planned boolean not null default true,
  unique (user_id, date)
);

-- ---------- Module 5: chat history ----------
create table if not exists chat_history (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references users(id) on delete cascade,
  message text not null,
  reply text not null,
  mood text,
  created_at timestamptz not null default now()
);

-- ---------- Module 6: weekly performance reports ----------
create table if not exists performance_reports (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references users(id) on delete cascade,
  week_start date,
  total_sessions integer,
  avg_form_score double precision,
  avg_tempo_consistency double precision,
  performance_score double precision,
  trend text,
  created_at timestamptz not null default now()
);
create index if not exists idx_performance_reports_user_created
  on performance_reports (user_id, created_at desc);

-- ---------- Module 7: gym directory (seeded automatically on first request) ----------
create table if not exists gyms (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  lat_offset double precision not null,
  lng_offset double precision not null,
  programs jsonb not null default '[]',
  rating double precision
);

-- Row Level Security is left OFF on purpose: this backend uses its own
-- bcrypt+JWT auth (not Supabase Auth) and talks to Postgres only from the
-- server using the service_role key, which bypasses RLS anyway. The API
-- itself enforces per-user access (every query is scoped by the user_id
-- taken from the verified JWT). If you later let the frontend call
-- Supabase directly with the anon key, enable RLS and write policies
-- keyed off auth.uid() first - don't do that with the current auth setup.
