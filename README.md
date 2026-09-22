# AI Gym & Fitness Assistant

A unified AI fitness ecosystem implementing all 7 modules from the project brief:

| # | Module | How it's implemented here |
|---|--------|---------------------------|
| 1 | AI Gym Trainer (workout detection) | **Real** computer vision - MediaPipe Pose analyzes your webcam feed, computes joint angles, and counts reps with a state machine. No physical equipment needed, just a webcam. |
| 2 | AI Dietician & Calorie Coach | Mifflin-St Jeor BMR + activity multipliers + goal adjustment, templated meal plans (veg/non-veg/vegan) and a generated grocery list. |
| 3 | Smart Gym Assistant (AI + IoT) | **Simulated** sensor readings (heart rate, resistance, reps) since no physical IoT hardware is required - the AI decision logic (resistance/rest recommendation from heart-rate zones) is real and swappable for a live MQTT feed later. |
| 4 | AI Fitness Habit Tracker | Recency-weighted adherence log → skip-risk % and streak tracking → motivational nudges. |
| 5 | Virtual Gym Buddy | Keyword-based sentiment detection + mood-aware canned responses (works fully offline, no API key needed; there's a commented hook to swap in a real LLM later). |
| 6 | Pose-to-Performance Analyzer | Aggregates form score + tempo consistency from your Module 1 sessions into a weekly performance score and trend. |
| 7 | Gym Recommender & Planner | Haversine-distance based recommender over a small seeded gym dataset near your coordinates, filtered/sorted by your goal. |

**Backend:** FastAPI (Python) · Supabase (Postgres, cloud) · JWT auth — shared by both frontends below.

**Two frontend options are included — pick one:**
- **`streamlit_app/`** - single-command Streamlit UI. Pose detection runs **server-side** (MediaPipe processes your webcam frames in Python via `streamlit-webrtc`). Simplest to run and demo.
- **`frontend/`** - React (Vite) UI. Pose detection runs **client-side** in the browser (MediaPipe.js). Closer to the PDF's proposed stack (React/Next.js), better if you want to show a traditional full-stack web app for your report.

Both talk to the exact same backend and database - you can run either, or both, without touching backend code.

---

## 1. Prerequisites

- **Python 3.10+** installed (Node.js 18+ too, only if you also want the React frontend)
- **VS Code** (with the Python extension; add ES7+ React if using the React frontend)
- A free **Supabase** account (this is your cloud Postgres database): https://supabase.com/dashboard/sign-up
- A webcam, for Module 1

## 2. Set up Supabase (cloud database)

1. Sign up / log in at https://supabase.com/dashboard and click **New project**.
2. Pick an organization, name the project, set a database password (you won't need this password directly - Supabase gives you an API key instead), and choose a region close to you. Wait ~2 minutes for it to provision.
3. Open the **SQL Editor** (left sidebar) → **New query**, paste in the entire contents of `backend/supabase_schema.sql` from this project, and click **Run**. This creates all 8 tables the app needs (`users`, `workout_sessions`, `diet_plans`, `iot_readings`, `habit_logs`, `chat_history`, `performance_reports`, `gyms`).
4. Go to **Project Settings → API**. You need two values from this page:
   - **Project URL** (looks like `https://xxxxxxxxxxxx.supabase.co`)
   - **`service_role` secret key** (⚠️ **not** the `anon`/`public` key — the service role key is required because this backend does its own auth and needs full database access from the server; never expose this key in frontend code)

You'll paste both into the backend `.env` in the next step.

## 3. Backend setup (FastAPI) - required either way

Open the project in VS Code, then in the integrated terminal:

```bash
cd backend
python -m venv venv

# Activate the virtual environment
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
```

Create your environment file:

```bash
cp .env.example .env         # macOS/Linux
copy .env.example .env       # Windows
```

Open `.env` and fill in:
- `SUPABASE_URL` - your Project URL from step 2
- `SUPABASE_KEY` - your `service_role` key from step 2
- `JWT_SECRET` - any long random string (e.g. generate one with `python -c "import secrets; print(secrets.token_hex(32))"`)

Run the API:

```bash
uvicorn app.main:app --reload
```

You should see it running at **http://localhost:8000**. Visit **http://localhost:8000/docs** for interactive Swagger docs covering every endpoint (great for testing each module independently before touching either frontend). Leave this running in its own terminal.

## 4a. Streamlit frontend setup (recommended, simplest)

Open a **second terminal**:

```bash
cd streamlit_app
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
cp .env.example .env         # macOS/Linux
copy .env.example .env       # Windows

streamlit run app.py
```

It opens automatically at **http://localhost:8501**. `.env` already points `API_URL` at `http://localhost:8000`, matching the backend.

**Note on `requirements.txt` versions:** these are pinned deliberately, not arbitrarily. `streamlit-webrtc` needs an older `mediapipe` release (0.10.21) because newer `mediapipe` versions removed the legacy `solutions.pose` API this project uses; that in turn needs an older `streamlit` (1.37.0) because newer Streamlit requires a `protobuf` version incompatible with that `mediapipe`. Installing outside these pins will hit a real dependency conflict (I hit it myself while building this - don't relax these pins). The backend has its own deliberate pin too: `bcrypt==4.0.1`, because newer `bcrypt` releases break `passlib`'s password hashing.

## 4b. React frontend setup (alternative)

Open a second terminal:

```bash
cd frontend
npm install
cp .env.example .env         # macOS/Linux
copy .env.example .env       # Windows
npm run dev
```

Visit **http://localhost:5173**. `.env` already points `VITE_API_URL` at `http://localhost:8000`.

## 5. Try it out

Works the same regardless of which frontend you chose:

1. Register an account (name, email, password, plus your age/height/weight/goal).
2. **AI Gym Trainer** - pick an exercise, start the camera, do a few reps, stop & save to see your rep count, form score and feedback.
3. **Diet Coach** - fill in your stats, generate a plan.
4. **Smart Gym (IoT)** - get a simulated sensor reading, then an AI recommendation.
5. **Habit Tracker** - log a day as done/skipped, watch the skip-risk % and streak update.
6. **Gym Buddy** - chat with it; try clearly positive/negative phrases to see mood detection change the reply.
7. **Performance** - after a couple of Workout sessions, check your weekly performance score.
8. **Gym Finder** - set your location (React: browser geolocation; Streamlit: enter lat/long manually), then find gyms.

## 6. Project structure

```
gym-fitness-assistant/
├── backend/                     # shared by both frontends
│   ├── app/
│   │   ├── main.py              # FastAPI app + router registration + startup (init Supabase client, seed gyms)
│   │   ├── config.py            # env-based settings
│   │   ├── database.py          # Supabase async client (lazily initialized at startup)
│   │   ├── models/schemas.py    # Pydantic request/response models
│   │   ├── routers/             # one router per module (auth, workout, diet, iot, habit, chatbot, performance, recommender)
│   │   └── services/            # business logic per module (kept separate from routers for clarity/testing)
│   ├── supabase_schema.sql      # run once in the Supabase SQL Editor to create all tables
│   ├── requirements.txt
│   └── .env.example
├── streamlit_app/                # Option A frontend
│   ├── app.py                    # dashboard / entry point
│   ├── pages/                    # one page per module (Streamlit auto-builds the sidebar nav from these)
│   ├── utils/
│   │   ├── api_client.py         # wraps every backend call + error handling
│   │   └── auth.py               # shared login/register gate
│   ├── requirements.txt
│   └── .env.example
└── frontend/                     # Option B frontend
    ├── src/
    │   ├── pages/                # one page per module + Login/Register/Dashboard
    │   ├── components/Navbar.jsx
    │   ├── context/AuthContext.jsx
    │   └── api.js                # axios instance, auto-attaches JWT
    ├── index.html                # loads MediaPipe Pose from CDN for Module 1
    └── .env.example
```

## 7. Deploying later

Supabase is already cloud-hosted, so deployment is just hosting the app(s) you use:

- **Backend** → Render, Railway, or Fly.io (all have free tiers for FastAPI). Set the same env vars (`SUPABASE_URL`, `SUPABASE_KEY`, `JWT_SECRET`, etc.) in the host's dashboard, and set `FRONTEND_ORIGINS` to your deployed frontend URL.
- **Streamlit frontend** → Streamlit Community Cloud (free, built for exactly this) or Render. Set `API_URL` to your deployed backend URL as an environment variable/secret.
- **React frontend** → Vercel or Netlify. Set `VITE_API_URL` to your deployed backend URL, then `npm run build`.
- No database network allow-list to manage (unlike self-hosted Postgres) - Supabase's API endpoint is public by default and access is controlled entirely by your API keys, so nothing extra to configure there when you move hosts.

## 8. Notes on scope (for your report/viva)

- **IoT (Module 3):** per your instructions, no physical IoT hardware is wired up. `/iot/simulate` generates realistic sensor readings so the full pipeline (sensor → AI decision → UI) works end-to-end; swapping in real hardware later only means replacing that one endpoint with an MQTT subscriber.
- **Pose detection (Module 1):** this *is* real pose estimation, not simulated - MediaPipe genuinely tracks your joints from webcam frames (client-side in React, server-side in Streamlit) - so it's a real computer-vision component for your submission.
- **Conversational AI (Module 5):** uses rule-based sentiment + templated responses so the project runs fully free/offline with no API key. A commented hook in `chat_service.py` shows exactly where to plug in a real LLM if you want to extend it.
- **Gym Recommender (Module 7):** uses a small seeded mock dataset positioned near your real coordinates (haversine distance is real math). Swapping in a live Google Places/OSM feed is a one-function change (see `recommender_service.py`).
- **Why two frontends:** the PDF's stack table proposes React/Next.js, which `frontend/` follows; you asked separately for a Streamlit version, which `streamlit_app/` provides against the identical backend/API - so you can pick whichever fits your submission, or mention both as "frontend options evaluated" in your report.
- **Why Supabase instead of the PDF's proposed MongoDB/PostgreSQL:** the PDF's stack table lists "MongoDB / PostgreSQL" as options; this build uses Supabase, which is hosted Postgres with a REST API on top, so `backend/supabase_schema.sql` defines a proper relational schema (foreign keys, a `unique` constraint on `diet_plans.user_id` and on `habit_logs(user_id, date)` used for upserts) rather than schemaless Mongo documents. Auth is still this app's own bcrypt+JWT system, not Supabase Auth, so switching later to Supabase Auth (or adding Row Level Security for direct frontend-to-Supabase calls) is a separate, optional step - not required for anything here to work.
