---
name: base-report
description: Answers a business question from NocoDB records or an uploaded spreadsheet and writes the answer up as a typeset PDF — KPI band, narrative, tables and charts, compiled with XeLaTeX. Use when the user asks for a report, review, board pack, monthly/quarterly summary, or "send me a PDF" of their data. Triggers include "monthly report", "quarterly review", "pipeline report", "write this up as a PDF". Do NOT use when the answer is a sentence or a single table — say it in chat instead; and do NOT use for slide decks (see pptx-deck).
---

# Base report

**A report answers a question about the business. It is never a description of the
data.** Row counts, column types, missing-value percentages, "Prepared from
deals.csv" — none of that belongs in something a person reads. Find the answer
first; the PDF is just how you hand it over.

> Script paths below are relative to this skill's directory — the absolute path is
> the one `load_skill` reported, e.g. `/home/user/skills/base-report`.

## How to use this skill

### 1. Work out what the question actually is

"Give me a report on the pipeline" is not a question — it's a request for one to
be found. Before pulling data, decide what a reader would *do* differently after
reading this. Usually one of:

- Is the number going the right way, and why?
- What changed since last period, and what caused it?
- What is stuck, and who owns it?
- Where should the next unit of effort go?

If the request is genuinely ambiguous about the period or the entity ("which
quarter?", "all regions or EMEA?"), ask **one** question. Otherwise pick the
likeliest reading and say what you assumed.

### 2. Get the numbers

- `aggregate` for the headline figures — `sum`, `avg`, `count`, `count_unique`,
  `earliest_date`/`latest_date`.
- `query_records` for the rows a table or chart needs. `limit` caps at 100; page
  with `offset` and never restart at 0 on a follow-up.
- Scope with `where`, e.g. `(Close Date,gte,2026-07-01)~and(Close Date,lte,2026-09-30)`.
- Compare against something. A number with no comparison is not a finding — pull
  the prior period too.

For an uploaded spreadsheet, load it in `execute_code` and answer the question
from the dataframe. **Profiling is for your eyes only**: check dtypes and nulls
so you don't compute nonsense, then throw that away — it never reaches the
report.

### 3. Sanity-check before you publish a number

Data defects don't matter in the abstract; they matter when they make a figure
wrong. Three stage spellings turn a four-slice chart into seven. Duplicate rows
inflate a total. Run this over the records **you are about to report on**:

```bash
python3 /home/user/skills/base-report/scripts/sanity_check.py \
  --records /tmp/deals.json --unique "Name" --date-fields "Close Date"
```

It flags duplicates, values that differ only in case or spacing, unparseable
dates and numeric outliers, naming the record ids. Then:

- **If it changes a number you were going to publish**, fix or exclude, and note
  it in one line: "Two duplicate Initech deals excluded."
- **If it doesn't**, say nothing. A hygiene appendix is the file talking about
  itself again.
- **Never publish the raw check output.** It is a guard, not a section.

### 4. Charts in `/tmp`, embedded

Pick the chart from the question, never from column position: trend over time →
line; compare categories → bar; share of a whole (≤8 slices) → pie.

```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(7, 3.2))
ax.bar(stages, values, color="#2952cc")
ax.set_ylabel("Value ($k)")
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
fig.tight_layout()
fig.savefig("/tmp/stage_value.png", dpi=200)
```

Never leave a loose PNG in `/home/user/outputs/` — each one surfaces as its own
download chip. Charts belong *inside* the PDF.

### 5. Write the spec

A JSON file that only `scripts/build_report.py` reads. Every string is plain
text; the script handles LaTeX escaping, so don't escape anything yourself.

**The KPI band and the first section carry the answer.** If a reader stops after
the first page they should already know the conclusion.

```json
{
  "title": "Q3 Pipeline Review",
  "subtitle": "Deals · 1 Jul – 30 Sep 2026",
  "kpis": [
    { "label": "Open pipeline", "value": "$2.4M", "note": "+18% vs Q2" },
    { "label": "Win rate", "value": "31%", "note": "24 of 78 closed" }
  ],
  "sections": [
    {
      "heading": "Inbound is winning volume and losing deals",
      "body": "Inbound sourced two thirds of new pipeline but converted at 22% against partner-sourced 51%...",
      "table": {
        "caption": "Value by stage",
        "columns": ["Stage", "Deals", "Value"],
        "rows": [["Discovery", "12", "$430k"], ["Proposal", "9", "$1.1M"]]
      },
      "chart": "/tmp/stage_value.png"
    }
  ],
  "recommendations": [
    "Re-qualify the six Proposal deals idle 21+ days — $680k of the commit rests on them."
  ]
}
```

Headings state findings ("Inbound is winning volume and losing deals"), not
topics ("Inbound analysis").

### 6. Compile, then look at it

```bash
python3 /home/user/skills/base-report/scripts/build_report.py \
  --spec /tmp/report.json \
  --out /home/user/outputs/q3-pipeline-review.pdf

pdftoppm -jpeg -r 100 /home/user/outputs/q3-pipeline-review.pdf /tmp/page
ls /tmp/page-*.jpg
```

Read the images. Look for overfull tables, a chart overflowing the text block, an
empty last page. On a LaTeX failure the script prints the relevant log lines —
fix and re-run. Iterating is normal.

## Guidelines

- **Never report on the file.** No row/column counts, dtype tables,
  missing-value matrices, or "Prepared from: deals.csv".
- **Every number comes from a tool call or a dataframe** you actually computed.
  Never carry a figure over from memory or an earlier guess.
- **One request = one file** in `/home/user/outputs/`. Build everything else in
  `/tmp`. Refer to the file by name only in your reply — never an absolute path.
- **Say what you scoped.** If you reported on 300 of 4,000 records, that's the
  first line, not a footnote.
- **Surface the non-obvious.** Cut by more than one dimension — time, segment,
  owner, size — and say what's surprising. A PDF that restates the dashboard
  wasn't worth making.
- **Recommendations name the thing to do.** "Re-qualify the six Proposal deals
  idle 21+ days" beats "improve pipeline hygiene".
- **Never `pip install` or `apt install`.** The toolchain is preinstalled; if an
  import fails, use a different preinstalled library.

## If XeLaTeX isn't available

`build_report.py` needs the nc-chat sandbox image. Where that's missing, build
with ReportLab instead — every rule above about *content* still applies. Two
gotchas worth knowing:

- Never use Unicode subscript/superscript characters in ReportLab text — the
  built-in fonts render them as black boxes. Use `<sub>`/`<super>` tags inside a
  `Paragraph`.
- Render charts to PNG with matplotlib first, then embed via
  `reportlab.platypus.Image("chart.png", width=..., height=...)`.

## What's preinstalled

XeLaTeX (`texlive-full`, `latexmk`), `pylatex`, WeasyPrint + Jinja2,
`reportlab`, `fpdf2`, `pandoc`, headless LibreOffice, `matplotlib`/`seaborn`,
`pandas`, `openpyxl`/`xlsxwriter`, `python-docx`, `python-pptx`,
`pdfplumber`/`pypdf`, `poppler-utils` (`pdftoppm`). Fonts: EB Garamond, Noto
(+ CJK), Liberation, DejaVu, Roboto, Open Sans, Lato, Fira Code.

For an XLSX deliverable, skip the script and use `openpyxl`/`xlsxwriter`
directly — the `outputs/` rules are the same.
