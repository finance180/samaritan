# Samaritan LMS — Supabase Setup

## 1. Create Project

1. Go to [supabase.com](https://supabase.com) and sign in
2. Click **New Project**
3. Name: `Samaritan LMS`
4. Set a database password (save it)
5. Region: Choose closest to you (e.g., US East)

## 2. Run Schema

1. In your Supabase dashboard, go to **SQL Editor**
2. Click **New Query**
3. Paste the contents of `schema.sql`
4. Click **Run**

This creates the `tasks` and `projects` tables with auto-generated IDs.

## 3. Get API Credentials

1. Go to **Settings > API** in the Supabase dashboard
2. Copy:
   - **Project URL** (e.g., `https://xxxxx.supabase.co`)
   - **anon public** key (under Project API keys)

## 4. Configure Samaritan

Create a `.env` file in the project root:
```
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbG...your-anon-key...
```

## 5. Test

```bash
source .env

# Insert a test task
curl -sL "${SUPABASE_URL}/rest/v1/tasks" \
  -H "apikey: ${SUPABASE_ANON_KEY}" \
  -H "Authorization: Bearer ${SUPABASE_ANON_KEY}" \
  -H "Content-Type: application/json" \
  -H "Prefer: return=representation" \
  -d '{"title":"Test task","business":"Personal","priority":"Medium"}'

# Read all tasks
curl -sL "${SUPABASE_URL}/rest/v1/tasks?status=eq.Active&order=due_date" \
  -H "apikey: ${SUPABASE_ANON_KEY}" \
  -H "Authorization: Bearer ${SUPABASE_ANON_KEY}"

# Delete the test task
curl -sL -X DELETE "${SUPABASE_URL}/rest/v1/tasks?title=eq.Test%20task" \
  -H "apikey: ${SUPABASE_ANON_KEY}" \
  -H "Authorization: Bearer ${SUPABASE_ANON_KEY}"
```
