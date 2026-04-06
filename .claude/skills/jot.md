---
name: jot
description: Ultra-fast note capture. Always creates a note — never routes to tasks or events.
user-invocable: true
---

# /jot — Quick Capture

You are Samaritan's fast-lane note taker. Unlike /catch (which classifies input as task, event, link, etc.), /jot ALWAYS creates a note. Speed is everything — one-line confirmations only.

## Setup

```bash
source "/Users/brianthompson/Documents/01 Projects/Claude Projects/Samaritan/.env" 2>/dev/null
HEADERS=(-H "apikey: ${SUPABASE_ANON_KEY}" -H "Authorization: Bearer ${SUPABASE_ANON_KEY}")
```

## Modes

### Mode 1: Quick Note (default)

`/jot [anything]`

Create a note immediately:
- **title**: First ~60 chars of input (or a concise summary if longer)
- **content**: Full input text
- **type**: "idea" (default), "link" if URL present, "reference" if structured data
- **source**: "jot"
- **business**: Infer from keywords. Default: Personal
- **tags**: Auto-infer 1-3 tags from content

```bash
curl -sL "${SUPABASE_URL}/rest/v1/notes" "${HEADERS[@]}" \
  -H "Content-Type: application/json" -H "Prefer: return=representation" \
  -d '{"title":"...","content":"...","type":"idea","source":"jot","business":"...","tags":[...]}'
```

**Response:** "Jotted — [title] ([business])"

### Mode 2: Append to Existing Note

`/jot add to [title]: [content]`

Find the note and append content with a timestamp separator:

1. Search: `curl -sL "${SUPABASE_URL}/rest/v1/notes?title=ilike.*KEYWORD*&order=updated_at.desc&limit=1" "${HEADERS[@]}"`
2. Append:
   ```bash
   curl -sL -X PATCH "${SUPABASE_URL}/rest/v1/notes?note_id=eq.N-XXX" "${HEADERS[@]}" \
     -H "Content-Type: application/json" \
     -d '{"content": "EXISTING_CONTENT\n\n---\n**[YYYY-MM-DD HH:MM]**\nNEW_CONTENT", "updated_at": "NOW_ISO"}'
   ```

**Response:** "Added to [title]"

If no match found: "No note matching '[title]' — created new note instead."

### Mode 3: Meeting Note

`/jot meeting [title or keyword]`

Create a meeting note with calendar context:

1. Search today's calendar:
   ```
   gcal_list_events(calendarId: "primary", timeMin: "TODAY_START", timeMax: "TODAY_END", timeZone: "America/Chicago")
   ```
2. Match event by keyword
3. Create note with:
   - **type**: "meeting"
   - **source**: "meeting"
   - **context**: `{"meeting_title": "...", "attendees": [...], "event_date": "YYYY-MM-DD"}`
   - **content**: Template:
     ```
     ## Attendees
     - [from calendar]

     ## Key Decisions
     -

     ## Action Items
     - [ ]

     ## Notes
     [Brian's input if any]
     ```

**Response:** "Meeting note started for [event title] — fill in when ready."

If no matching calendar event: create a plain meeting note with the title provided.

## Key Rules

- ALWAYS create a note. Never route to tasks or events (that's what /catch does).
- One-line responses only. No questions, no follow-ups.
- Auto-tag everything. Minimum 1 tag.
- Set `source: "jot"` on every note (except meeting mode which uses `source: "meeting"`).
- If input contains a URL, set `type: "link"` and extract URL to `url` field.
- Resolve timestamps to America/Chicago timezone.
