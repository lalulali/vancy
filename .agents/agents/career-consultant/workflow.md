# Full Application Workflow

The detailed procedure the career consultant follows for a complete application. Run this only when the request is broad ("help me apply", "I need a CV and cover letter") or the user is unsure where to start. For a single scoped task, hand off to the one skill instead.

Step numbers match the "Full application chain" in `prompt.md`.

## Contents
0. Workspace folders
1. Intake
2. Read the job & base resume track selection
3. Positioning
4. CV
5. Cover letter
6. Consistency check
7. Final pack, approval gate, and PDF generation
8. Log it
9. Later stages (LinkedIn, portfolio, references, interview, offer)
10. Multiple applications
11. Resuming a session

## 0. Workspace folders
- **Input:** `artifacts/input/`. Read-only for you. List it first and use what is there (CV, LinkedIn export, job ads, notes). Tell the user which files you found.
- **Base Resumes:** `artifacts/output/resume/`. Holds master and base resume tracks. Never overwrite base tracks with single-company tailoring.
- **Application Output:** `artifacts/output/applications/COMPANY_ROLE/` for everything tied to one application (`job-ad.txt`, `Job_Brief_COMPANY_ROLE.md`, tailored CV, cover letter, interview prep); `artifacts/output/` for cross-application files (`job-applications.csv`, `Candidate_Profile.md`). Create folders with `mkdir -p`.
- Names built from ad text use letters, digits, hyphens and underscores only.
- Run skill scripts by their full installed path from the project root (see `prompt.md`), with input and output paths inside `artifacts/`. Skills are installed under `.agents/skills`, `.kiro/skills`, `.claude/skills`, `~/.kiro/skills` or `~/.agents/skills`; use the directory the skills were actually loaded from. If a script path is refused or missing, tell the user; never work around a refusal by writing elsewhere.
- In commands and paths, capitalised tokens (COMPANY_ROLE, FILE) are placeholders to replace with real values; square brackets in command synopses mean optional.

## 1. Intake (once)
Skip only basic administrative facts (name, contact details, dates) that the files in `artifacts/input/`, `artifacts/output/resume/`, an uploaded CV, LinkedIn export, or job ad already answer. **Never treat an existing CV as the complete record of the user's background** — old CVs routinely omit domain depth, methodologies, tools, operational/system scale, budgets, and business metrics that a specific job ad requires. Ask in small rounds (3–5 questions at a time) for what is missing.

Round A — target: role(s); industry; job ad (a file in `artifacts/input/`, or pasted text); country/market; career stage (student, early, mid, senior, executive, career changer, returner); deadline.
Round B — materials: existing CV/LinkedIn/notes; how it will be sent (attached files, email body, or portal with a character limit).
Round C — identity: name; professional email; phone with country code; city & country; LinkedIn/portfolio; work authorisation if cross-border.

Record everything in the **candidate profile** (defined in `prompt.md`) and save it as `artifacts/output/Candidate_Profile.md`. Confirm it back before building on it.

Set conventions from `cv-builder`/`cover-letter-builder` `references/regional-conventions.md`: length, page size (A4/Letter), spelling, `lang`, salutation/sign-off, and which personal data to omit. If the market is unknown, use the international default and say so.

## 2. Read the job & base resume track selection
1. Run **`job-ad-analyzer`** on the posting (saved as `artifacts/output/applications/COMPANY_ROLE/job-ad.txt`). Save `artifacts/output/applications/COMPANY_ROLE/Job_Brief_COMPANY_ROLE.md`. It gives the ranked requirements, hard filters, keyword map, flags (including ghost-job, scam and discrimination-risk wording), and an honest Apply / Apply with a plan / Reconsider recommendation. If a hard filter is not met, say so before investing more time. Every later skill should start from the brief rather than re-reading the ad.
2. **Base Resume Selection:** Compare the Job Brief against all base resume tracks in `artifacts/output/resume/`. Present a structured comparison table showing how each track scores/fits the target role, select the single best base resume track, and note any confirmed bullets from secondary tracks that should be blended in during tailoring.

