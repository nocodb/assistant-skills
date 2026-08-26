#!/usr/bin/env python3
"""Flag the data defects that would make a reported number wrong.

    python3 scripts/sanity_check.py --records /tmp/deals.json \
        --unique Name --date-fields "Close Date"

This is a GUARD, not a deliverable. Its output never reaches the reader — you run
it over the records you are about to report on, fix or exclude what it finds, and
mention it only if it changed a published figure. Three spellings of one stage
turn a four-slice chart into seven; two duplicate rows inflate a total. That is
the whole point.

--records is JSON: either a list of records, or an object with a "records"/"list"
key (both shapes `query_records` can produce). A record is either flat
(`{"Id": 1, "Name": "..."}`) or V3-shaped (`{"id": 1, "fields": {...}}`).

Findings name record ids, because a count on its own isn't actionable. Every
check reports at most --max-examples ids and says how many more there were.
"""

import argparse
import json
import re
import statistics
import sys
from collections import Counter, defaultdict
from datetime import datetime

# A check firing on most of the table means the rule is wrong, not the data.
NOISE_RATIO = 0.30


def normalise(value) -> str:
    """Fold case, whitespace and punctuation — how near-miss duplicates are found."""
    text = str(value).strip().lower()
    text = re.sub(r"[\s_\-]+", " ", text)
    text = re.sub(r"[^\w\s]", "", text)
    return text.strip()


def plural(count, noun="record") -> str:
    return f"{count} {noun}" if count == 1 else f"{count} {noun}s"


def is_blank(value) -> bool:
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, (list, dict)):
        return len(value) == 0
    return value is None


def load_records(path):
    """Accept every shape query_records can hand back, flat or V3."""
    with open(path, "r") as fh:
        raw = json.load(fh)

    if isinstance(raw, dict):
        for key in ("records", "list", "rows", "data"):
            if isinstance(raw.get(key), list):
                raw = raw[key]
                break
        else:
            raise SystemExit(
                "--records JSON is an object with no records/list/rows/data array"
            )

    if not isinstance(raw, list):
        raise SystemExit("--records JSON must be a list of records")

    flat = []
    for index, record in enumerate(raw):
        if not isinstance(record, dict):
            continue
        fields = record.get("fields")
        row = dict(fields) if isinstance(fields, dict) else dict(record)
        row.pop("fields", None)
        # Keep whichever id the payload carried; fall back to position so every
        # finding can still point somewhere.
        row["__id"] = (
            record.get("id")
            or record.get("Id")
            or record.get("ID")
            or (fields or {}).get("Id")
            or f"row {index + 1}"
        )
        flat.append(row)
    return flat


def parse_date(value):
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip().replace("Z", "+00:00")
    for candidate in (text, text[:19], text[:10]):
        try:
            return datetime.fromisoformat(candidate)
        except ValueError:
            continue
    return None


class Report:
    def __init__(self, table, scanned, max_examples):
        self.table = table
        self.scanned = scanned
        self.max_examples = max_examples
        self.sections = []

    def add(self, heading, lines, severity="warning"):
        if lines:
            self.sections.append((heading, lines, severity))

    def examples(self, ids):
        shown = [str(i) for i in ids[: self.max_examples]]
        more = len(ids) - len(shown)
        return ", ".join(shown) + (f" …and {more} more" if more > 0 else "")

    def render(self, scope_note=None):
        out = [f"# {self.table} — sanity check (internal, do not publish)", ""]
        out.append(f"Scanned **{self.scanned}** records.")
        if scope_note:
            out.append(f"{scope_note}")
        out.append("")

        if not self.sections:
            out.append("Nothing found that would change a reported number.")
            return "\n".join(out)

        blocking = [s for s in self.sections if s[2] == "blocking"]
        if blocking:
            out.append("::: callout warning")
            out.append(
                "%d check%s found something that could make a published number wrong."
                % (len(blocking), "" if len(blocking) == 1 else "s")
            )
            out.append(":::")
            out.append("")

        for heading, lines, _severity in self.sections:
            out.append(f"## {heading}")
            out.append("")
            out.extend(f"- {line}" for line in lines)
            out.append("")

        return "\n".join(out)


