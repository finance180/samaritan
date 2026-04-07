# Evening Wind-Down Ritual — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the barebones 6 PM evening check-in with a guided 3-step wind-down ritual — quick wins, tomorrow's top 3, and open loops brain dump.

**Architecture:** A new skill file (`.claude/skills/wind-down.md`) contains the full guided flow. The `daily-briefing.md` agent gets an updated Evening Check-in section that invokes the wind-down skill. A new scheduled task fires at 6 PM CT daily. Morning briefing gets a small addition to surface last night's top 3.

**Tech Stack:** Supabase PostgREST (notes table), existing `/catch` classification logic, scheduled-tasks MCP.

---

### Task 1: Create the Wind-Down Skill

**Files:**
- Create: `.claude/skills/wind-down.md`

- [ ] **Step 1: Create the skill file**

Create `.claude/skills/wind-down.md` with the following content:

```markdown
---
name: wind-down
description: Evening wind-down ritual — celebrate wins, set tomorrow's priorities, clear open loops.
---

# Evening Wind-Down Ritual

You are Samaritan running Brian's evening wind-down. This is a guided 3-step ritual. Walk through each step conversationally. Do NOT rush — wait for Brian's input at each step.

## Setup

```bash
source "/Users/brianthompson/Documents/01 Projects/Claude Projects/Samaritan/.env" 2>/dev/null
HEADERS=(-H "apikey: ${SUPABASE_ANON_KEY}" -H "Authorization: Bearer ${SUPABASE_ANON_KEY}")
TODAY=$(TZ=America/Chicago date +%Y-%m-%d)
TOMORROW=$(TZ=America/Chicago date -v+1d +%Y-%m-%d)
THREE_DAYS=$(TZ=America/Chicago date -v+3d +%Y-%m-%d)
```

## Step 1: Quick Wins

Query today's completed tasks:
```bash
curl -sL "${SUPABASE_URL}/rest/v1/tasks?status=eq.Completed&completed_at=gte.${TODAY}T00:00:00&order=business,completed_at" "${HEADERS[@]}"
```

Present them grouped by business:
```
🏆 Here's what you knocked out today:

**Happy Pup Manor**
- Onboarded new grooming client

**Reseller Business**
- Closed the Hasbro compliance issue
- Shipped 12 FBA orders

**Personal**
- (none today)
```

Then ask: **"What were your top 3 wins today? Pick from the list or add your own."**

Wait for Brian's response. Store his picks for the journal note.

If Brian doesn't respond or says "skip", move to Step 2.

## Step 2: Tomorrow's Top 3

Query upcoming tasks:
```bash
# Due tomorrow
curl -sL "${SUPABASE_URL}/rest/v1/tasks?due_date=eq.${TOMORROW}&status=eq.Active&order=priority,business" "${HEADERS[@]}"

# Overdue
curl -sL "${SUPABASE_URL}/rest/v1/tasks?due_date=lt.${TODAY}&status=eq.Active&order=due_date" "${HEADERS[@]}"

# High priority next 3 days
curl -sL "${SUPABASE_URL}/rest/v1/tasks?due_date=gte.${TOMORROW}&due_date=lte.${THREE_DAYS}&priority=eq.High&status=eq.Active&order=due_date" "${HEADERS[@]}"
```

Present as a numbered list grouped by business:
```
📋 Here's what's on deck for tomorrow:

**Due Tomorrow:**
1. [High] Submit CPC documentation — Reseller Business
2. [Medium] Review staff schedule — Happy Pup Manor

**Overdue:**
3. [High] Call insurance agent — Personal

