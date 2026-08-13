#!/usr/bin/env python3
"""
instant-resume-maker.py

Repurposed from bs.py: instead of fetching a URL over the network, this reads
the portfolio's own index.html straight off disk (same idea as
requests.get(url).text, just local), pulls out the resume-relevant sections
with BeautifulSoup, and drops them into a formal LaTeX template -- same as
bs.py's "map extracted text into a LaTeX resume template" step, just with all
the actual sections (education, experience, projects, etc.) instead of just
name + bio.

Run this any time index.html changes:
    python3 instant-resume-maker.py

Output: assets/resume.pdf -- already what the site's "Download resume"
button links to, so refreshing the page after a run picks up the update.

Requires: beautifulsoup4  (pip install beautifulsoup4 --break-system-packages)
          a LaTeX install with pdflatex on PATH
"""

import subprocess
import sys
from pathlib import Path
from bs4 import BeautifulSoup

HERE = Path(__file__).parent
HTML_PATH = HERE / "index.html"
ASSETS_DIR = HERE / "assets"
TEX_NAME = "resume.tex"  # pdflatex names its output after this stem

# --- LaTeX escaping -----------------------------------------------------
SPECIAL = {
    "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_",
    "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
    "\u2014": "---", "\u2013": "--",           # em dash, en dash
    "\u2192": r"$\rightarrow$",                 # →
    "\u00b7": r"$\cdot$",                       # ·
    "\u2018": "`", "\u2019": "'", "\u201c": "``", "\u201d": "''",
}

def esc(text: str) -> str:
    text = " ".join(text.split())  # collapse whitespace, same as bs.py's strip=True
    return "".join(SPECIAL.get(ch, ch) for ch in text)

# --- extraction -----------------------------------------------------------
def entry_block(article):
    h3 = article.select_one("h3")
    period = article.select_one(".entry-period")
    sub = article.select_one(".entry-sub")
    bullets = [li.get_text() for li in article.select(".bullet-list li")]
    tags = [t.get_text() for t in article.select(".tag-row .tag")]
    return {
        "title": h3.get_text() if h3 else "",
        "period": period.get_text() if period else "",
        "sub": sub.get_text() if sub else "",
        "bullets": bullets,
        "tags": tags,
    }

def extract(soup):
    meta = {row.select_one(".meta-label").get_text(): row.select_one(".meta-value").get_text()
            for row in soup.select(".meta-row")}
    email_link = soup.select_one(".meta-row a.meta-value")
    return {
        "name": soup.select_one(".name").get_text(),
        "tagline": soup.select_one(".tagline").get_text(),
        "based": meta.get("Based", ""),
        "email": email_link.get_text() if email_link else "",
        "socials": {a.get_text(strip=True): a["href"] for a in soup.select(".social-row a")},
        "about": [p.get_text() for p in soup.select("#about .prose p")],
        "education": [entry_block(e) for e in soup.select("#education .entry")],
        "stack": [c.get_text() for c in soup.select("#stack .stack-chip")],
        "experience": [entry_block(e) for e in soup.select("#experience .entry")],
        "projects": [entry_block(e) for e in soup.select("#projects .entry")],
        "leadership": [entry_block(e) for e in soup.select("#leadership .entry")],
        "extras": [entry_block(e) for e in soup.select("#extras .entry")],
    }

# --- LaTeX template ---------------------------------------------------------
PREAMBLE = r"""\documentclass[10pt,letterpaper]{article}
\usepackage[margin=0.5in]{geometry}
\usepackage{mathptmx}
\usepackage{titlesec}
\usepackage{enumitem}
\usepackage{hyperref}
\usepackage{xcolor}
\usepackage[T1]{fontenc}
\pagestyle{empty}
\setlength{\parindent}{0pt}
\definecolor{linkcol}{HTML}{1a4480}
\hypersetup{colorlinks=true, urlcolor=linkcol}
\titleformat{\section}{\large\bfseries}{}{0pt}{}[\vspace{-2pt}\titlerule]
\titlespacing{\section}{0pt}{8pt}{4pt}
\newcommand{\head}[2]{{\bfseries #1} \hfill {\itshape #2}\\}
\newcommand{\subline}[1]{{\itshape #1}\\[2pt]}
\setlist[itemize]{leftmargin=14pt, itemsep=1pt, topsep=2pt, parsep=0pt}
\begin{document}
"""

