## Instructions

The fallback for any internal communication that isn't a 3P, a status rollup or
an incident update: announcements, changelogs, a decision write-up, a heads-up
about a change, a reply to a recurring question.

There is no strict template here, so the discipline has to come from structure.
Three questions decide the shape:

1. **What does the reader need to do?** Nothing / know something / act by a date.
2. **How much context do they have?** Adjacent team vs. whole company.
3. **Is this durable or disposable?** A decision record is read in six months; a
   "deploying at 4pm" note is dead by 5.

## Shape

**Always** lead with the conclusion. Never open with background.

```
[Title — states the thing, not the topic]

[One or two sentences: what changed and what it means for the reader.]

[Detail — only what a reader needs. Bullets if it's a list of changes.]

[What to do, if anything, and by when.]
```

Then, by type:

- **Announcement / change** — what changed, who is affected, what breaks, when.
  If nothing breaks, say "no action needed" explicitly; readers assume the worst.
- **Changelog** — grouped by audience impact, not by component. "Faster imports"
  beats "refactored the storage adapter". Skip internal refactors entirely unless
  they change behaviour.
- **Decision record** — the decision, the options considered, why this one, and
  what would make you revisit it. This is the one case where background belongs
  in the body, because it is the durable value.
- **Recurring question** — answer first, then the reasoning. If it's asked
  repeatedly, publish it as a document and link it, rather than answering again.

## Gathering

Whatever the subject is, read it before writing about it:

- `query_records` on the tracker for the shipped items behind a changelog:
  `(Status,eq,Done)~and(Updated At,gte,oneWeekAgo)`
- `list_documents` / `get_document` — has this been announced already, or is
  there a decision doc to link rather than restate?
- `aggregate` for any number you plan to quote.

## Length

| Type | Target |
|---|---|
| Change / heads-up | Under 100 words |
| Changelog | One line per item, grouped |
| Decision record | As long as the reasoning needs — but the decision is in the first sentence |
| Recurring answer | Answer in one sentence, then detail |

If a change note runs past 100 words, the extra is almost always background the
reader didn't ask for.

## Example

```
Imports now handle files up to 200MB

The import pipeline was rewritten this week. Files up to 200MB now import in a single pass, and p95 import time dropped from 41s to 9s.

- Column mapping is remembered per table between imports
- Excel files with multiple sheets now prompt for which sheet
- Files over 200MB still need splitting

No action needed — existing imports and saved mappings keep working.
```

## Guidelines

- **Title states the thing.** "Imports now handle files up to 200MB", not "Import
  pipeline update".
- **"No action needed" is worth saying** when it's true. Its absence is read as
  action being needed.
- **Cut every sentence that only signals effort.** "The team has been working
  hard on", "we're excited to announce", "as part of our ongoing commitment".
- **Link, don't restate.** If a decision doc exists, name and link it rather than
  summarising it badly.
- **Group a changelog by what the reader notices.** Internal refactors with no
  behaviour change don't belong in an internal comm at all.
- **Never announce something you haven't confirmed shipped.** A task marked Done
  is not the same as deployed; check before you tell the company.
- If it's durable, publish it as a document so it can be linked later. If it's
  disposable, a channel message is enough.
