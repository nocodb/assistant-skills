#!/usr/bin/env python3
"""Build a simple PDF report (title, summary table, one chart) from a CSV.

Usage:
    python3 build_pdf_report.py path/to/data.csv --title "My Report" --out report.pdf
"""
import argparse
import sys
import tempfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib import colors


def pick_numeric_column(df: pd.DataFrame):
    numeric = df.select_dtypes(include="number").columns.tolist()
    return numeric[0] if numeric else None


def pick_category_column(df: pd.DataFrame, exclude: str, max_categories: int = 12):
    for col in df.columns:
        if col == exclude:
            continue
        if df[col].dtype == object and 1 < df[col].nunique(dropna=True) <= max_categories:
            return col
    return None


def build_chart(df: pd.DataFrame, numeric_col: str, category_col: str | None, out_path: Path):
    fig, ax = plt.subplots(figsize=(6, 3.5))
    if category_col:
        grouped = df.groupby(category_col)[numeric_col].sum().sort_values(ascending=False)
        grouped.plot(kind="bar", ax=ax, color="#2E86AB")
        ax.set_xlabel(category_col)
    else:
        df[numeric_col].plot(kind="hist", ax=ax, color="#2E86AB", bins=20)
        ax.set_xlabel(numeric_col)
    ax.set_ylabel(numeric_col if category_col else "Frequency")
    ax.set_title(f"{numeric_col} by {category_col}" if category_col else f"Distribution of {numeric_col}")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def build_report(csv_path: str, title: str, out_path: str) -> None:
    df = pd.read_csv(csv_path)
    styles = getSampleStyleSheet()
    story = [Paragraph(title, styles["Title"]), Spacer(1, 6)]
    story.append(
        Paragraph(f"Generated from <b>{Path(csv_path).name}</b> — {len(df)} rows, {len(df.columns)} columns.", styles["Normal"])
    )
    story.append(Spacer(1, 16))

    numeric_col = pick_numeric_column(df)
    if numeric_col:
        story.append(Paragraph("Summary Statistics", styles["Heading2"]))
        desc = df[numeric_col].describe().round(2)
        table_data = [["Metric", numeric_col]] + [[idx, str(val)] for idx, val in desc.items()]
        table = Table(table_data, hAlign="LEFT")
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E86AB")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                ]
            )
        )
        story.append(table)
        story.append(Spacer(1, 16))

        category_col = pick_category_column(df, exclude=numeric_col)
        with tempfile.TemporaryDirectory() as tmp:
            chart_path = Path(tmp) / "chart.png"
            build_chart(df, numeric_col, category_col, chart_path)
            story.append(Paragraph("Chart", styles["Heading2"]))
            story.append(Image(str(chart_path), width=440, height=260))
    else:
        story.append(Paragraph("No numeric columns found to summarize.", styles["Normal"]))

    doc = SimpleDocTemplate(out_path, pagesize=letter)
    doc.build(story)
    print(f"Wrote {out_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path")
    parser.add_argument("--title", default="Data Report")
    parser.add_argument("--out", default="report.pdf")
    args = parser.parse_args()

    try:
        build_report(args.csv_path, args.title, args.out)
    except FileNotFoundError:
        print(f"File not found: {args.csv_path}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
