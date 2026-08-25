#!/usr/bin/env python3
"""Quick structural + statistical profile of a CSV file.

Usage:
    python3 profile_csv.py path/to/data.csv [--max-categories 15]
"""
import argparse
import sys

import pandas as pd


def profile(path: str, max_categories: int) -> None:
    df = pd.read_csv(path)

    print(f"# Profile: {path}\n")
    print(f"Rows: {len(df)}  Columns: {len(df.columns)}")
    dup_count = df.duplicated().sum()
    if dup_count:
        print(f"Duplicate rows: {dup_count}")

    print("\n## Columns")
    missing = df.isna().mean().mul(100).round(1)
    for col in df.columns:
        dtype = df[col].dtype
        print(f"- {col} ({dtype}) — {missing[col]}% missing")

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    if numeric_cols:
        print("\n## Numeric summary")
        print(df[numeric_cols].describe().round(2).to_string())

    categorical_cols = [
        c
        for c in df.columns
        if c not in numeric_cols and df[c].nunique(dropna=True) <= max_categories
    ]
    if categorical_cols:
        print("\n## Categorical value counts (low-cardinality columns)")
        for col in categorical_cols:
            print(f"\n{col}:")
            print(df[col].value_counts(dropna=False).to_string())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path")
    parser.add_argument(
        "--max-categories",
        type=int,
        default=15,
        help="Max distinct values for a column to be treated as categorical (default: 15)",
    )
    args = parser.parse_args()

    try:
        profile(args.csv_path, args.max_categories)
    except FileNotFoundError:
        print(f"File not found: {args.csv_path}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
