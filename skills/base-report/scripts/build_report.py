#!/usr/bin/env python3
"""Compile a report spec (JSON) into a typeset PDF via XeLaTeX.

    python3 scripts/build_report.py --spec /tmp/report.json --out /home/user/outputs/report.pdf

The spec is plain text throughout — LaTeX escaping happens here, so callers never
have to think about backslashes or ampersands. See SKILL.md for the shape.

Compiles in a scratch directory and copies only the finished PDF to --out, so a
failed run leaves no half-built artefact next to the deliverable.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

# House style: serif display headings, sans body. Both preinstalled in the
# nc-chat sandbox — see SKILL.md.
HEADING_FONT = "EB Garamond"
BODY_FONT = "Noto Sans"
ACCENT = "2952CC"

PREAMBLE = r"""
\documentclass[11pt,a4paper]{article}
\usepackage[margin=22mm,top=24mm,bottom=24mm]{geometry}
\usepackage{fontspec}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{graphicx}
\usepackage{xcolor}
\usepackage{titlesec}
\usepackage{enumitem}
\usepackage[hidelinks]{hyperref}
\usepackage{tabularx}
\usepackage{ragged2e}

\definecolor{accent}{HTML}{%(accent)s}
\definecolor{rule}{HTML}{D5D5D9}
\definecolor{muted}{HTML}{6A6A75}

\setmainfont{%(body)s}
\newfontfamily\displayfont{%(heading)s}

