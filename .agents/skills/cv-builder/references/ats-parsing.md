# How ATS Parse Documents (and What Survives)

An applicant tracking system (ATS) is the software most employers use to receive, parse, store, search, and rank applications. Writing for it is about **clean parsing and honest keyword relevance**, not tricks. Source numbers refer to `evidence.md`.

## Contents
1. What an ATS actually does
2. Myths vs facts
3. What parses cleanly
4. What breaks parsing
5. File format
6. Keyword relevance (done honestly)
7. Quick pre-submit checklist

## 1. What an ATS actually does
- Ingests the file and extracts text into fields: contact, work history (employer, title, dates), education, skills [27][2].
- Lets a recruiter search and filter the pool by keywords, titles, and dates; may rank by match [2][19].
- Stores the parsed record. If parsing scrambles your dates or drops a job, a recruiter sees the scrambled version.
- Most systems **rank and surface**; they rarely auto-reject on content. A human still decides [19][2].
  - In a small US study of 25 recruiters, most said their ATS ranks and sorts but does not reject on content (2 of 25 had content auto-reject switched on) [19]. Practice varies by employer and some use AI match scores to rank or filter [19][25], so write for both the parser and the human.
- The automatic filters that do exist are **knockout questions** (work authorisation, licence or certification, location, minimum education) and **low-rank placement** in high-volume roles, where a low match score can mean nobody reads the application [19]. Answer knockout questions truthfully and exactly as asked; a wrong "no" can end the application, and a false "yes" is a lie.

## 2. Myths vs facts
| Claim | Reality |
|---|---|
| "75% of resumes are rejected by the ATS before a human sees them." | Unsupported. The figure traces to a 2012 sales pitch by Preptel, a vendor that closed in 2013 [18]. In a small, vendor-run US study of 25 recruiters, 23 said their ATS does not auto-reject on format or content [19]. |
| "You must match the job ad word-for-word." | No. Match genuine, relevant terms; keyword *stuffing* and copying the ad's wording are named as problems by recruiters [5][8]. |
| "Hidden white-text keywords beat the ATS." | They're extracted as normal text, look like manipulation to a recruiter, and are treated as an integrity problem [32]. |
| "A fancy template ranks higher." | Parsing cares about structure, not decoration; complex layouts hurt [5][27][30]. |
| "PDFs are always rejected." | Most modern ATS read text-based PDFs. Image/scanned PDFs fail. DOCX is the safest default [26][28]. |

## 3. What parses cleanly
- A single column, top to bottom.
- Standard section headings: Professional Summary / Summary, Key Skills / Skills, Professional Experience / Experience, Education, Certifications, Projects, Publications.
- Real text for everything, including name and contact details (in the body, not a header/footer).
- Each role as: Title — Employer — Location — Mon YYYY–Mon YYYY, on text lines.
- Standard bullet characters (•, -). Common fonts. 10–12 pt body.

## 4. What breaks parsing
| Element | Why it breaks | Instead |
|---|---|---|
| Tables / multi-column | Text is read in the wrong order or merged | One column; the bundled `render_docx.py` guarantees this |
| Text boxes | Often skipped entirely | Body text |
| Header/footer content | Many parsers ignore it — losing your phone/email | Contact line in the body |
| Images, logos, icons, photos, skill bars | Carry no extractable text | Words; drop the photo unless the market requires it |
| Graphics-based charts of "proficiency" | Meaningless to a parser and to a reader | State the level in words (e.g. "Spanish — professional") |
| Non-standard headings ("My Journey") | Not mapped to a known field | Standard headings |
| Unusual fonts / tiny text / dense colour | Mis-extraction, poor OCR, low readability | Standard fonts, adequate size and contrast [63] |
| Abbreviated titles ("Sr. Acct Exec") | Weak keyword and title matching | Spell out in full [27] |

## 5. File format
- **DOCX** is the safest universal choice for a parser.
- **PDF** (text-based) when the portal asks for PDF or you must lock formatting; confirm text is selectable.
- Never a scanned or image-only PDF [28].
- File name: `Firstname_Lastname_CV.docx`.

## 6. Keyword relevance (done honestly)
- Pull the real skills, tools, and titles from the job ad; use the ones that are genuinely true of you, in the ad's wording (e.g. "stakeholder management" if that's the ad's phrase) [2][41].
- Place them where they belong: Key Skills, the scope bullet, and achievement bullets — not a hidden block.
- Spell out an acronym once with its expansion so both forms match ("SEO (search engine optimisation)").
- Mirror the exact job title in your headline when it truthfully reflects your role.
- Do **not** paste whole sentences from the ad, repeat a term unnaturally, or list skills you lack [5][8].
- Method in short: list the ad's must-haves, mark which ones the user can evidence, and use the ad's wording only for those. Never add the rest. Keyword coverage is information, not a score to maximise.

## 7. Quick pre-submit checklist
- [ ] Single column, standard headings, text-only (no tables/boxes/images).
- [ ] Contact details in the body; selectable in the exported file.
- [ ] Titles, employers, and dates on clean text lines; dates consistent.
- [ ] Relevant job-ad terms present naturally; no stuffing or hidden text.
- [ ] DOCX (or a text-based PDF if required); sensible file name.
- [ ] `doc_lint.py` on the .docx shows no tables/text boxes/images and no header/footer text.
