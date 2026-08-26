---
name: csv-analysis
description: Answers a business question from an uploaded spreadsheet (CSV, Excel, JSON) or a NocoDB export — what changed, what is driving it, what to do about it — and replies with the finding, not a profile of the file. Use whenever the user attaches tabular data and asks anything about it, including a bare "what do you make of this?" or "any insights?". Do NOT use to describe a file's structure back to the user, and do NOT use for a spreadsheet they want loaded into a table — that is import_file.
---

# Spreadsheet analysis

Someone attaches a file because they want to know something. **Row counts,
column dtypes, null percentages and `describe()` output are not that
something.** Profile the file to avoid computing nonsense, then throw the
profile away and answer the question.

> Script paths below are relative to this skill's directory — the absolute path is
> the one `load_skill` reported, e.g. `/home/user/skills/csv-analysis`.

## How to use this skill

### 1. Decide what is being asked

If the user named a question, answer that one. If they said "have a look" or
"any insights", the question is implicit and you have to choose it. Pick the one
a person who owns this data would care about:

- What is the largest contributor, and how concentrated is it?
- What changed over time, and where did the change come from?
- Which segment behaves differently from the rest?
- What looks wrong or at risk?

Don't answer all four. Pick the one the data best supports, lead with it, and
offer the others in a closing line.

### 2. Orient yourself — privately

Uploaded files land in `/home/user/<filename>`. The compute is shared across
calls and turns, so load once and reuse.

```bash
python3 /home/user/skills/csv-analysis/scripts/profile_csv.py /home/user/data.csv
```

This exists so you don't multiply a string by a string. **Its output is for you.**
Never paste it, summarise it, or turn it into a section. Specifically watch for:

- Numeric-looking columns parsed as strings — currency symbols, thousands
  separators, percent signs. Clean before you aggregate.
- NocoDB link/lookup columns exported as stringified JSON or comma-joined text.
  Check one sample row before treating a column as scalar.
- Dates as strings. Parse them before any time comparison.

### 3. Find the answer

```python
import pandas as pd
df = pd.read_csv("/home/user/data.csv")

# Clean, then answer. Not the other way round.
df["Amount"] = pd.to_numeric(df["Amount"].astype(str).str.replace(r"[$,]", "", regex=True))
by_segment = df.groupby("Segment")["Amount"].agg(["sum", "count", "mean"])
```

Two habits that separate an answer from a summary:

- **Compare.** A total on its own says nothing. Against last month, against the
  other segments, against the median — now it's a finding.
- **Cut twice.** Slice by one dimension and you get a ranking. Slice by two and
  you find the reason. "EMEA is up" is a ranking; "EMEA is up entirely on two
  partner deals" is the reason.

### 4. Reply with the finding

For most questions the answer belongs **in the chat**, not in a file:

- Lead with the conclusion in one sentence.
- Support it with the two or three numbers that establish it.
- Say what you'd do about it.
- Note what you cleaned or excluded, in one line, only if it moved a number.

Reach for a chart when a shape carries the point better than a number — call
`generate_chart_config` for base tables, or render a PNG with matplotlib for
file data. One chart, not a gallery.

Escalate to a document only if the user asked for one, or the answer genuinely
needs sections and tables — then hand off to
[base-report](../base-report/SKILL.md). Producing an unrequested PDF for a
question that fits in a paragraph is worse than useless: it surfaces as a
download chip the user has to open to learn one sentence.

## Guidelines

- **Never describe the file.** No shape, no dtype table, no missing-value matrix,
  no "your CSV has 14 columns and 1,204 rows".
- **Never report on data you didn't clean.** If a column arrived as a string with
  a `$` in it, fix it before summing — silently producing a wrong total is worse
  than saying you couldn't parse it.
- **Sample large files first**, then confirm the finding on the whole file before
  stating it. Say so if you only sampled.
- **Cite exact values**, not paraphrases from memory. If you computed 31.4%, say
  31.4%, not "about a third".
- **Don't invent causes.** The data shows correlation and concentration; it
  rarely shows why. "Two deals account for the increase" is supported;
  "the campaign worked" usually isn't.
- Encodings: try `utf-8`, fall back to `latin-1`/`cp1252`. Excel via
  `pd.read_excel` (`openpyxl` is installed).
- **Never `pip install`.** `pandas`, `matplotlib`, `seaborn`, `openpyxl` and the
  rest are already there.