\titleformat{\section}{\displayfont\Large\bfseries\color{accent}}{}{0pt}{}
\titlespacing*{\section}{0pt}{16pt}{6pt}
\setlist[itemize]{leftmargin=1.2em,itemsep=2pt,topsep=4pt}
\setlength{\parindent}{0pt}
\setlength{\parskip}{6pt}
\renewcommand{\arraystretch}{1.15}
\pagestyle{plain}
""" % {"accent": ACCENT, "body": BODY_FONT, "heading": HEADING_FONT}


def tex_escape(value) -> str:
    """Escape the ten characters TeX treats specially."""
    text = "" if value is None else str(value)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(ch, ch) for ch in text)


def paragraphs(body: str) -> str:
    """Blank-line-separated text → LaTeX paragraphs, escaped."""
    blocks = [b.strip() for b in re.split(r"\n\s*\n", body or "") if b.strip()]
    return "\n\n".join(tex_escape(b) for b in blocks)


def kpi_band(kpis) -> str:
    """A single row of headline figures. Capped at four — five stops scanning."""
    if not kpis:
        return ""
    kpis = kpis[:4]
    cols = "".join(["X"] * len(kpis))
    cells = []
    for kpi in kpis:
        note = kpi.get("note")
        cells.append(
            r"\begin{minipage}[t]{\linewidth}\RaggedRight"
            r"{\footnotesize\color{muted}%s}\\[2pt]"
            r"{\displayfont\LARGE\color{accent}%s}%s"
            r"\end{minipage}"
            % (
                tex_escape(kpi.get("label", "")),
                tex_escape(kpi.get("value", "")),
                (r"\\[2pt]{\footnotesize\color{muted}%s}" % tex_escape(note)) if note else "",
            )
        )
    return (
        r"\vspace{4pt}\noindent\textcolor{rule}{\rule{\linewidth}{0.4pt}}\vspace{8pt}" "\n"
        r"\noindent\begin{tabularx}{\linewidth}{%s}" "\n%s\n" r"\end{tabularx}" "\n"
        r"\vspace{6pt}\noindent\textcolor{rule}{\rule{\linewidth}{0.4pt}}" "\n"
        % (cols, " & ".join(cells) + r" \\")
    )


def table_block(table) -> str:
    """booktabs table. Long tables break across pages rather than overflowing."""
    if not table:
        return ""
    columns = table.get("columns") or []
    rows = table.get("rows") or []
    if not columns or not rows:
        return ""

    # First column left, the rest right — numbers read better right-aligned.
    spec = "l" + "r" * (len(columns) - 1)
    head = " & ".join(r"\textbf{%s}" % tex_escape(c) for c in columns) + r" \\"
    body = "\n".join(
        " & ".join(tex_escape(cell) for cell in row) + r" \\" for row in rows
    )
    caption = table.get("caption")

    return "\n".join(
        filter(
            None,
            [
                # Leading \par, or the caption joins the paragraph above it
                # instead of sitting over the table.
                (
                    r"\par\vspace{6pt}\noindent{\footnotesize\color{muted}%s}\par\vspace{2pt}"
                    % tex_escape(caption)
                )
                if caption
                else None,
                r"\begin{longtable}{%s}" % spec,
                r"\toprule",
                head,
                r"\midrule",
                r"\endhead",
                body,
                r"\bottomrule",
                r"\end{longtable}",
            ],
        )
    )


def chart_block(path, scratch) -> str:
    """Copy the image beside the .tex so the compile has no absolute deps."""
    if not path:
        return ""
    if not os.path.isfile(path):
        print(f"warning: chart not found, skipping: {path}", file=sys.stderr)
        return ""
    name = os.path.basename(path)
    shutil.copyfile(path, os.path.join(scratch, name))
    return (
        r"\vspace{6pt}\begin{center}\includegraphics[width=\linewidth]{%s}\end{center}"
        % name
    )


def build_tex(spec, scratch) -> str:
    parts = [PREAMBLE, r"\begin{document}"]

    # `\par` rather than `\\` — a `\\` outside a tabular is fragile once
    # \parskip is set, and warns with "There's no line here to end".
    parts.append(
        r"{\displayfont\huge\bfseries %s\par}"
        % tex_escape(spec.get("title", "Report"))
    )
    if spec.get("subtitle"):
        parts.append(
            r"\vspace{2pt}{\large\color{muted}%s\par}" % tex_escape(spec["subtitle"])
        )
    parts.append(r"\vspace{10pt}")

    parts.append(kpi_band(spec.get("kpis")))

    for section in spec.get("sections") or []:
        if section.get("heading"):
            parts.append(r"\section*{%s}" % tex_escape(section["heading"]))
        if section.get("body"):
            parts.append(paragraphs(section["body"]))
        parts.append(table_block(section.get("table")))
        parts.append(chart_block(section.get("chart"), scratch))

    recommendations = spec.get("recommendations") or []
    if recommendations:
        parts.append(r"\section*{Recommendations}")
        parts.append(r"\begin{itemize}")
        parts.extend(r"\item %s" % tex_escape(r) for r in recommendations)
        parts.append(r"\end{itemize}")

    parts.append(r"\end{document}")
    return "\n".join(p for p in parts if p)


def relevant_log(log_path) -> str:
    """The lines that actually say what went wrong."""
    if not os.path.isfile(log_path):
        return ""
    with open(log_path, "r", errors="replace") as fh:
        lines = fh.readlines()
    keep = [
        line.rstrip()
        for line in lines
        if line.startswith("!")
        or "Overfull" in line
        or "Underfull" in line
        or "Error" in line
        or line.startswith("l.")
    ]
    return "\n".join(keep[-40:])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", required=True, help="Path to the JSON spec.")
    parser.add_argument("--out", required=True, help="Destination .pdf path.")
    parser.add_argument(
        "--keep-tex",
        metavar="PATH",
        help="Also write the generated .tex here, for debugging.",
    )
    args = parser.parse_args()

    with open(args.spec, "r") as fh:
        spec = json.load(fh)

    scratch = tempfile.mkdtemp(prefix="base-report-")
    tex_path = os.path.join(scratch, "report.tex")

    with open(tex_path, "w") as fh:
        fh.write(build_tex(spec, scratch))

    if args.keep_tex:
        shutil.copyfile(tex_path, args.keep_tex)

    # -halt-on-error so a broken run fails fast instead of waiting on stdin.
    try:
        result = subprocess.run(
            [
                "latexmk",
                "-xelatex",
                "-interaction=nonstopmode",
                "-halt-on-error",
                "report.tex",
            ],
            cwd=scratch,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        print(
            "latexmk not found. This skill needs the nc-chat sandbox image; "
            "do not attempt to install it. Fall back to WeasyPrint or reportlab.",
            file=sys.stderr,
        )
        return 1

    pdf_path = os.path.join(scratch, "report.pdf")
    if result.returncode or not os.path.isfile(pdf_path):
        print("XeLaTeX failed. Relevant log lines:", file=sys.stderr)
        print(relevant_log(os.path.join(scratch, "report.log")), file=sys.stderr)
        print(f"\nScratch kept for inspection: {scratch}", file=sys.stderr)
        return 1

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    shutil.copyfile(pdf_path, args.out)
    shutil.rmtree(scratch, ignore_errors=True)

    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
