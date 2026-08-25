---
name: pdf-report
description: Generates polished PDF reports — e.g. summarizing a NocoDB table export or a CSV analysis — with a title page, summary stats table, and charts, using ReportLab and matplotlib. Use whenever the user asks to create, export, or generate a PDF report/document from tabular data.
---

# PDF Report Generation

## When to use this skill
- The user asks for a PDF report/summary built from a CSV, a NocoDB export, or an already-computed analysis
- Follows naturally after [csv-analysis](../csv-analysis/SKILL.md) once the user wants the findings written up as a shareable document

## How to use this skill

1. Quick path — build a full report directly from a CSV:
   ```bash
   python3 scripts/build_pdf_report.py path/to/data.csv --title "Monthly Sales Report" --out report.pdf
   ```
   This auto-picks the first numeric column, renders a bar chart of it grouped by the first low-cardinality categorical column, adds a summary-stats table, and writes `report.pdf`.
2. Custom path — for anything the script doesn't cover (multiple charts, custom sections, branded styling), build directly with ReportLab's `platypus` API:
   ```python
   from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, Spacer, Image
   from reportlab.lib.styles import getSampleStyleSheet
   from reportlab.lib.pagesizes import letter

   styles = getSampleStyleSheet()
   story = [Paragraph("Report Title", styles["Title"]), Spacer(1, 12)]
   story.append(Paragraph("Summary text...", styles["Normal"]))
   story.append(Table([["Metric", "Value"], ["Total Rows", "1,204"]]))
   doc = SimpleDocTemplate("report.pdf", pagesize=letter)
   doc.build(story)
   ```
3. For charts, render with `matplotlib` to a PNG first, then embed via `reportlab.platypus.Image("chart.png", width=..., height=...)`.

## Guidelines
- Never use Unicode subscript/superscript characters in ReportLab text — built-in fonts render them as black boxes. Use `<sub>`/`<super>` tags inside `Paragraph` text instead.
- Keep tables to a reasonable row count on the page — paginate or summarize (top N + "and N more") rather than dumping thousands of rows into a PDF table.
- Confirm the output path with the user if it's not obvious where the PDF should be saved.
- This is a dummy/example skill — the bundled script covers one chart + one table; extend it for multi-section or branded reports.
