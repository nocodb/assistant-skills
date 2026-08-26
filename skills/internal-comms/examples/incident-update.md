## Instructions

You are writing an **incident update** — something is broken or degraded *now*.
This is the one format where being wrong is worse than being late, and where
saying "we don't know yet" is the correct content.

The reader wants four things, in this order: what is broken, who it affects,
what is being done, when they'll hear next. Everything else can wait.

**Impact before cause.** Nobody reading an incident update needs the root cause
in the first update; they need to know whether their customers are affected.

Three kinds of update, same format:

- **Initial** — first notice. Impact and next-update time are mandatory; cause is
  almost always "under investigation".
- **Ongoing** — what changed since the last one. If nothing changed, say that.
- **Resolved** — what fixed it, when it ended, and what follows up.

## Gathering

```
describe_table(table_name: "Incidents")
```

Read the incident record for: severity, start time, affected component,
current owner, and the notes trail. Then:

- The notes or comments on the record — that is the timeline, and its **last
  entry timestamp** tells you how stale your information is.
- `list_document_comments` / `get_document` if the team keeps a live doc.
- Related open work: `(Status,neq,Done)~and(Incident,eq,<name>)` if a link exists.

**If the record's last update is older than your next-update promise, say so.**
"Last confirmed status 40 minutes ago" is honest; presenting stale state as
current is how an incident update does damage.

## Formatting

```
[🔴 INVESTIGATING | 🟡 MONITORING | 🟢 RESOLVED] [Component] — [HH:MM TZ]

Impact: [who is affected and how — in the user's terms, not the system's]
Status: [what is currently true]
Action: [what is being done, and by whom]
Next update: [time, or "on resolution"]
```

For a resolved update, replace `Action`/`Next update` with:

```
Duration: [start – end, total]
Cause: [one sentence, or "under investigation — postmortem to follow"]
Follow-up: [the tracked item, by name]
```

No prose paragraphs, no apology paragraph, no "we take reliability seriously".

## Example

```
🔴 INVESTIGATING Import pipeline — 14:20 UTC

Impact: CSV and Excel imports are failing for all workspaces. Records already imported are unaffected; nothing has been lost.
Status: Failures began 13:52 UTC. Every import since returns an error at the upload step. Cause not yet identified.
Action: Priya is rolling back the 13:45 deploy; Sam is checking storage-adapter errors in parallel.
Next update: 15:00 UTC, or sooner if the rollback resolves it.
```

Resolved:

```
🟢 RESOLVED Import pipeline — 15:12 UTC

Impact: CSV and Excel imports failed for all workspaces. No data was lost.
Duration: 13:52 – 15:04 UTC, 72 minutes.
Cause: The 13:45 deploy changed the storage-adapter stream signature; the import worker was not redeployed with it.
Follow-up: "Add import smoke test to deploy gate" on the Platform board.
```

## Guidelines

- **Never speculate on cause in writing.** "Under investigation" costs nothing;
  a wrong cause gets quoted back for weeks.
- **State what is *not* affected.** It is usually the most reassuring true thing
  you can say, and it stops the reader inventing a worse scenario.
- **Impact in the user's terms.** "Imports are failing", not "the worker queue is
  saturated".
- **Always commit to a next-update time**, even when there is nothing to say.
  Silence reads as things getting worse.
- **Name people for actions, not for blame.** "Priya is rolling back the deploy",
  never "Priya's deploy broke it".
- **Never say "resolved" from a status field alone.** Resolved means someone
  confirmed the user-facing symptom is gone. If the record just flipped to Done,
  write MONITORING.
- **Timestamps carry a timezone.** Every one, every time.
- On a triggered run with a stale record, publish what you have with the
  as-of time stated — do not skip the update.