def check_blanks(records, fields, report):
    for field in fields:
        offenders = [r["__id"] for r in records if is_blank(r.get(field))]
        if not offenders:
            continue
        if len(offenders) > len(records) * NOISE_RATIO:
            report.add(
                f"`{field}` is blank on most records",
                [
                    f"{len(offenders)} of {len(records)} are blank — that reads more "
                    f"like `{field}` not being required after all than {len(offenders)} "
                    f"separate mistakes. Confirm the rule before treating these as findings."
                ],
                severity="warning",
            )
            continue
        report.add(
            f"Blank `{field}` ({plural(len(offenders))})",
            [f"Records: {report.examples(offenders)}"],
            severity="blocking",
        )


def check_duplicates(records, fields, report):
    for field in fields:
        exact = defaultdict(list)
        folded = defaultdict(list)
        for record in records:
            value = record.get(field)
            if is_blank(value):
                continue
            exact[str(value)].append(record["__id"])
            folded[normalise(value)].append(record["__id"])

        exact_dupes = {k: v for k, v in exact.items() if len(v) > 1}
        if exact_dupes:
            report.add(
                f"Duplicate `{field}` — identical values",
                [
                    f'"{value}" × {len(ids)} — {report.examples(ids)}'
                    for value, ids in sorted(
                        exact_dupes.items(), key=lambda kv: -len(kv[1])
                    )
                ],
                severity="blocking",
            )

        # Folded groups that aren't already exact duplicates: same thing typed
        # differently, which no unique index would have caught.
        near = {}
        for key, ids in folded.items():
            if len(ids) < 2:
                continue
            variants = {
                str(r.get(field))
                for r in records
                if r["__id"] in set(ids) and not is_blank(r.get(field))
            }
            if len(variants) > 1:
                near[key] = (sorted(variants), ids)

        if near:
            report.add(
                f"Near-duplicate `{field}` — same value, different spelling",
                [
                    f'{" / ".join(chr(34) + v + chr(34) for v in variants)} — '
                    f"{report.examples(ids)}"
                    for _key, (variants, ids) in sorted(
                        near.items(), key=lambda kv: -len(kv[1][1])
                    )
                ],
                severity="blocking",
            )


def check_value_drift(records, report, skip_fields=(), max_cardinality=25):
    """Low-cardinality text fields: variants that fold together, and one-offs."""
    candidates = defaultdict(Counter)
    for record in records:
        for field, value in record.items():
            if field == "__id" or field in skip_fields:
                continue
            if not isinstance(value, str) or is_blank(value):
                continue
            candidates[field][value.strip()] += 1

    for field, counts in candidates.items():
        if len(counts) > max_cardinality or len(counts) < 2:
            continue

        groups = defaultdict(list)
        for value in counts:
            groups[normalise(value)].append(value)

        variants = [v for v in groups.values() if len(v) > 1]
        if variants:
            report.add(
                f"`{field}` has values that differ only in case or spacing",
                [
                    " / ".join(f'"{v}" ({counts[v]})' for v in sorted(group))
                    for group in variants
                ],
                severity="blocking",
            )

        singles = [v for v, n in counts.items() if n == 1]
        # Only meaningful where the field behaves like an enum: few distinct
        # values against many rows. In a free-text field every value is a
        # single, and "Kim" appearing once is a person, not a typo.
        enum_shaped = len(counts) * 3 <= len(records)
        if singles and enum_shaped and len(counts) - len(singles) >= 2:
            report.add(
                f"`{field}` values used exactly once — check for typos",
                [", ".join(f'"{v}"' for v in sorted(singles))],
                severity="warning",
            )


