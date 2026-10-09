#!/usr/bin/env python3
"""Reproducible PDF build for RESEARCH_NOTE_ROUND1_rev3.pdf (compact rev3).

Same Route B toolchain as build_pdf_rev2.py (pandoc 3.1.11 -> XeLaTeX, DejaVu
fonts). rev3 is the user-directed compact rewrite (~12 body pages + appendix,
figure-driven) of the same evidence base; all numbers are copied verbatim from
RESEARCH_NOTE_FINAL.md or derived from checked-in JSON (fresh-seed split,
soft-ask screens). Presentational post-processing only: no content edits here.

Usage: python3 research/build_pdf_rev3.py
"""
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "RESEARCH_NOTE_REV3.md"
OUT = HERE / "RESEARCH_NOTE_ROUND1_rev3.pdf"
TEX = HERE / "_rev3_build.tex"

os.environ.setdefault("SOURCE_DATE_EPOCH", "1767225600")  # 2026-01-01T00:00:00Z

HEADER = r"""
\usepackage[a4paper,margin=16mm]{geometry}
\usepackage{fontspec}
\setmainfont{DejaVu Serif}
\setsansfont{DejaVu Sans}
\setmonofont{DejaVu Sans Mono}
\usepackage{fancyhdr,lastpage,etoolbox,longtable,booktabs,lscape,titlesec,graphicx}
\titlespacing*{\section}{2.0ex plus .5ex minus .2ex}{0.8ex}{0pt}
\titlespacing*{\subsection}{1.6ex plus .4ex minus .2ex}{0.6ex}{0pt}
\titlespacing*{\subsubsection}{1.4ex plus .3ex minus .2ex}{0.5ex}{0pt}
\pagestyle{fancy}
\fancyhf{}
\fancyfoot[C]{\footnotesize The One Introduction Problem $\cdot$ Round 1 research note (rev3) $\cdot$ Page \thepage\ of \pageref{LastPage}}
\renewcommand{\headrulewidth}{0pt}
\emergencystretch=3em
\setlength{\parskip}{0.2em}
\usepackage{setspace}\setstretch{0.97}
\setlength{\LTpre}{4pt}\setlength{\LTpost}{4pt}
\AtBeginEnvironment{longtable}{\fontsize{7.5}{9.2}\selectfont\setlength{\tabcolsep}{2.5pt}}
\AtBeginEnvironment{tabular}{\footnotesize\setlength{\tabcolsep}{3.5pt}}
\setcounter{secnumdepth}{0}
\relpenalty=0 \binoppenalty=0
\AtBeginDocument{\hypersetup{pdftitle={The One Introduction Problem},pdfauthor={Bipartite Bard},pdflang={en}}}
"""


def postprocess(tex: str) -> str:
    # line breaks after underscores in identifiers (trailing space mandatory)
    tex = tex.replace("\\_", "\\allowbreak \\_\\allowbreak ")
    # tabular -> longtable so long evidence tables paginate instead of overflowing
    tex = tex.replace("\\begin{tabular}", "\\begin{longtable}")
    tex = tex.replace("\\end{tabular}", "\\end{longtable}")
    # pandoc already emits \endhead/\endlastfoot; never add more.
    # Wide evidence tables get their own landscape page (never drop columns,
    # never wrap digits).
    def land(m):
        markers = ("Max same-day matching",   # Appendix B structure table
                   "% of ceiling")            # Appendix D full results table
        if any(k in m.group(0) for k in markers):
            return "\\begin{landscape}\n" + m.group(0) + "\n\\end{landscape}"
        return m.group(0)
    tex = re.sub(r"\\begin\{longtable\}.*?\\end\{longtable\}", land, tex, flags=re.S)
    # identifier-first tables: fixed p-width first column so names wrap
    def pcol(m):
        blk = m.group(0)
        if "\\texttt{" not in blk:
            return blk
        i = blk.index("[]{") + 2
        depth = 0
        for j in range(i, len(blk)):
            if blk[j] == "{":
                depth += 1
            elif blk[j] == "}":
                depth -= 1
                if depth == 0:
                    spec = blk[: j + 1]
                    rest = blk[j + 1:]
                    spec = spec.replace("@{}l", "@{}p{4.0cm}", 1)
                    return spec + rest
        return blk
    tex = re.sub(r"\\begin\{longtable\}.*?\\end\{longtable\}", pcol, tex, flags=re.S)
    return tex


def main() -> int:
    md = SRC.read_text(encoding="utf-8")
    (HERE / "_rev3_src.md").write_text(md, encoding="utf-8")
    (HERE / "_rev3_header.tex").write_text(HEADER, encoding="utf-8")
    r1 = subprocess.run(
        ["pandoc", str(HERE / "_rev3_src.md"),
         "-f", "markdown+pipe_tables+tex_math_dollars",
         "-t", "latex", "--standalone", "--no-highlight",
         "-V", "lang=en",
         "--resource-path", str(HERE),
         "--include-in-header=" + str(HERE / "_rev3_header.tex"),
         "-o", str(TEX)],
        capture_output=True, text=True)
    if r1.returncode != 0:
        print(r1.stderr)
        return 1
    TEX.write_text(postprocess(TEX.read_text(encoding="utf-8")), encoding="utf-8")
    for _ in range(2):
        subprocess.run(["xelatex", "-interaction=nonstopmode",
                        "-output-directory", str(HERE), str(TEX)],
                       capture_output=True, text=True, cwd=str(HERE))
    built = HERE / "_rev3_build.pdf"
    if built.exists():
        built.replace(OUT)
    log = (HERE / "_rev3_build.log").read_text(encoding="utf-8", errors="replace")
    if not OUT.exists():
        print(log[-4000:])
        return 1
    print(f"overfull hbox: {log.count('Overfull \\hbox')} | "
          f"latex errors: {len(re.findall(r'^!', log, re.M))}")
    print("OK ->", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
