#!/usr/bin/env python3
"""Convert CV or Cover Letter markdown to PDF with pixel-perfect matching of the Modern DOCX template."""
import sys
import os
import subprocess
import tempfile
import re

CSS_STYLE = """@page {
    size: A4;
    margin: 19.05mm; /* Exactly 0.75 in matching Word Modern margins */
}
*, *:before, *:after {
    box-sizing: border-box !important;
}
html {
    max-width: none !important;
    width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
    background: #fff !important;
}
body {
    max-width: none !important;
    width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
    font-family: Calibri, Candara, "Segoe UI", Segoe, Roboto, Helvetica, Arial, sans-serif !important;
    font-size: 10pt;
    line-height: 1.35;
    color: #222222 !important;
    background: #fff !important;
}
h1 {
    font-size: 24pt;
    font-weight: 700;
    color: #1F6F78 !important;
    margin: 0 0 2pt 0;
    letter-spacing: -0.3px;
    width: 100% !important;
}
.subtitle {
    font-size: 10.5pt;
    font-weight: 600;
    color: #555555 !important;
    margin: 0 0 3pt 0;
    width: 100% !important;
}
.contact {
    font-size: 9.5pt;
    color: #555555 !important;
    margin: 0 0 10pt 0;
    padding-bottom: 5pt;
    border-bottom: 0.8pt solid #cbd5e1;
    width: 100% !important;
}
.contact a {
    color: #1F6F78 !important;
    text-decoration: none;
}
h2 {
    font-size: 12pt;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #1F6F78 !important;
    border-bottom: 1.2pt solid #1F6F78 !important;
    padding-bottom: 2pt;
    margin-top: 12pt;
    margin-bottom: 6pt;
    width: 100% !important;
    display: block !important;
}
h3 {
    font-size: 10.5pt;
    font-weight: 700;
    color: #222222 !important;
    margin-top: 8pt;
    margin-bottom: 2pt;
    width: 100% !important;
}
.role-header {
    display: flex !important;
    justify-content: space-between !important;
    align-items: baseline !important;
    margin-top: 8pt;
    margin-bottom: 2pt;
    width: 100% !important;
}
.role-title {
    font-size: 10.5pt;
    font-weight: 700;
    color: #222222 !important;
}
.role-date {
    font-size: 10pt;
    font-weight: normal;
    color: #555555 !important;
    text-align: right;
    white-space: nowrap;
}
p {
    margin-top: 0;
    margin-bottom: 6pt;
    font-size: 10pt;
    line-height: 1.38;
    width: 100% !important;
}
.letter-p {
    margin-top: 0;
    margin-bottom: 10pt;
    font-size: 10.5pt;
    line-height: 1.45;
    width: 100% !important;
}
.letter-subject {
    font-size: 10.5pt;
    font-weight: 700;
    color: #1F6F78 !important;
    margin-top: 10pt;
    margin-bottom: 10pt;
    width: 100% !important;
}
.letter-recipient {
    font-size: 10pt;
    color: #333333 !important;
    line-height: 1.35;
    margin-bottom: 10pt;
    width: 100% !important;
}
ul {
    margin-top: 2pt;
    margin-bottom: 6pt;
    padding-left: 18px;
    width: 100% !important;
}
li {
    margin-bottom: 2.5pt;
    font-size: 9.8pt;
    line-height: 1.34;
}
strong {
    color: #111827 !important;
}
a {
    color: #1F6F78 !important;
    text-decoration: none;
}
blockquote, .footnotes {
    display: none !important;
}"""

def convert_md_to_pdf(input_md, output_pdf):
    with open(input_md, "r", encoding="utf-8") as f:
        content = f.read()

    is_cover_letter = "doc: cover-letter" in content or "Dear " in content

    # Strip YAML frontmatter
    content = re.sub(r"^---\n.*?\n---\n", "", content, flags=re.DOTALL)
    # Strip markdown footnotes citations e.g. [^1]
    content = re.sub(r"\[\^\d+\]", "", content)
    # Strip footnote definitions
    content = re.sub(r"\[\^\d+\]:.*$", "", content, flags=re.MULTILINE)
    # Strip blockquotes (draft notes)
    content = re.sub(r"^>.*$\n?", "", content, flags=re.MULTILINE)

    lines = content.splitlines()
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # Format Top Name, Subtitle and Contact
        if line.startswith("# ") and i + 2 < len(lines) and not lines[i+1].startswith("#"):
            new_lines.append(f"<h1>{line[2:].strip()}</h1>")
            new_lines.append(f"<div class='subtitle'>{lines[i+1].strip()}</div>")
            new_lines.append(f"<div class='contact'>{lines[i+2].strip()}</div>")
            i += 3
            continue
        
        # Handle H3 role headers with dates (e.g. ### Title | Company | City | Date)
        if line.startswith("### "):
            parts = [p.strip() for p in line[4:].split("|")]
            if len(parts) >= 2 and re.search(r"(\d{4}|present|current)", parts[-1], re.I):
                role_info = " | ".join(parts[:-1])
                date_info = parts[-1]
                new_lines.append(f"<div class='role-header'><span class='role-title'>{role_info}</span><span class='role-date'>{date_info}</span></div>")
            else:
                new_lines.append(line)
            i += 1
            continue

        # Handle Cover letter subject lines **Re: ...**
        if is_cover_letter and re.match(r"^\*\*Re:.*?\*\*$", line.strip()):
            subj = line.strip().replace("**", "")
            new_lines.append(f"<div class='letter-subject'>{subj}</div>")
            i += 1
            continue

        new_lines.append(line)
        i += 1
    
    cleaned_md = "\n".join(new_lines)

    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f_md:
        f_md.write(cleaned_md)
        temp_md = f_md.name

    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f_html:
        temp_html = f_html.name

    try:
        # Run pandoc
        cmd_pandoc = ["pandoc", temp_md, "-s", "-o", temp_html]
        subprocess.run(cmd_pandoc, check=True)

        # Inject CSS
        with open(temp_html, "r", encoding="utf-8") as f:
            html = f.read()

        html = html.replace("</head>", f"<style>{CSS_STYLE}</style></head>")
        with open(temp_html, "w", encoding="utf-8") as f:
            f.write(html)

        # Run headless chrome
        chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        cmd_chrome = [
            chrome_path,
            "--headless=new",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--print-to-pdf={output_pdf}",
            temp_html
        ]
        subprocess.run(cmd_chrome, capture_output=True, check=True)
        print(f"Successfully generated PDF: {output_pdf}")
    finally:
        if os.path.exists(temp_md):
            os.remove(temp_md)
        if os.path.exists(temp_html):
            os.remove(temp_html)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: md_to_pdf.py input.md output.pdf")
        sys.exit(1)
    convert_md_to_pdf(sys.argv[1], sys.argv[2])