def entries_section(title, entries):
    if not entries:
        return []
    out = [r"\section*{%s}" % esc(title)]
    for e in entries:
        head = esc(e["title"])
        if e["tags"]:
            head += r" \normalfont{\small(%s)}" % esc(", ".join(e["tags"]))
        out.append(r"\head{%s}{%s}" % (head, esc(e["period"])))
        if e["sub"]:
            out.append(r"\subline{%s}" % esc(e["sub"]))
        if e["bullets"]:
            out.append(r"\begin{itemize}")
            out += [r"\item " + esc(b) for b in e["bullets"]]
            out.append(r"\end{itemize}")
        out.append(r"\vspace{2pt}")
    return out

def build_tex(d):
    L = [PREAMBLE]

    L.append(r"\begin{center}")
    L.append(r"{\LARGE \bfseries %s}\\[2pt]" % esc(d["name"]))
    L.append(r"{\small %s}\\[2pt]" % esc(d["tagline"]))
    bits = []
    if d["based"]:
        bits.append(esc(d["based"]))
    if d["email"]:
        bits.append(r"\href{mailto:%s}{%s}" % (d["email"], esc(d["email"])))
    for label, url in d["socials"].items():
        bits.append(r"\href{%s}{%s}" % (url, esc(label)))
    L.append(r"{\small " + " ~$\\vert$~ ".join(bits) + r"}")
    L.append(r"\end{center}")
    L.append(r"\vspace{-4pt}")

    if d["about"]:
        L.append(r"\section*{About}")
        for p in d["about"]:
            L.append(esc(p) + r"\\[3pt]")

    if d["education"]:
        L.append(r"\section*{Education}")
        for e in d["education"]:
            L.append(r"\head{%s}{%s}" % (esc(e["title"]), esc(e["period"])))
            if e["sub"]:
                L.append(esc(e["sub"]) + r"\\[2pt]")

    if d["stack"]:
        L.append(r"\section*{Technical Skills}")
        L.append(esc(", ".join(d["stack"])))

    L += entries_section("Experience", d["experience"])
    L += entries_section("Projects", d["projects"])
    L += entries_section("Leadership", d["leadership"])
    L += entries_section("Talks & Workshops", d["extras"])

    L.append(r"\end{document}")
    return "\n".join(L)

def main():
    if not HTML_PATH.exists():
        sys.exit(f"Can't find {HTML_PATH}")

    # Same shape as bs.py's requests.get(url).text -> BeautifulSoup(...),
    # just reading the local file instead of fetching it over HTTP.
    soup = BeautifulSoup(HTML_PATH.read_text(encoding="utf-8"), "html.parser")
    data = extract(soup)
    tex_source = build_tex(data)

    ASSETS_DIR.mkdir(exist_ok=True)
    tex_path = ASSETS_DIR / TEX_NAME
    tex_path.write_text(tex_source, encoding="utf-8")

    result = subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", TEX_NAME],
        cwd=ASSETS_DIR, capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(result.stdout[-3000:])
        sys.exit("pdflatex failed -- see log above")

    # Clean up LaTeX build artifacts, keep only the .tex source + .pdf
    for ext in (".aux", ".log", ".out"):
        (ASSETS_DIR / f"resume{ext}").unlink(missing_ok=True)

    print(f"Wrote {ASSETS_DIR / 'resume.pdf'}")

if __name__ == "__main__":
    main()
