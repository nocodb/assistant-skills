---
name: csv-analysis
description: Analyzes CSV files — e.g. data exported from a NocoDB table/base — to profile columns, compute summary statistics, flag data-quality issues, and surface key insights. Use whenever the user asks to analyze, explore, profile, or summarize a CSV file, or wants to understand data exported from NocoDB before building a report or chart from it.
---

# CSV Analysis

## When to use this skill
- The user provides or points to a `.csv` file and asks to analyze, explore, profile, clean, or summarize it
- The user has exported a NocoDB table/view as CSV and wants insights before further work
- As a first step before building a PDF report ([pdf-report](../pdf-report/SKILL.md)) or slide deck ([pptx-deck](../pptx-deck/SKILL.md)) from the data

## How to use this skill

1. Run the bundled profiler for a fast, structured first pass:
   ```bash
   python3 scripts/profile_csv.py path/to/data.csv
   ```
   It prints shape, column dtypes, missing-value percentages, numeric summary stats (`describe()`), and top value counts for low-cardinality categorical columns.
2. Read the output and lead with what matters to the user — don't just dump the raw profile. Call out:
   - Columns with significant missing/null data
   - Obvious outliers or suspicious values (e.g. negative counts, dates in the future)
   - Likely key/ID columns vs. categorical vs. numeric vs. date columns
   - Any duplicate rows
3. For deeper questions (correlations, group-by breakdowns, time trends), drop into `pandas` directly rather than extending the script:
   ```python
   import pandas as pd
   df = pd.read_csv("data.csv")
   df.groupby("Status")["Amount"].sum().sort_values(ascending=False)
   ```
4. If the CSV came from NocoDB, remember linked/lookup columns often export as stringified JSON or comma-joined values — check a sample row before assuming a column is a plain scalar.

## Guidelines
- Always inspect `df.dtypes` before doing math — NocoDB exports can leave numeric-looking columns as strings (e.g. currency symbols, thousands separators).
- Prefer summarizing findings in prose/tables over pasting large raw DataFrames into the conversation.
- This is a dummy/example skill — the profiler script is intentionally generic; extend it or write ad-hoc pandas for anything domain-specific.
