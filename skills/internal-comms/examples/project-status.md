## Instructions

You are writing a **project status rollup** for leadership. One line per project,
each carrying a colour, a one-sentence "so what", and — where the colour is not
green — the decision or help needed.

The reader is scanning for exceptions. Green projects exist so the reader knows
they were checked, not to be read about.

Colour is assigned from evidence, never from vibe:

| Colour | Means | Assign when |
|---|---|---|
| 🟢 Green | On track | No overdue tasks, no blockers, dates unchanged since last update |
| 🟡 Amber | At risk | Slipping but recoverable — an overdue task, a date moved once, a blocker with an owner |
| 🔴 Red | Off track | Will miss unless something changes — date moved twice, a blocker with no owner, or a dependency gone red |
| ⚪ Unknown | No signal | Nothing updated in the period. Say so; do not guess green |

**⚪ is a real status and the most important one to report honestly.** A project
with no activity is not a project that is fine.

## Gathering

```
describe_table(table_name: "Projects")
```

Per project, you need: current phase or status, target date, owner, and whether
anything moved. Then for each one:

- Overdue work: `(Due Date,lt,today)~and(Status,neq,Done)`
- Blockers: `(Status,eq,Blocked)`
- Recent activity: `(Updated At,gte,oneWeekAgo)` — an empty result is what makes
  it ⚪
- Unowned work: `(Owner,blank)~and(Status,neq,Done)`

Read last period's rollup with `get_document`. **The date-moved count is the
strongest red signal you have**, and it only exists by comparing to the previous
update. If there is no previous update, say the colours are a first baseline.

## Formatting

```
[emoji] Project status — [date]

🔴 [Project] — [one sentence: what is wrong and the consequence]
   Needs: [the specific decision or resource, and from whom]

🟡 [Project] — [one sentence]
   Needs: [only if something is actually needed]

🟢 [Project] — [one sentence: what landed or what is next]

⚪ [Project] — no updates since [date]

[Optional single callout if one item needs a decision this week]
```

Order red → amber → green → unknown. Never alphabetically, never by project id.

## Example

```
🧭 Project status — 26 Aug 2026

🔴 Billing v3 — Launch date has moved twice (Sep 5 → Sep 19 → Oct 3); the migration review has been unassigned for 9 days.
   Needs: a reviewer named by Thu, or the Oct 3 date goes too.

🟡 Audit log retention — Two tasks overdue by 4 days, both on one engineer who is on the incident rota.
   Needs: nothing yet — re-check next week.

🟢 Telegram channels — Shipped to 6 workspaces; next is Slack, due Sep 12.

⚪ Data residency — no updates since Aug 5.
```

## Guidelines

- **The "so what" is the sentence, not the status.** "Billing v3 is Amber" says
  nothing; "launch has moved twice and the reviewer is unassigned" does.
- **`Needs:` names a person or a role and a date.** "Needs: exec decision" is not
  a need, it is a shrug.
- **Never upgrade a colour to be reassuring.** If the evidence says red, it is
  red. Softening it is the one failure that makes the whole rollup worthless.
- **Never downgrade to look diligent** either. Two overdue tasks on a 300-task
  project is not red.
- **One callout maximum**, for the single thing that needs a decision this week.
  Two callouts means neither gets read.
- If a project has no target date recorded, say so — an undated project cannot be
  on track.