**High Priority (next 3 days):**
4. [High] Quarterly inventory count — Reseller Business
```

Then ask: **"Pick your top 3 priorities for tomorrow."**

Wait for Brian's response. Store his picks for the journal note.

If Brian doesn't respond or says "skip", move to Step 3.

## Step 3: Open Loops Brain Dump

Ask: **"Anything still bouncing around in your head? List them out — I'll sort them."**

Wait for Brian's response.

For each item, triage using `/catch` classification logic:
- If it sounds like a task (keywords: "remind me", "need to", "have to", "should", "follow up") → create task in Supabase
- If it has a date/time and sounds like a meeting/appointment → suggest calendar event via `gcal_create_event`
- Otherwise → save as a note with `type: "idea"` and `source: "wind-down"`

After processing all items, confirm:
```
✅ Captured 3 items — 2 tasks, 1 idea. Your head is clear.
```

If Brian says "nothing" or "nope", skip to the journal save.

## Save the Journal Note

After all 3 steps (or skips), save a single journal note with everything:

```bash
curl -sL "${SUPABASE_URL}/rest/v1/notes" "${HEADERS[@]}" \
  -H "Content-Type: application/json" -H "Prefer: return=representation" \
  -d '{
    "title": "Wind-Down — YYYY-MM-DD",
    "type": "text",
    "source": "wind-down",
    "business": "Personal",
    "tags": ["journal", "wins", "wind-down", "YYYY-MM-DD"],
    "content": "# Wind-Down — YYYY-MM-DD\n\n## Today'\''s Wins\n1. ...\n2. ...\n3. ...\n\n## Tomorrow'\''s Top 3\n1. ...\n2. ...\n3. ...\n\n## Open Loops Captured\n- ..."
  }'
```

Replace the date and content dynamically based on Brian's responses.

## Closing

End with:
```
Wind-down complete. Tomorrow's priorities are locked in. Have a good evening, Brian.
```

## Key Rules

- Wait for Brian's input at each step — this is a conversation, not a report
- If Brian skips a step, move on gracefully
- Always save the journal note even if some steps were skipped (just mark those sections as "Skipped")
- Use today's actual date (America/Chicago timezone) everywhere
- Group tasks by business in all displays
```

- [ ] **Step 2: Verify the skill file is valid**

Run: `head -5 .claude/skills/wind-down.md`
Expected: YAML frontmatter with `name: wind-down` and `description`

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/wind-down.md
git commit -m "feat: add evening wind-down skill — guided 3-step ritual"
```

---

### Task 2: Update Daily Briefing Agent — Evening Section

**Files:**
- Modify: `.claude/agents/daily-briefing.md` (lines 227-246, the "Evening Check-in" section)

- [ ] **Step 1: Replace the Evening Check-in section**

In `.claude/agents/daily-briefing.md`, replace the existing "### 3. Evening Check-in (6:00 PM)" section (lines 227-246) with:

```markdown
### 3. Evening Wind-Down (6:00 PM)

Invoke the **wind-down** skill for a guided 3-step evening ritual:

1. **Quick Wins** — show today's completed tasks, ask Brian for his top 3 wins
2. **Tomorrow's Top 3** — show upcoming/overdue tasks, ask Brian to pick 3 priorities
3. **Open Loops** — brain dump anything still in his head, triage each item

The wind-down skill handles all the logic. See `.claude/skills/wind-down.md` for the full flow.

After the wind-down completes, it saves a journal note (`source: "wind-down"`) that the morning briefing picks up.
```

- [ ] **Step 2: Verify the edit**

Run: `grep -n "Evening Wind-Down" .claude/agents/daily-briefing.md`
Expected: Line with "### 3. Evening Wind-Down (6:00 PM)"

- [ ] **Step 3: Commit**

```bash
git add .claude/agents/daily-briefing.md
git commit -m "feat: replace evening check-in with wind-down ritual in daily-briefing"
```

---

### Task 3: Update Daily Briefing Agent — Morning Integration

**Files:**
- Modify: `.claude/agents/daily-briefing.md` (insert after Step 1 — Journal Prompt, before Step 2)

- [ ] **Step 1: Add wind-down recall to the morning briefing**

In `.claude/agents/daily-briefing.md`, insert a new step after Step 1 (Journal Prompt) and before Step 2 (Process Recurring Tasks). This becomes the new **Step 1.5**:

```markdown
**Step 1.5 — Last Night's Priorities:**
Check if Brian set priorities during last night's wind-down:
```bash
YESTERDAY=$(TZ=America/Chicago date -v-1d +%Y-%m-%d)
curl -sL "${SUPABASE_URL}/rest/v1/notes?source=eq.wind-down&tags=cs.{${YESTERDAY}}&order=created_at.desc&limit=1" "${HEADERS[@]}"
```

