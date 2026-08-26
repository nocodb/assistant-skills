## Instructions

You are writing a **3P update** — Progress, Plans, Problems. The audience is
leadership and adjacent teams: people with *some* context but not a lot. It must
be readable in 30–60 seconds.

Three sections, always in this order:

1. **Progress** — what actually landed in the period. Shipped, closed, merged,
   signed. Not "worked on".
2. **Plans** — what the team is on next period. Top priorities only.
3. **Problems** — what is slowing the team down. Blockers, missing people, a
   dependency that slipped, a deal that fell through.

Granularity scales with scope. A single squad's 3P is "shipped the import
rewrite"; the whole company's is "closed 10 deals, hired 20 people".

Before writing, you need the **team** and the **period**. In an interactive chat,
ask once if the team isn't obvious. On a triggered run, derive both and state
what you assumed.

## Gathering

Read the tracker, don't ask for the contents.

```
describe_table(table_name: "Tasks")
```

- **Progress** — closed in the period:
  `(Status,eq,Done)~and(Updated At,gte,oneWeekAgo)`
- **Plans** — open and prioritised for next period:
  `(Status,in,Todo,In Progress)~and(Due Date,lte,oneWeekFromNow)`
- **Problems** — blocked, overdue, or unowned:
  `(Status,eq,Blocked)` · `(Due Date,lt,today)~and(Status,neq,Done)` ·
  `(Owner,blank)~and(Status,neq,Done)`

Then `aggregate` for the counts you'll quote (`count`, and `sum` on points or
value if the table has one), and `get_document` on last week's update to check
what was promised. **A plan from last week that didn't land is a Problem**, not a
silently dropped line.

## Formatting

Strict. Never deviate, never add sections. Pick one emoji that fits the team.

```
[emoji] [Team Name] — [Mon D]–[Mon D]

Progress: [1–3 sentences]
Plans: [1–3 sentences]
Problems: [1–3 sentences]
```

Each section is 1–3 sentences, matter-of-fact, metrics where they exist. No
bullets, no sub-headings, no prose warm-up.

## Example

```
🚚 Platform — Aug 19–26

Progress: Shipped the import rewrite (14 tasks closed, 3 carried from last week) and cut p95 import time from 41s to 9s. Telegram channel delivery went live for 6 workspaces.
Plans: Land schema-lock for managed apps, and start the audit-log retention work — both due Sep 2.
Problems: Schema-lock is blocked on the migration review that has sat unassigned for 9 days. Two of five engineers are on the incident rota this week, so capacity is roughly 60%.
```

## Guidelines

- **"Progress" means finished.** In-flight work belongs in Plans.
- **Carried-over work is worth naming**, once: "3 carried from last week".
- **Quote the blocker, don't theorise.** If a Blocked task has no note, write
  "no reason recorded" — that itself is the finding.
- **Nothing to report is a valid section.** "Problems: Nothing blocking." Do not
  manufacture a problem to fill the slot.
- **Never pad with adjectives.** "Shipped the import rewrite" not "successfully
  delivered the highly anticipated import rewrite".
- Over a channel, drop the code fence and send the five lines as plain text.
