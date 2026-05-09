---
name: scan-inbox
description: Scan Gmail inbox for actionable emails and suggest tasks. Deduplicates automatically.
user-invocable: true
---

# /scan-inbox — Email Task Suggestion Scanner

Scan the finance@happypupmanor.com inbox for actionable emails and suggest tasks. Never suggest the same email twice.

All paths are relative to the Obsidian vault root. Suggestion files live under `Samaritan/Email/`.

---

## Step 1: Load Skip Rules

Call `obsidian_read_note(filePath: "Samaritan/Config/email-rules.md")`.

Parse the markdown table to extract sender patterns to skip. Each row has: `from_pattern | action | reason`. Collect all patterns where action is `skip`.

---

## Step 2: Load Already-Seen Message IDs

Call `obsidian_list_notes(dirPath: "Samaritan/Email", nameRegexFilter: "ES-\\d+")` to get all existing suggestion files.

For each returned file, call `obsidian_manage_frontmatter(filePath: PATH, operation: "get", key: "message_id")` to retrieve its message_id.

Collect all seen message_ids into a set for dedup.

> **Optimization:** If there are many files (20+), use `obsidian_global_search(query: "message_id:", searchInPath: "Samaritan/Email")` instead — parse message_id values from the returned snippets.

---

## Step 3: Scan Gmail

Call `gmail_search_messages(q: "to:finance@happypupmanor.com newer_than:3d", maxResults: 20)`.

---

## Step 4: Filter and Suggest

For each email:
1. **Skip** if message_id is in the seen set (dedup)
2. **Skip** if sender domain matches any pattern from email-rules.md
3. **Skip** non-actionable categories: security alerts, promotional, social

For remaining emails, determine:
- `suggested_title`: What task would this email create?
- `suggested_business`: Infer from sender/subject (Walmart/Amazon/TCGplayer → Reseller Business, HPM staff → Happy Pup Manor, else → Personal)
- `suggested_priority`: High for orders/cancellations/urgent, Medium for general, Low for FYI
- `action_url`: Direct link to take action (see table below)
- `from_domain`: Extract domain from sender email

## Known Action URLs

| Sender Pattern | Action URL |
|---------------|------------|
| Walmart Marketplace | https://seller.walmart.com/orders |
| Amazon Seller | https://sellercentral.amazon.com/orders-v3 |
| TCGplayer | https://store.tcgplayer.com/admin/orders |
| Synchrony/OnePay | https://www.mysynchrony.com |
| US Bank | https://www.usbank.com/auth/login |
| Anthropic | https://console.anthropic.com/settings/billing |
| Google (security) | SKIP |
| LinkedIn | SKIP |
| Patreon | SKIP |

---

## Step 5: Write Suggestion Files

**Step 5a — Get next suggestion ID**
Call `obsidian_list_notes(dirPath: "Samaritan/Email", nameRegexFilter: "ES-\\d+")`. Find the highest ES-XXX number and add 1. If none, start at ES-001.

**Step 5b — For each actionable email, create a suggestion file**
Call `obsidian_update_note` with:
- `targetType`: `"filepath"`
- `targetIdentifier`: `"Samaritan/Email/ES-XXX SUGGESTED_TITLE.md"`
- `wholeFileMode`: `true`
- `content`:
```
---
suggestion_id: ES-XXX
message_id: MESSAGE_ID
from_address: "FROM_ADDRESS"
from_domain: FROM_DOMAIN
subject: "SUBJECT"
received_at: YYYY-MM-DD
suggested_title: "SUGGESTED_TITLE"
suggested_business: SUGGESTED_BUSINESS
suggested_priority: SUGGESTED_PRIORITY
action_url: ACTION_URL
status: pending
---

# SUGGESTED_TITLE

**From:** FROM_ADDRESS
**Subject:** SUBJECT
**Received:** YYYY-MM-DD
**Status:** pending
```

Increment ES-XXX for each new file.

---

## Step 6: Report

```
📧 Inbox scanned — X new actionable emails found:
1. [High] Ship Walmart order — from Walmart Marketplace
2. [Medium] Review TCGplayer sale — from TCGplayer

(Y emails skipped: already seen or from blocked senders)
```

---

## Auto-Learn

After each scan, check for sender domains that have been dismissed 3+ times.

Call `obsidian_global_search(query: "status: dismissed", searchInPath: "Samaritan/Email")`. From the results, collect `from_domain` values (read each matched file's frontmatter via `obsidian_manage_frontmatter` if needed). Count occurrences per domain.

For any domain with 3+ dismissals that isn't already in email-rules.md, append a new row to the rules file:

Call `obsidian_update_note` with:
- `targetType`: `"filepath"`
- `targetIdentifier`: `"Samaritan/Config/email-rules.md"`
- `wholeFileMode`: `false`
- `content`: `"\n| DOMAIN | skip | Auto-learned: dismissed Nx |"`

---

## Approving / Dismissing Suggestions

**To approve** (create a task from it):
1. Read the suggestion file with `obsidian_read_note`
2. Create a task using the catch skill task-write pattern with `suggested_title`, `suggested_business`, `suggested_priority`
3. Update status: call `obsidian_manage_frontmatter(filePath: PATH, operation: "set", key: "status", value: "approved")`

**To dismiss:**
Call `obsidian_manage_frontmatter(filePath: PATH, operation: "set", key: "status", value: "dismissed")`