If a wind-down note exists, extract the "Tomorrow's Top 3" section and display:
```
🎯 Last night you set these priorities for today:
1. [High] Submit CPC documentation — Reseller Business
2. [Medium] Review staff schedule — Happy Pup Manor
3. [Medium] Schedule dentist appointment — Personal
```

If no wind-down note found, skip this step silently.
```

- [ ] **Step 2: Verify the edit**

Run: `grep -n "Last Night" .claude/agents/daily-briefing.md`
Expected: Line with "Step 1.5 — Last Night's Priorities"

- [ ] **Step 3: Commit**

```bash
git add .claude/agents/daily-briefing.md
git commit -m "feat: morning briefing surfaces last night's wind-down priorities"
```

---

### Task 4: Create the Scheduled Task

**Files:**
- No files — uses the `scheduled-tasks` MCP to create a new scheduled task

- [ ] **Step 1: Create the evening wind-down scheduled task**

Use the `mcp__scheduled-tasks__create_scheduled_task` tool with:
- `taskId`: `evening-wind-down`
- `cronExpression`: `3 18 * * *` (6:03 PM CT daily — offset to avoid the :00 mark)
- `description`: `Evening wind-down ritual — wins, tomorrow's top 3, open loops brain dump`
- `prompt`: The prompt should instruct Samaritan to run the evening wind-down flow by:
  1. Loading credentials from `.env`
  2. Running Step 1 (Quick Wins) — query completed tasks, ask for top 3 wins
  3. Running Step 2 (Tomorrow's Top 3) — query upcoming tasks, ask for 3 priorities
  4. Running Step 3 (Open Loops) — ask for brain dump, triage each item via /catch logic
  5. Saving the journal note to Supabase
  6. Closing with a brief wind-down message

- [ ] **Step 2: Verify the scheduled task was created**

Use `mcp__scheduled-tasks__list_scheduled_tasks` and confirm `evening-wind-down` appears with cron `3 18 * * *` and enabled = true.

- [ ] **Step 3: Verify no duplicate evening tasks exist**

Check that the old `daily-briefing` task is still running for the morning only (cron should be ~9 AM, not 6 PM). The wind-down is a separate scheduled task.

---

### Task 5: End-to-End Walkthrough

**Files:**
- None — manual verification

- [ ] **Step 1: Simulate the wind-down flow**

Manually invoke the wind-down skill by running through the 3 steps:
1. Query completed tasks for today — verify the curl command returns valid JSON
2. Query tomorrow's tasks — verify the curl command returns valid JSON
3. Test saving a journal note — insert a test note with `source: "wind-down"` and verify it appears in Supabase

```bash
source "/Users/brianthompson/Documents/01 Projects/Claude Projects/Samaritan/.env" 2>/dev/null
HEADERS=(-H "apikey: ${SUPABASE_ANON_KEY}" -H "Authorization: Bearer ${SUPABASE_ANON_KEY}")
TODAY=$(TZ=America/Chicago date +%Y-%m-%d)

# Test: query completed tasks today
curl -sL "${SUPABASE_URL}/rest/v1/tasks?status=eq.Completed&completed_at=gte.${TODAY}T00:00:00&order=business,completed_at" "${HEADERS[@]}" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'{len(d)} completed tasks today')"

# Test: query tomorrow's tasks
TOMORROW=$(TZ=America/Chicago date -v+1d +%Y-%m-%d)
curl -sL "${SUPABASE_URL}/rest/v1/tasks?due_date=eq.${TOMORROW}&status=eq.Active&order=priority,business" "${HEADERS[@]}" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'{len(d)} tasks due tomorrow')"

# Test: query wind-down notes (should return empty or previous entries)
curl -sL "${SUPABASE_URL}/rest/v1/notes?source=eq.wind-down&order=created_at.desc&limit=1" "${HEADERS[@]}" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'{len(d)} wind-down notes found')"
```

Expected: All three commands return valid JSON with counts.

- [ ] **Step 2: Verify morning briefing integration**

Check that the daily-briefing agent has the wind-down recall step:
```bash
grep -A5 "Last Night" .claude/agents/daily-briefing.md
```

Expected: Shows the Step 1.5 section with the curl query for yesterday's wind-down note.

- [ ] **Step 3: Final commit if any cleanup needed**

```bash
git status
# If any uncommitted changes:
git add -A && git commit -m "chore: wind-down implementation cleanup"
```
