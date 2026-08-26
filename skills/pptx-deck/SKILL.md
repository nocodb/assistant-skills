---
name: pptx-deck
description: Builds a PowerPoint deck that argues a conclusion from NocoDB records or an uploaded spreadsheet — one point per slide, evidence under it. Use when the user asks for a deck, slides, a presentation, or "something I can show the team" built from their data. Triggers include "make a deck", "slides for the board", "presentation on Q3". Do NOT use for a document to be read rather than presented (see base-report), and never build a deck nobody asked for.
---

# PPTX deck

A deck is an argument delivered out loud. **One point per slide, stated in the
slide title, with just enough evidence under it to be believed.** A slide that
shows a table and lets the audience work it out is a slide that failed.

> Script paths below are relative to this skill's directory — the absolute path is
> the one `load_skill` reported, e.g. `/home/user/skills/pptx-deck`.

## How to use this skill

### 1. Decide the argument before opening python-pptx

Write the slide titles first, as full sentences. If they read as a coherent
argument top to bottom, you have a deck. If they read as a list of topics
("Overview", "Data", "Analysis", "Next steps"), you don't — go back to the data.

Good spine:

1. "Q3 landed at $2.4M, 18% ahead of Q2"
2. "All of the growth came from EMEA partner deals"
3. "Inbound tripled in volume and halved in conversion"
4. "Six Proposal deals are carrying $680k with no activity in 21 days"
5. "Rebalance two reps and cap Negotiation at 30 days"

Five to seven slides. A fourteen-slide deck for a fifteen-minute meeting is a
document with the wrong file extension.

### 2. Get the numbers

Same as any analysis: `aggregate` for headlines, `query_records` (page with
`offset`, `limit` caps at 100) for rows, or `pandas` over an uploaded file. Every
figure on a slide must come from something you actually computed.

Check the values before they become a chart — three spellings of one stage turn a
four-bar chart into seven bars, and a duplicate row inflates a total. Fold
case/whitespace variants together and drop duplicates before you plot:

```python
df["Stage"] = df["Stage"].str.strip().str.title()   # "in progress" → "In Progress"
df = df.drop_duplicates(subset=["Name"])
```

If [base-report](../base-report/SKILL.md) is also installed, its
`scripts/sanity_check.py` does this more thoroughly and names the offending
record ids — but don't assume that directory exists; each skill is installed on
its own.

### 3. Build it

For a conventional spine, the bundled script gets you a working deck fast:

```bash
python3 /home/user/skills/pptx-deck/scripts/build_pptx_deck.py \
  /home/user/data.csv --title "Q3 Review" --out /home/user/outputs/q3-review.pptx
```

For anything with a real argument, drive `python-pptx` directly — the script's
default layout can't know what your point is:

```python
from pptx import Presentation
from pptx.util import Inches, Pt

prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[5])   # title only
slide.shapes.title.text = "All of the growth came from EMEA partner deals"
box = slide.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(8.4), Inches(4))
box.text_frame.text = "$940k of the $1.3M added — APAC contracted $210k"
prs.save("/home/user/outputs/q3-review.pptx")
```

Charts: prefer `python-pptx`'s native charts (`slide.shapes.add_chart(...)`) when
the audience may want to edit or re-cut them in PowerPoint. Render with
matplotlib and `add_picture(...)` when you need a shape native charts can't do.

### 4. Look at it before handing it over

```bash
soffice --headless --convert-to pdf --outdir /tmp /home/user/outputs/q3-review.pptx
pdftoppm -jpeg -r 80 /tmp/q3-review.pdf /tmp/slide
ls /tmp/slide-*.jpg
```

Then read the images. Text overflowing its box, a chart squeezed to nothing, a
title wrapping to three lines — all invisible until you look.

## Guidelines

- **The slide title is the point**, not the topic. "Inbound conversion halved"
  not "Inbound analysis".
- **One idea per slide.** If it needs two, it's two slides.
- **Tables are evidence, not content.** Cap at 8–10 rows and say "top 8 of 34"
  when you truncate. A slide that needs 30 rows wants to be a document.
- **Never pick a column by position.** "The first numeric column" is not a
  business decision — choose what the argument needs.
- **No file-about-file slides.** No row counts, no schema, no "data quality"
  slide unless bad data *is* the argument.
- **End on the ask.** The last slide says what should happen next and who does
  it.
- One deck = one `.pptx` in `/home/user/outputs/`. Build intermediates in `/tmp`.
  Refer to it by name only in your reply.
- **Never `pip install`.** `python-pptx`, `matplotlib`, `pandas` and headless
  LibreOffice are all preinstalled.