def check_dates(records, fields, date_range, report):
    now = datetime.now()
    for field in fields:
        impossible, far_future, unparsed = [], [], []
        for record in records:
            value = record.get(field)
            if is_blank(value):
                continue
            parsed = parse_date(value)
            if parsed is None:
                unparsed.append(record["__id"])
                continue
            if parsed.year < 1990:
                impossible.append(record["__id"])
            elif (parsed - now).days > 365 * 5:
                far_future.append(record["__id"])

        report.add(
            f"`{field}` before 1990 ({plural(len(impossible))})",
            [f"Records: {report.examples(impossible)}"] if impossible else [],
            severity="blocking",
        )
        report.add(
            f"`{field}` more than 5 years out ({plural(len(far_future))})",
            [f"Records: {report.examples(far_future)}"] if far_future else [],
        )
        report.add(
            f"`{field}` values that aren't parseable dates ({plural(len(unparsed))})",
            [f"Records: {report.examples(unparsed)}"] if unparsed else [],
            severity="blocking",
        )

    if date_range and ":" in date_range:
        start_field, end_field = (p.strip() for p in date_range.split(":", 1))
        inverted = []
        for record in records:
            start = parse_date(record.get(start_field))
            end = parse_date(record.get(end_field))
            if start and end and end < start:
                inverted.append(record["__id"])
        report.add(
            f"`{end_field}` earlier than `{start_field}` ({plural(len(inverted))})",
            [f"Records: {report.examples(inverted)}"] if inverted else [],
            severity="blocking",
        )


def check_numeric_outliers(records, report):
    """Median-absolute-deviation, so a couple of extremes don't hide themselves."""
    columns = defaultdict(list)
    for record in records:
        for field, value in record.items():
            if field == "__id" or isinstance(value, bool):
                continue
            if isinstance(value, (int, float)):
                columns[field].append((record["__id"], float(value)))

    for field, pairs in columns.items():
        values = [v for _id, v in pairs]
        if len(values) < 8:
            continue
        median = statistics.median(values)
        deviations = [abs(v - median) for v in values]
        mad = statistics.median(deviations)
        if mad == 0:
            continue
        outliers = [i for i, v in pairs if abs(v - median) / mad > 3]
        if outliers and len(outliers) <= len(values) * NOISE_RATIO:
            report.add(
                f"`{field}` outliers ({plural(len(outliers))}, median {median:g})",
                [f"Records: {report.examples(outliers)}"],
            )


def split_arg(value):
    return [p.strip() for p in (value or "").split(",") if p.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--records", required=True, help="Path to the records JSON.")
    parser.add_argument("--table", default="Records", help="Table name, for the heading.")
    parser.add_argument("--required", help="Comma-separated fields that must be filled.")
    parser.add_argument("--unique", help="Comma-separated fields that must be unique.")
    parser.add_argument("--date-fields", help="Comma-separated Date/DateTime fields.")
    parser.add_argument(
        "--date-range",
        metavar="START:END",
        help='Two date fields where END must not precede START, e.g. "Start:End".',
    )
    parser.add_argument(
        "--scope-note",
        help="Note the scope when only part of the table was pulled.",
    )
    parser.add_argument("--max-examples", type=int, default=15)
    parser.add_argument("--out", help="Write markdown here instead of stdout.")
    args = parser.parse_args()

    records = load_records(args.records)
    if not records:
        print("No records to audit.", file=sys.stderr)
        return 1

    report = Report(args.table, len(records), args.max_examples)

    check_blanks(records, split_arg(args.required), report)
    check_duplicates(records, split_arg(args.unique), report)
    # --unique fields already get a near-duplicate section; don't say it twice.
    check_value_drift(records, report, skip_fields=set(split_arg(args.unique)))
    check_dates(records, split_arg(args.date_fields), args.date_range, report)
    check_numeric_outliers(records, report)

    markdown = report.render(args.scope_note)

    if args.out:
        with open(args.out, "w") as fh:
            fh.write(markdown + "\n")
        print(f"Wrote {args.out} — {len(report.sections)} finding section(s)")
    else:
        print(markdown)
    return 0


if __name__ == "__main__":
    sys.exit(main())
