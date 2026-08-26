---
name: internal-comms
description: Writes internal communications from what is actually in the base — weekly 3P updates, project status rollups, incident updates, announcements — in a strict house format, published as a NocoDocs document or sent over a channel. Use whenever the user asks to write, draft, or send an update, status report, leadership summary, standup note, incident update, changelog or announcement. Triggers include "weekly update", "3P", "status report", "write this up for the team", "post an update". Do NOT use for an analytical report with charts and tables (see base-report) or for a slide deck (see pptx-deck).
---

# Internal comms

An internal update is read in under a minute by someone with partial context.
Its job is to tell them what changed, what is next, and what needs a decision —
**from the records, not from memory.**

Every number in an update comes from a tool call. If a field is blank, that is
"unknown", never zero.

## How to use this skill

1. **Identify the type** from the request.
2. **Load the matching guideline** from `examples/` and follow it exactly — the
   formats are strict on purpose, so a reader who sees these weekly can skim
   them.

   | Ask | File |
   |---|---|
   | Weekly team update, standup rollup, "3P" | `examples/3p-updates.md` |
   | Project or portfolio status for leadership | `examples/project-status.md` |
   | Something is broken or degraded right now | `examples/incident-update.md` |
   | Announcement, changelog, anything else | `examples/general-comms.md` |

3. **Gather from the base** before writing (see below).
4. **Publish** as a document or send to a channel (see below).

If the request matches nothing here, use `general-comms.md` rather than inventing
a format.

## Gathering from the base

The base is the source of truth. Do not ask the user for numbers you can read.

- `list_tables` / `describe_table` — find the tracker and learn its fields before
  querying. Field names vary per base; never assume "Status" or "Owner" exists.
- `query_records` — the rows behind the narrative. `limit` caps at 100; page with
  `offset` and never restart at 0 on a follow-up. Pass `fields` to keep wide
  tables from flooding the response.
- `aggregate` — counts and totals. `count`, `count_unique`, `sum`, `avg`,
  `earliest_date`/`latest_date`.
- `list_documents` / `get_document` — prior updates. **Read last period's update
  before writing this one**: it tells you what was promised, which is most of
  what makes an update useful.

Scoping a period, with a `where` clause:

```
(Updated At,gte,2026-08-19)~and(Updated At,lte,2026-08-26)
```

Useful date sub-operators, so you don't hardcode dates on a recurring run:
`(Due Date,eq,today)`, `(Updated At,gte,oneWeekAgo)`, `(Close Date,lte,oneWeekFromNow)`.

## Publishing

**As a document** — the default for anything with structure, and it gives the
next run something to read:

```
create_document(
  title: "Platform — weekly update, 26 Aug 2026",
  content: "<markdown>",
  parent_document_name: "Weekly updates"
)
```

NocoDocs markdown supports:

- `::: callout note|warning|tip|important` — one per update at most, for the thing
  that needs a decision.
- `::: columns {ratio=50}` … `::: column` … `:::` — two columns, e.g. Progress
  beside Plans.

**Over a channel** (Telegram and similar) the rules change:

- **No markdown tables** — they arrive as unaligned pipes. Use short lines with a
  leading `•`.
- **No callouts or column blocks** — they render as literal `:::`.
- Bold sparingly, links inline, and keep it to a screen. If it needs more,
  publish the document and send a two-line summary plus the doc title.

## When a trigger started the run

A cron or record trigger means **nobody is waiting to answer a question**:

- Never ask for the team name or the period. Derive the period from the trigger
  time; derive the team from the base or the table you were pointed at.
- If something is genuinely missing, make the reasonable assumption and state it
  in one line at the end: "Assumed the Platform team from base name; no Team
  field on Tasks."
- Your final message is the run's record. Make it the update itself, not a
  description of having written one.

## Guidelines

- **Names, not IDs.** "Migrate billing to v3", never `rec_a91f`.
- **Every metric traceable.** If you didn't `aggregate` or `query_records` it, it
  doesn't go in.
- **Say what you couldn't see.** "Three tasks have no owner set" is information;
  silently omitting them is not.
- **No filler.** Cut "we continued to make progress on", "as always", "exciting".
  If a section has nothing real, write "Nothing this week" and move on.
- **Don't diagnose from a status field.** A task flipping to Blocked tells you it
  is blocked, not why. Quote the note if there is one; otherwise say the reason
  isn't recorded.
- **Never invent a person's words.** Attribute only what a record actually
  contains.