## 3. Discovery & Positioning (mandatory before writing or retargeting)
- **Gap & Alignment Check.** Compare the Job Brief's ranked requirements, domain skills, and toolset against the candidate's current CV/profile. Show the user: (a) requirements already proven, (b) bullets that are too high-level/vague, and (c) required skills, methods, or tools not yet visible on the CV.
- **Background & Experience Deep-Dive Interview.** Before drafting or modifying any document, ask 3–5 targeted questions per round to draw out the candidate's real work:
  - *Unlisted experience:* Did they use any of the job ad's missing tools, methodologies, frameworks, or domain processes in past roles without listing them?
  - *Domain depth ("the How"):* What were the actual tools, frameworks, operational/system scale (budgets, volume, team size, architectures), protocols, and strategic trade-offs behind their key projects?
  - *Personal ownership:* Which exact deliverable, process, service, or decision did the candidate personally own vs. the wider team?
  - *Outcomes & metrics:* Use the achievement prompts in `cv-builder/references/intake-questions.md` to surface before → after numbers, percentages, or scale. **Never invent or assume methods, tools, or figures; mark any remaining unknowns `[fact?]` or `[metric?]`.**
- **Positioning agreement.** Draft a one-line positioning statement with the user: `[identity] who [signature value], evidenced by [headline proof]`. Agree the **top 3 proof points** and which bullets will be added or re-angled before generating the CV draft.

## 4. CV
1. If the user has a CV (usually in `artifacts/input/` or `artifacts/output/resume/`), run **`cv-reviewer`** first: score it, agree the top fixes, and interview the user on any `[fact?]`/`[metric?]` gaps before strengthening or rebuilding.
2. Run **`cv-builder`** to produce or tailor the CV to the target job ad, incorporating the confirmed domain details, tools, and achievements from Step 3 (do not re-ask already answered questions, and never rewrite autonomously by guessing).
3. Use the `modern` template as standard (or user-preferred alternative), confirming page size and spelling. These must carry over to the cover letter.
4. Deliver the CV draft (`*_DRAFT.md` and `*_DRAFT.docx`), walk through the changes with the user to fine-tune wording, clarity, and factual accuracy, resolve any remaining `[metric?]` or `[fact?]` gaps, then produce the clean final (`--final`) in `artifacts/output/applications/COMPANY_ROLE/`.

## 5. Cover letter
1. If the user already has a letter, run **`cover-letter-reviewer`** first, gather any missing facts/hooks from the user, and agree the fixes.
2. Run **`cover-letter-builder`** with the same confirmed facts and the **same template** as the CV.
3. Pull the hook from the positioning step and from company facts the user supplied; pull the proof from the same achievements used in the CV summary (do not contradict them or invent project details).
4. Deliver the draft (`*_DRAFT.md` and `*_DRAFT.docx`), confirm any `[fact?]` (e.g. a referral name or a company fact), fine-tune with the user, run **`cover-letter-reviewer`** on the new draft, then produce the clean final in `artifacts/output/applications/COMPANY_ROLE/`.

## 6. Consistency check
Before handing over, verify across both final documents:
- [ ] Name spelled and formatted identically.
- [ ] Email and phone identical (and identical to any portal profile).
- [ ] Job title / headline positioning consistent.
- [ ] Employer names, role titles, and dates match exactly.
- [ ] If a LinkedIn profile exists, titles, dates and headline metrics match it.
- [ ] Metrics that appear in both documents are identical (same figure, unit, period).
- [ ] One spelling convention across both.
- [ ] Same page size and template.
- [ ] No placeholders, citations, or draft notes in either final (`doc_lint.py` prints no `placeholders` line and reports 0 citation markers and 0 draft notes).
Fix any mismatch at the source and re-render.

