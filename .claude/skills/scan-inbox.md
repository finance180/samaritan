---
name: scan-inbox
description: Scan Gmail inbox for actionable emails and suggest tasks. Deduplicates automatically.
user-invocable: true
---

# /scan-inbox — Email Task Suggestion Scanner

Scan the finance@happypupmanor.com inbox for actionable emails and suggest tasks. Never suggest the same email twice.

## Setup

```bash
source "/Users/brianthompson/Documents/01 Projects/Claude Projects/Samaritan/.env" 2>/dev/null
HEADERS=(-H "apikey: ${SUPABASE_ANON_KEY}" -H "Authorization: Bearer ${SUPABASE_ANON_KEY}")
```

## Step 1: Load Skip Rules

Query senders to skip:
```bash
curl -sL "${SUPABASE_URL}/rest/v1/email_rules?action=eq.skip&select=from_pattern" "${HEADERS[@]}"
```

## Step 2: Load Already-Seen Message IDs

Get all message_ids already in email_suggestions (any status):
```bash
curl -sL "${SUPABASE_URL}/rest/v1/email_suggestions?select=message_id" "${HEADERS[@]}"
```

## Step 3: Scan Gmail

Use `gmail_search_messages(q: "to:finance@happypupmanor.com newer_than:3d", maxResults: 20)`

## Step 4: Filter and Suggest

For each email:
1. **Skip** if message_id already exists in email_suggestions (dedup)
2. **Skip** if sender domain matches any from_pattern in email_rules
3. **Skip** non-actionable categories: security alerts, promotional, social
4. For remaining emails, determine:
   - **suggested_title**: What task would this email create?
   - **suggested_business**: Infer from sender/subject (Walmart/Amazon/TCGplayer → Reseller, HPM staff → Happy Pup Manor, etc.)
   - **suggested_priority**: High for orders/cancellations/urgent, Medium for general, Low for FYI
   - **action_url**: Direct link to take action (see known URLs below)
   - **from_domain**: Extract domain from sender email

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

## Step 5: Insert Suggestions

For each actionable email, insert with ON CONFLICT DO NOTHING (message_id is unique):
```bash
curl -sL "${SUPABASE_URL}/rest/v1/email_suggestions" "${HEADERS[@]}" \
  -H "Content-Type: application/json" -H "Prefer: return=representation" \
  -H "Prefer: resolution=ignore-duplicates" \
  -d '{"message_id":"...","from_address":"...","subject":"...","received_at":"...","suggested_title":"...","suggested_business":"...","suggested_priority":"...","action_url":"...","from_domain":"...","status":"pending"}'
```

Use the header `Prefer: resolution=ignore-duplicates` to silently skip duplicates.

## Step 6: Report

```
📧 Inbox scanned — X new actionable emails found:
1. [High] Ship Walmart order — from Walmart Marketplace
2. [Medium] Review TCGplayer sale — from TCGplayer

(Y emails skipped: already seen or from blocked senders)

Open the EMAIL tab in Samaritan to approve or dismiss.
```

## Auto-Learn

When the morning briefing or this skill runs, it also checks:
- Any sender dismissed 3+ times → auto-add to email_rules with action='skip'
