---
name: spreadsheet
description: Produces or edits a real spreadsheet file — .xlsx with live formulas, formatting and multiple sheets — from NocoDB records, an uploaded file, or from scratch. Use whenever the deliverable itself is a spreadsheet the user will open in Excel or Sheets: a budget or model, an export with computed columns, a filled template, a workbook someone else has to fill in, or cleaning a messy .xlsx/.csv into a proper one. Trigger when the user names a spreadsheet file even casually ("the xlsx in my downloads", "add a total column to that sheet"). Do NOT use when the deliverable is a PDF or written report (see base-report), a slide deck (see pptx-deck), an answer in chat about data (see csv-analysis), or loading a file into a NocoDB table — that is import_file.
---

# Spreadsheet (.xlsx)

| Task | Approach |
|---|---|
| Create or edit with formulas and formatting | `openpyxl` — see gotchas below |
| Bulk rows in or out, no formatting | `pandas` (`read_excel`, `to_excel`) |
| Look at an existing sheet before editing | `pandas.read_excel(..., sheet_name=None)`, then `openpyxl` for cell coordinates |
| Any workbook containing formulas | **`scripts/recalc.py` before you hand it over** |

> Script paths below are relative to this skill's directory — the absolute path is
> the one `load_skill` reported, e.g. `/home/user/skills/spreadsheet`.

## The thing that will catch you

openpyxl writes a formula as a **string with no cached result**. Nothing computes
it on save. Until the file is recalculated, every formula cell reads back empty —
and not just as `None`:

```python
ws["B1"] = "=SUM(A1:A3)"; wb.save(path)

load_workbook(path, data_only=True)["B1"].value   # -> None
pd.read_excel(path)                               # -> column B is ABSENT entirely
```

So a workbook that is correct in your code arrives at the user with blank
columns, and nothing in your script warns you. This is the single most common way
to ship a broken spreadsheet.

## Recalculate — mandatory whenever the file has formulas

```bash
python3 /home/user/skills/spreadsheet/scripts/recalc.py /home/user/outputs/model.xlsx
```

LibreOffice computes every formula, the file is rewritten in place, and you get
JSON:

- `status` — `ok` · `errors_found` · `unevaluated` · `failed`
- `errors` — cells holding `#REF!`, `#NAME?`, `#VALUE!`, `#DIV/0!` …
- `unevaluated` — formula cells **still empty after recalculation**. Usually a
  function this LibreOffice build cannot compute. A formula that legitimately
  returns `""` also lands here, so check the named cells before assuming they are
  all broken.
- `by_type` — up to 100 locations per error type, as `Sheet1!B4`

Fix what it names and run it again. Pass `--strict` to make it exit non-zero on
anything but `ok`, if you want to gate on it.

**Two things a green result does not tell you:**

1. Without `--strict` the exit code is 0 even for `errors_found`. Read `status`,
   never the exit code alone.
2. `ok` proves your formulas **evaluate**, not that they are **right**. A range
   off by one, or a reference to the wrong row, computes perfectly and produces a
   clean file with wrong numbers. Write two or three formulas first, recalc, and
   check the values are what you expect *before* building out a grid.

## Choosing formulas that survive

LibreOffice implements a large subset of Excel's functions, not all of them, and
this cuts both ways:

- A function it cannot parse gets baked into the delivered file as `#NAME?`.
- Some modern dynamic-array functions (the ones that spill across a range) are
  worse than that — an openpyxl-written file carries no spill metadata, so only
  the anchor cell gets a value and the rest silently stay empty. Those surface as
  `unevaluated`, not as errors.

So: **prefer long-established functions** — `SUM`, `SUMIFS`, `INDEX`, `MATCH`,
`IFERROR`, `SUMPRODUCT`, `VLOOKUP` — and do sorting, filtering and de-duplication
in Python before writing cells, rather than with a spilling formula.

Do not trust a memorised list of what works. `recalc.py` tells you the truth for
*this* runtime: write one cell using the function, recalc, and look.

## Sourcing the data

**From the base** — `query_records` for rows (`limit` caps at 100; page with
`offset`, never restart at 0), `aggregate` for totals. Pass `fields` to keep wide
tables manageable. Write values into cells and let the *spreadsheet* compute the
derived columns — that is the point of shipping a spreadsheet rather than a CSV.

**From an upload** — files land at `/home/user/<filename>`. Load with pandas,
clean, then write. Watch for numeric-looking columns arriving as strings
(currency symbols, thousands separators) — fix before any formula references
them.

## Requirements for anything you hand over

- **Formulas, not computed constants.** Write `ws["B10"] = "=SUM(B2:B9)"`, never
  the Python-computed total. The sheet has to stay correct when its inputs change
  — otherwise send a CSV and be honest about it.
- **Follow the spec literally.** Exact sheet names, exact column headers, the
  formula the user spelled out. A tidier design that computes something else is a
  failure, however much better it looks.
- **Editing an existing file: match its conventions.** They override everything
  here. Find where its inputs live (usually marked by a distinct font colour or
  fill), write only there, and leave existing formulas alone.
- **Label every assumption** in a cell the reader will see — an adjacent cell or a
  header note. A hardcoded number with no stated origin is the thing that gets
  quoted back wrongly.
- **A workbook for someone else to fill in** needs a short legend saying which
  cells to edit, and one example row in the expected format. Never add an example
  row to a file you were asked to edit.
- **One deliverable** in `/home/user/outputs/`. Build intermediates in `/tmp`.
  Refer to the file by name only in your reply.

## openpyxl gotchas

- **Reading formulas and values takes two loads.** `data_only=True` gives cached
  values with the formulas gone; the default gives formula strings with no
  values. One pass cannot give both.
- **`data_only=True` is destructive if you save.** That workbook object has no
  formulas left, so saving replaces every formula with a literal — permanently.
  Load twice; only ever save the non-`data_only` one.
- **Merged cells: write the top-left anchor only.** Every other cell in the range
  is a `MergedCell` whose `.value` is read-only.
- **`.xlsm` loses its macros** unless you pass `keep_vba=True` to
  `load_workbook`.
- **A sheet name containing a space must be quoted** in a cross-sheet reference:
  `='Input Assumptions'!$B$5`. Unquoted it evaluates to an error.
- **Percentages are stored as fractions.** `0.15` with a `0.0%` format renders
  `15.0%`; storing `15` renders `1500.0%`.

## Dependencies

`openpyxl`, `xlsxwriter`, `xlrd`, `pandas` and headless LibreOffice (`soffice`)
are preinstalled in the nc-chat sandbox image. **Never `pip install` or
`apt install`** — if an import fails, use a different preinstalled library.
`recalc.py` fails with a clear message when LibreOffice is absent rather than
pretending it worked.