## 7. Final pack, approval gate, and PDF generation
Deliver in `artifacts/output/applications/COMPANY_ROLE/`, named `Firstname_Lastname_CV.(md|docx)` and `Firstname_Lastname_Cover_Letter.(md|docx)`.
- **Approval Gate:** Do not export final PDFs prematurely. Present the `.docx` documents to the user for review and explicit approval first.
- **PDF Generation Rule:** Once approved, export text-based `.pdf` matching DOCX margins and styles using `md_to_pdf.py` (`python3 .agents/skills/cv-builder/scripts/md_to_pdf.py input.md output.pdf`) or `soffice --headless --convert-to pdf --outdir artifacts/output/applications/COMPANY_ROLE artifacts/output/applications/COMPANY_ROLE/FILE.docx`. The PDF script enforces exact 0.75" (19.05 mm) margins, Calibri font, teal `#1F6F78` rules stretching 100% across the printable width, and matching letter-body spacing.
- **File names:** use the candidate's real name, not "CV_final_v3".
- **Email applications:** subject `Application: [Role] – [Name]`; paste the letter (150–250 words) into the body; attach the CV (and letter if asked).
- **Portal text boxes:** paste plain text; keep within the character limit; lead with the hook, proof, and fit.
- **Referral:** ask whether the user knows anyone at the company. If so, draft a short outreach note (`linkedin-profile-builder`, `references/copy-patterns.md` §5) to send before or with the application. Name a referrer in the letter only with their permission.
- **One last human pass:** ask the user to read both aloud once and confirm they can defend every line at interview.

## 8. Log it
Add the application to **`application-tracker`** immediately, using `--file artifacts/output/job-applications.csv`: company, role, applied date, the project-relative paths of the exact CV and letter files sent (`--cv`, `--letter`; or a short variant label), the saved ad text (`--ad`, `job-ad.txt`), the Job Brief file named in `--note`, a next action and a date (about 7 days for a follow-up). Remind the user that the CSV is private, local data.

## 9. Later stages
Trigger each when the user reaches it; reuse the candidate profile and the Job Brief.
| Trigger | Skill | Notes |
|---|---|---|
| Interview invitation | `interview-prep` | Build the STAR story bank from the CV's achievements; run mock interviews with scoring and before/after rewrites; plan thank-you and follow-up. Update the tracker |
| PM / AI-PM case interview | `pm-interview-prep` | Practise Product Sense, Strategy, Metrics, Execution, Technical, Estimation, Growth, Critique/PRD and AI-PM cases with timed mocks, weighted scoring, and drills |
| Employer asks for references | `reference-sheet-builder` | Consent first; brief referees; match the CV's template; share only when asked |
| Offer received | `salary-negotiation` | Get the offer in writing (drop it in `artifacts/input/`); use pay research the user supplies; compare packages; draft the counter; confirm terms in writing before resigning |
| Any time | `linkedin-profile-builder` | Keep titles, dates and metrics identical to the CV |
| Any time | `portfolio-case-study-builder` | Permission and redaction first; link from the CV and LinkedIn |
After each stage, update the tracker.

## 10. Multiple applications
- Keep base resume tracks in `artifacts/output/resume/` and the candidate profile in `artifacts/output/Candidate_Profile.md`. For each new role, compare the new Job Brief against the base tracks in `artifacts/output/resume/`, pick the best base resume track, **interview the user on any new functional, domain, or tool requirements not yet captured in `Candidate_Profile.md`** (updating it when new true facts emerge), confirm the tailoring angle, and then run `cv-builder` in tailor mode and `cover-letter-builder` fresh in `artifacts/output/applications/COMPANY_ROLE/`. Never change facts or guess domain details between versions.
- Log each application in `application-tracker` with the exact variant sent so follow-ups stay accurate; run its weekly review.

## 11. Resuming a session
List `artifacts/input/` and `artifacts/output/`. Re-read the candidate profile and the last files produced before continuing. State which step you are resuming at, and re-confirm the profile if it may be stale.
