#!/usr/bin/env python3
"""
generate_resume.py

Parses index.html (the portfolio site) and generates a formal LaTeX resume,
then compiles it to resume.pdf. Run this any time index.html content changes
to keep resume.pdf in sync.

Usage:
    python3 generate_resume.py [path/to/index.html] [output_dir]

Requires: beautifulsoup4, a LaTeX distribution (pdflatex on PATH).
"""

import sys
import re
import subprocess
import tempfile
import shutil
from pathlib import Path
from bs4 import BeautifulSoup

LATEX_SPECIAL = {
    '&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#',
    '_': r'\_', '{': r'\{', '}': r'\}', '~': r'\textasciitilde{}',
    '^': r'\textasciicircum{}', '\\': r'\textbackslash{}',
}
# order matters: backslash first so we don't double-escape our own output
_ESCAPE_RE = re.compile('|'.join(re.escape(k) for k in sorted(LATEX_SPECIAL, key=len, reverse=True)))

def esc(text: str) -> str:
    if text is None:
        return ""
    text = re.sub(r'\s+', ' ', text).strip()
    text = text.replace('\\', r'\textbackslash{}')
    for k, v in LATEX_SPECIAL.items():
        if k == '\\':
            continue
        text = text.replace(k, v)
    # normalize typographic dashes/ampersand-entities BeautifulSoup already decoded
    text = text.replace('—', '---').replace('–', '--')
    return text

def get_text(node):
    return node.get_text(" ", strip=True) if node else ""

def parse_portfolio(html_path: Path):
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
    data = {}

    data["name"] = get_text(soup.select_one(".id-block .name"))
    data["tagline"] = get_text(soup.select_one(".id-block .tagline"))

    meta = {}
    for row in soup.select(".meta-list .meta-row"):
        label = get_text(row.select_one(".meta-label"))
        value = get_text(row.select_one(".meta-value"))
        meta[label] = value
    data["meta"] = meta

    socials = []
    for a in soup.select(".social-row a.social-btn"):
        socials.append({"label": get_text(a.select_one("span")), "href": a.get("href", "")})
    data["socials"] = socials

    data["about"] = [get_text(p) for p in soup.select("#about .prose p")]

    def parse_entries(section_id):
        entries = []
        section = soup.select_one(f"#{section_id}")
        if not section:
            return entries
        for entry in section.select(".entry"):
            e = {
                "title": get_text(entry.select_one(".entry-head h3")),
                "period": get_text(entry.select_one(".entry-period")),
                "sub": get_text(entry.select_one(".entry-sub")),
                "bullets": [get_text(li) for li in entry.select(".bullet-list li")],
                "tags": [get_text(t) for t in entry.select(".tag-row .tag")],
            }
            entries.append(e)
        return entries

    data["education"] = parse_entries("education")
    data["experience"] = parse_entries("experience")
    data["projects"] = parse_entries("projects")
    data["leadership"] = parse_entries("leadership")
    data["extras"] = parse_entries("extras")
    data["stack"] = [get_text(s) for s in soup.select("#stack .stack-chip")]

    return data


