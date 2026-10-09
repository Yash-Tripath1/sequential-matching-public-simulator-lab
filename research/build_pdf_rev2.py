#!/usr/bin/env python3
"""Reproducible PDF build for RESEARCH_NOTE_ROUND1_rev2.pdf (Route B).

Toolchain (verified 2026-10-09): Python 3.13, pandoc 3.1.11, XeTeX (texlive-xetex +
texlive-latex-recommended + texlive-latex-extra + lscape/titlesec), DejaVu fonts.

Route choice: a matplotlib-mathtext pre-flight over the 90 math spans found 7 spans
(\\le, \\ge, \\texttt, escaped underscores) that would need LaTeX->mathtext rewrites;
per the build policy that switches the whole document to native LaTeX (Route B)
rather than mixing rewritten spans. XeLaTeX renders all math and the note's Unicode
natively with zero content rewrites.

The script does NOT edit the note. It (1) converts markdown to LaTeX, (2) applies
purely presentational post-processing (tabular->longtable with repeating header,
line-break permission after underscores in identifiers, landscape pages for the
three tables that cannot fit portrait at >=7pt), and (3) compiles twice with xelatex.

Usage: python3 research/build_pdf_rev2.py
"""
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "RESEARCH_NOTE_FINAL.md"
OUT = HERE / "RESEARCH_NOTE_ROUND1_rev2.pdf"
TEX = HERE / "_rev2_build.tex"

os.environ.setdefault("SOURCE_DATE_EPOCH", "1767225600")  # 2026-01-01T00:00:00Z

HEADER = r"""
\usepackage[a4paper,margin=16mm]{geometry}
\usepackage{fontspec}
\setmainfont{DejaVu Serif}
\setsansfont{DejaVu Sans}
\setmonofont{DejaVu Sans Mono}
\usepackage{fancyhdr,lastpage,etoolbox,longtable,booktabs,lscape,titlesec}
\titlespacing*{\section}{2.0ex plus .5ex minus .2ex}{0.8ex}{0pt}
\titlespacing*{\subsection}{1.6ex plus .4ex minus .2ex}{0.6ex}{0pt}
\titlespacing*{\subsubsection}{1.4ex plus .3ex minus .2ex}{0.5ex}{0pt}
\pagestyle{fancy}
\fancyhf{}
\fancyfoot[C]{\footnotesize The One Introduction Problem $\cdot$ Round 1 research note $\cdot$ Page \thepage\ of \pageref{LastPage}}
\renewcommand{\headrulewidth}{0pt}
\emergencystretch=3em
\setlength{\parskip}{0.2em}
\usepackage{setspace}\setstretch{0.97}
\setlength{\LTpre}{4pt}\setlength{\LTpost}{4pt}
% presentational: tables smaller, never wider than the text block
\AtBeginEnvironment{longtable}{\fontsize{7.5}{9.2}\selectfont\setlength{\tabcolsep}{2.5pt}}
\AtBeginEnvironment{tabular}{\footnotesize\setlength{\tabcolsep}{3.5pt}}
\setcounter{secnumdepth}{0}
% let inline math break at relations/binops instead of overflowing
\relpenalty=0 \binoppenalty=0
\AtBeginDocument{\hypersetup{pdftitle={The One Introduction Problem},pdfauthor={Bipartite Bard},pdflang={en}}}
"""


def postprocess(tex: str) -> str:
    # Allow line breaks after underscores (identifiers like
    # lab_potential_core4_maxw). The space after \allowbreak is MANDATORY:
    # without it TeX reads \allowbreak<letters> as one undefined control word
    # and silently drops the letters.
    tex = tex.replace("\\_", "\\allowbreak \\_\\allowbreak ")
    # tabular -> longtable so long evidence tables paginate instead of overflowing
    tex = tex.replace("\\begin{tabular}", "\\begin{longtable}")
    tex = tex.replace("\\end{tabular}", "\\end{longtable}")
    # NOTE: pandoc already emits \endhead/\endlastfoot for repeating headers.
    # Do NOT insert extra \endhead markers — a second \endhead redefines the
    # header chunk as empty and silently deletes every table's header row.
    # The three tables that cannot fit the portrait text block at >=7pt get
    # their own landscape page (layout policy: never drop columns, never wrap
    # digits).
    def land(m):
        markers = ("Max same-day matching",   # §3.1 structure table
                   "d59")                     # §6.8 ask-timing probe
        if any(k in m.group(0) for k in markers):
            return "\\begin{landscape}\n" + m.group(0) + "\n\\end{landscape}"
        return m.group(0)
    tex = re.sub(r"\\begin\{longtable\}.*?\\end\{longtable\}", land, tex, flags=re.S)
    # Tables whose first body cell is a code identifier sit in an `l` column,
    # where the identifier can never wrap; give that column a fixed p-width so
    # the \allowbreak points inserted above can act.
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


def fix_pipe_tables(md: str) -> str:
    """Structural-only repair: pandoc sizes a pipe table from the delimiter
    row; where a source delimiter row has fewer cells than its header row,
    pandoc silently DROPS the extra columns (losing numbers).  Extend the
    delimiter row so every header/body cell survives.  No text is changed."""
    def cells(s: str) -> int:
        s = s.strip()
        if s.startswith("|"):
            s = s[1:]
        if s.endswith("|"):
            s = s[:-1]
        return len(re.split(r"(?<!\\)\|", s))
    lines = md.split("\n")
    out = []
    for i, l in enumerate(lines):
        out.append(l)
        if (l.strip().startswith("|") and i + 1 < len(lines)
                and re.match(r"^\s*\|?[\s:|-]+\|?\s*$", lines[i + 1])
                and "---" in lines[i + 1]):
            d = lines[i + 1]
            miss = cells(l) - cells(d)
            if miss > 0:
                lines[i + 1] = d.rstrip() + "---:|" * miss
    return "\n".join(out)


def main() -> int:
    md = fix_pipe_tables(SRC.read_text(encoding="utf-8"))
    (HERE / "_rev2_src.md").write_text(md, encoding="utf-8")
    (HERE / "_rev2_header.tex").write_text(HEADER, encoding="utf-8")
    r1 = subprocess.run(
        ["pandoc", str(HERE / "_rev2_src.md"),
         "-f", "markdown+pipe_tables+tex_math_dollars",
         "-t", "latex", "--standalone", "--no-highlight",
         "-V", "lang=en",
         "--include-in-header=" + str(HERE / "_rev2_header.tex"),
         "-o", str(TEX)],
        capture_output=True, text=True)
    if r1.returncode != 0:
        print(r1.stderr)
        return 1
    TEX.write_text(postprocess(TEX.read_text(encoding="utf-8")), encoding="utf-8")
    for _ in range(2):
        subprocess.run(["xelatex", "-interaction=nonstopmode",
                        "-output-directory", str(HERE), str(TEX)],
                       capture_output=True, text=True)
    built = HERE / "_rev2_build.pdf"
    if built.exists():
        built.replace(OUT)
    log = (HERE / "_rev2_build.log").read_text(encoding="utf-8", errors="replace")
    if not OUT.exists():
        print(log[-4000:])
        return 1
    n_over = log.count("Overfull \\hbox")
    n_err = len(re.findall(r"^!", log, re.M))
    print(f"overfull hbox: {n_over} | latex errors: {n_err}")
    print("OK ->", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
