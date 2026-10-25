# Document Markdown Format, Templates and Rendering

All documents are written first as Markdown in the constrained format below. `scripts/render_docx.py` (Python 3.8+, standard library only, no install needed) turns them into Word files.

## Contents
1. Format rules
2. Draft vs final (citations)
3. Templates
4. Commands
5. Output files

## 1. Format rules

```markdown
---
doc: cv                 # cv | cover-letter | references | linkedin | interview | case-study | offer | negotiation
template: modern        # classic | modern | minimal | executive | compact
page: a4                # a4 | letter
lang: en-GB             # sets Word spell-check language
---

# Full Name
Headline | Specialism | Specialism           <- optional line (CV)
+44 7700 900123 | name@example.com | linkedin.com/in/name | City, Country

## Section Heading                         <- section (Heading 1)
Paragraph text. **bold** and *italic* are supported.

### Job Title | Company | City, Country | Mon YYYY – Present   <- role (Heading 2); the last part, if it contains a year/"Present", is right-aligned as dates
- Bullet
  - Sub-bullet (indent 2+ spaces)

**Key Achievements**                        <- a line that is entirely bold becomes a sub-heading (CV) or bold line (letter)
```

- Headings: use plain, standard names that ATS recognise: Professional Summary, Key Skills, Professional Experience, Education, Certifications, Projects, Publications, Additional Information [27].
- Key Skills: one paragraph separated by ` • ` or 2–4 grouped lines (`**Languages:** Python, SQL`).
- No tables, columns, images, icons, text boxes, headers or footers. The format cannot produce them on purpose [27][30].
- Other `doc:` values (`references`, `linkedin`, `interview`, `case-study`, `offer`, `negotiation`) set the Word title and use the same rules and templates; only `cover-letter` gets letter spacing. Write `doc: case-study` (not `case`). For `doc: references`, `--final` refuses to render unless every referee has a consent line; for the exact consent-line wording, see the reference-sheet-builder skill.
- Not supported, so they degrade to plain text: tables (`| a | b |` rows keep their pipes), numbered lists (`1.` lines), `####` headings and code fences. Consecutive lines of this kind become one paragraph separated by line breaks. Write numbered steps as bullets or sentences. An image line (`![alt](file)`) is not embedded; it prints a "Figure: alt (image not embedded)" caption only.
- Links: write `[label](https://url)`. The renderer prints them as visible text so they survive PDF printing and ATS parsing.
- Cover letters: blank lines separate paragraphs. A line containing only `**Re: ...**` becomes the subject line.

## 2. Draft vs final (citations)

| Element | Syntax | Draft render | Final render |
|---|---|---|---|
| Rationale note | line starting with `> ` | yellow "Draft note" | removed |
| Citation marker | `[^3]` | grey superscript | removed |
| Source definition | `[^3]: Source title, publisher, year, URL` | listed under "Draft sources" | removed |
| HTML comment | `<!-- ... -->` | hidden | removed |
| Placeholder | `[Company]`, `XX%`, `TBD`, `<Name>` | shown | **render blocked** (exit code 2) |

- Drafts **include citations** so the user can see why each recommendation was made. Cite only sources listed in `evidence.md`, using its numbers.
- Final products **contain no citations, notes, or placeholders**. Always produce the final with `--final`. It also writes the cleaned Markdown with `--clean-md`.
- Citations go on rationale notes, never inside the candidate's own claims. A citation explains a writing choice; it does not prove the candidate's achievements.

## 3. Templates

All templates are original, single-column, ATS-safe designs. They use real Word heading and list styles, and keep all text in the document body.

| Template | Look | Best for |
|---|---|---|
| `classic` | Centred Georgia header, black rules | Law, finance, government, academia, conservative employers |
| `modern` (default) | Left-aligned Calibri, teal accent | Tech, product, marketing, startups, most corporate roles |
| `minimal` | Arial, black only, no rules | Maximum ATS safety, online portals, any industry |
| `executive` | Centred Cambria, navy, letter-spaced headings, double rule | Director, VP, C-suite, board |
| `compact` | Tight Calibri, plum accent, narrow margins | Students, graduates, 1-page CVs |

- Use the same template for the CV and the cover letter so they form a matched set.
- If the user is unsure, recommend one template based on industry and seniority, and mention one alternative.
- Run `python3 scripts/render_docx.py --list-templates` to show the options.

## 4. Commands

Run scripts by their full installed path from the project root, with input/output under `artifacts/input` and `artifacts/output/<Company>_<Role>/` (or the user's folder), never inside the skill folder. In the examples below, `scripts/...` stands for that full path (e.g. `.agents/skills/cv-builder/scripts/render_docx.py`) and file names are shortened.

```bash
# Draft (keeps notes + citations)
python3 scripts/render_docx.py cv-draft.md -o "Name_CV_DRAFT.docx"

# Final (strips notes/citations, blocks on placeholders, writes clean Markdown)
python3 scripts/render_docx.py cv-draft.md -o "Name_CV.docx" --final --clean-md "Name_CV.md"

# Override front-matter settings
python3 scripts/render_docx.py cv.md -o out.docx --template executive --page letter --lang en-US

# Mechanical checks (word count, metrics ratio, clichés, placeholders, dates, keyword coverage)
python3 scripts/doc_lint.py "Name_CV.docx" --type cv --job job-ad.txt
```

- If `python3` is unavailable, deliver the Markdown and tell the user that the Word file needs Python 3. Do not hand-write the .docx XML.
- PDF: suggest the user export from Word ("Save as PDF"), or, if LibreOffice is installed, run `soffice --headless --convert-to pdf --outdir artifacts/output/<Company>_<Role> artifacts/output/<Company>_<Role>/file.docx`. Without `--outdir` the PDF is written to the current folder (usually the project root). A text-based PDF is fine for most ATS. Never submit a scanned or image-based PDF [28].

## 5. Output files

Name files `Firstname_Lastname_CV.docx` / `Firstname_Lastname_Cover_Letter.docx`. Never use names like "CV_final_v3". A company suffix for a tailored version (`Firstname_Lastname_CV_Acme_v1.docx`) is fine. Save them in `artifacts/output/<Company>_<Role>/` (or the user's folder if they name one), never inside the skill folder. Deliver:

1. **Draft**: `*_DRAFT.md` and `*_DRAFT.docx` (with notes and citations) for review.
2. **Final** (after the user approves): `*.md` and `*.docx` (clean).