def build_tex(data: dict) -> str:
    name = esc(data["name"])
    meta = data["meta"]
    email = ""
    email_link = None
    for label, val in meta.items():
        if label.lower() == "reach":
            email = val
    # pull the real mailto href for a clickable link
    reach_href = None
    # (kept simple: display text is enough for a resume header)

    location = meta.get("Based", "")
    studying = meta.get("Studying", "")

    social_line = " \\quad $\\vert$ \\quad ".join(
        f"\\href{{{s['href']}}}{{{esc(s['label'])}}}" for s in data["socials"] if s.get("href")
    )

    header = r"""
\begin{center}
{\Huge \scshape """ + name + r"""} \\ \vspace{4pt}
""" + esc(location) + (r" \quad $\vert$ \quad " + esc(email) if email else "") + r""" \\
""" + social_line + r"""
\end{center}
"""

    def section(title):
        return f"\n\\section*{{{esc(title)}}}\n\\vspace{{-4pt}}\n"

    def entry_block(e, show_tags=False):
        out = "\\resumeEntry\n"
        out += f"{{{esc(e['title'])}}}{{{esc(e['period'])}}}{{{esc(e['sub'])}}}\n"
        if e["bullets"]:
            out += "\\begin{itemize}[leftmargin=*, itemsep=0pt, topsep=2pt]\n"
            for b in e["bullets"]:
                out += f"  \\item {esc(b)}\n"
            out += "\\end{itemize}\n"
        if show_tags and e["tags"]:
            out += f"\\textit{{\\small {esc(', '.join(e['tags']))}}}\\\\[4pt]\n"
        return out

    body = header

    if data["about"]:
        body += section("Summary")
        body += esc(data["about"][0]) + "\n"  # first paragraph only — resumes stay tight
        if len(data["about"]) > 1:
            body += " " + esc(data["about"][1]) + "\n"

    if data["education"]:
        body += section("Education")
        for e in data["education"]:
            body += entry_block(e)

    if data["stack"]:
        body += section("Technical Skills")
        body += esc(", ".join(data["stack"])) + "\n"

    if data["experience"]:
        body += section("Experience")
        for e in data["experience"]:
            body += entry_block(e)

    if data["projects"]:
        body += section("Projects")
        for e in data["projects"]:
            body += entry_block(e, show_tags=True)

    if data["leadership"]:
        body += section("Leadership")
        for e in data["leadership"]:
            body += entry_block(e)

    if data["extras"]:
        body += section("Talks \\& Workshops")
        for e in data["extras"]:
            body += entry_block(e)

    preamble = r"""
\documentclass[10.5pt, letterpaper]{article}
\usepackage[left=0.75in, right=0.75in, top=0.6in, bottom=0.6in]{geometry}
\usepackage{titlesec}
\usepackage{enumitem}
\usepackage{hyperref}
\usepackage{xcolor}
\usepackage{tabularx}
\usepackage[T1]{fontenc}
\pagestyle{empty}
\definecolor{headergray}{RGB}{60,60,60}
\titleformat{\section}{\large\scshape\raggedright\color{headergray}}{}{0em}{}[\titlerule]
\titlespacing*{\section}{0pt}{10pt}{6pt}
\hypersetup{colorlinks=true, urlcolor=headergray, linkcolor=headergray}
\setlength{\parindent}{0pt}

\newcommand{\resumeEntry}[3]{%
  \noindent\textbf{#1} \hfill \textit{#2} \\
  \textit{\small #3} \\[2pt]
}

\begin{document}
"""
    footer = r"""
\end{document}
"""
    return preamble + body + footer


def compile_pdf(tex_source: str, out_dir: Path, out_name: str = "resume"):
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        tex_path = tmp / f"{out_name}.tex"
        tex_path.write_text(tex_source, encoding="utf-8")
        for _ in range(2):  # run twice for hyperref/toc stability
            result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", f"{out_name}.tex"],
                cwd=tmp, capture_output=True, text=True
            )
        pdf_path = tmp / f"{out_name}.pdf"
        if not pdf_path.exists():
            print(result.stdout[-3000:])
            print(result.stderr[-2000:])
            raise RuntimeError("pdflatex failed to produce a PDF — see log above.")
        out_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy(pdf_path, out_dir / f"{out_name}.pdf")
        shutil.copy(tex_path, out_dir / f"{out_name}.tex")
        return out_dir / f"{out_name}.pdf"


def main():
    html_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("index.html")
    out_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")

    data = parse_portfolio(html_path)
    tex = build_tex(data)
    pdf_path = compile_pdf(tex, out_dir)
    print(f"Generated {pdf_path}")


if __name__ == "__main__":
    main()
