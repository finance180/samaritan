# Evening Wind-Down Ritual — Design Spec

## Overview

A guided 3-step evening check-in scheduled at 6:00 PM CT daily that replaces the current barebones evening review. Transforms "here are your outstanding tasks" into a structured wind-down: celebrate wins, set tomorrow's priorities, and clear open loops from your head.

## Architecture

- **Skill file**: `.claude/skills/wind-down.md` — contains the guided flow logic
- **Scheduled task**: Updates the existing `daily-briefing` evening check-in to invoke the wind-down skill instead of the basic outstanding-tasks review
- **Storage**: Daily journal notes saved to Supabase `notes` table
- **No new database tables or columns required**

## Step 1: Quick Wins Log

1. Query completed tasks today: `status=Completed`, `completed_at` >= today's date (America/Chicago)
2. Present them grouped by business (Happy Pup Manor, Reseller Business, Personal)
3. Ask Brian to pick his **top 3 wins** — can be from the completed list or freeform (e.g., "good supplier call")
4. Save as a journal note:
   - `title`: "Wind-Down — YYYY-MM-DD"
   - `type`: "text"
   - `source`: "wind-down"
   - `tags`: ["journal", "wins", "wind-down", "YYYY-MM-DD"]
   - `content`: Markdown with wins section

## Step 2: Tomorrow's Top 3

1. Query upcoming tasks:
   - Due tomorrow (`due_date = tomorrow`)
   - Overdue (`due_date < today`, `status = Active`)
   - High priority upcoming (next 3 days)
2. Present as a numbered list grouped by business
3. Ask Brian to pick **3 priorities for tomorrow**
4. Append to the same journal note under a "Tomorrow's Top 3" section
5. The morning briefing leads with these 3 tasks (query notes with `source=wind-down` and today's date tag)

## Step 3: Open Loops Brain Dump

1. Prompt: "Anything still bouncing around in your head? List them out — I'll sort them."
2. Each item gets triaged using `/catch` classification logic:
   - Task → create in Supabase with inferred business/priority
   - Event → suggest calendar entry
   - Idea/Note → save as note
3. Confirmation summary: "Captured X items — Y tasks, Z notes. Your head is clear."
4. Append capture summary to the journal note

## Journal Note Structure

```markdown
# Wind-Down — 2026-04-07

## Today's Wins
1. Closed the Hasbro compliance issue [Reseller]
2. Onboarded new grooming client [HPM]
3. Finally organized the garage [Personal]

## Tomorrow's Top 3
1. [High] Submit CPC documentation — Reseller Business
2. [Medium] Review staff schedule for next week — Happy Pup Manor
3. [Medium] Schedule dentist appointment — Personal

## Open Loops Captured
- Created task: "Call supplier about Q3 pricing" (Reseller, Medium)
- Created note: "Idea for weekend kennel promo" (HPM, idea)
- 2 items captured, head clear.
```

## Scheduling

- **Time**: 6:00 PM CT daily
- **Mechanism**: Update the existing evening check-in in `daily-briefing.md` to invoke the wind-down skill
- **Fallback**: If Brian doesn't respond to a step, skip it gracefully and move to the next

## Integration with Morning Briefing

The morning briefing (9 AM) adds a new step after the journal prompt:

1. Query last night's wind-down note (`source=wind-down`, yesterday's date tag)
2. If found, lead with "Last night you set these 3 priorities:" and list them
3. Show these before the full task list so Brian starts the day focused

## Success Criteria

- Evening check-in feels like a ritual, not a chore
- Brian wakes up knowing his top 3 without checking anything
- Open loops don't stay in his head overnight
- Wins are logged for weekly review visibility
