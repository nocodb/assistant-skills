---
name: pptx-deck
description: Builds PowerPoint slide decks — e.g. summarizing a NocoDB table export or a CSV analysis — with a title slide, a data table slide, and a chart slide, using python-pptx and matplotlib. Use whenever the user asks to create a PPT/PPTX presentation or slide deck from tabular data.
---

# PPTX Deck Generation

## When to use this skill
- The user asks for a slide deck / PowerPoint / presentation built from a CSV, a NocoDB export, or an analysis
- Often follows [csv-analysis](../csv-analysis/SKILL.md) when the user wants findings turned into slides rather than a PDF ([pdf-report](../pdf-report/SKILL.md) is the PDF equivalent)

## How to use this skill

1. Quick path — build a starter deck directly from a CSV:
   ```bash
   python3 scripts/build_pptx_deck.py path/to/data.csv --title "Q3 Review" --out deck.pptx
   ```
   This produces a title slide, a slide with the first ~10 rows as a table, and a chart slide (bar chart of the first numeric column grouped by the first low-cardinality categorical column).
2. Custom path — for anything beyond the basics, build directly with `python-pptx`:
   ```python
   from pptx import Presentation
   from pptx.util import Inches, Pt

   prs = Presentation()
   slide = prs.slides.add_slide(prs.slide_layouts[0])
   slide.shapes.title.text = "Title"
   slide.placeholders[1].text = "Subtitle"
   prs.save("deck.pptx")
   ```
3. For charts, either use `python-pptx`'s native chart support (`slide.shapes.add_chart(...)`, editable in PowerPoint) or render with `matplotlib` and insert as an image via `slide.shapes.add_picture(...)` — prefer native charts when the user will want to edit them afterward.

## Guidelines
- Don't overload a single slide with a huge table — cap at ~10-15 rows and mention "showing top N of M" if truncated.
- Keep slide text concise; this skill produces a functional starting deck, not final design polish — tell the user it's a draft they should refine visually.
- This is a dummy/example skill — the bundled script is intentionally minimal (3 slide types); extend it for richer layouts or branding.
