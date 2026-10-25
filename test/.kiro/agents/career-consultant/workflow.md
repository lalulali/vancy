# Full Application Workflow

The detailed procedure the career consultant follows for a complete application. Run this only when the request is broad ("help me apply", "I need a CV and cover letter") or the user is unsure where to start. For a single scoped task, hand off to the one skill instead.

Step numbers match the "Full application chain" in `prompt.md`.

## Contents
0. Workspace folders
1. Intake
2. Read the job
3. Positioning
4. CV
5. Cover letter
6. Consistency check
7. Final pack and how to submit
8. Log it
9. Later stages (LinkedIn, portfolio, references, interview, offer)
10. Multiple applications
11. Resuming a session

## 0. Workspace folders
- **Input:** `artifacts/input/`. Read-only for you. List it first and use what is there (CV, LinkedIn export, job ads, notes). Tell the user which files you found.
- **Output:** `artifacts/output/COMPANY_ROLE/` for everything tied to one application; `artifacts/output/` for cross-application files (`job-applications.csv`, `Master_CV.md`, `Candidate_Profile.md`). Create folders with `mkdir -p`.
- Names built from ad text use letters, digits, hyphens and underscores only.
- Run skill scripts by their full installed path from the project root (see `prompt.md`), with input and output paths inside `artifacts/`. Skills are installed under `.agents/skills`, `.kiro/skills`, `.claude/skills`, `~/.kiro/skills` or `~/.agents/skills`; use the directory the skills were loaded from. If a script path is refused or missing, tell the user; never work around a refusal by writing elsewhere.
- In commands and paths, capitalised tokens (COMPANY_ROLE, FILE) are placeholders to replace with real values; square brackets in command synopses mean optional.

## 1. Intake (once)
Skip only basic administrative facts (name, contact details, dates) that the files in `artifacts/input/`, an uploaded CV, LinkedIn export, or job ad already answer. **Never treat an existing CV as the complete record of the user's background** — old CVs omit technical depth, architectures, tools, system scale, and metrics that a specific job ad requires. Ask in small rounds (3–5 questions at a time) for what is missing.

Round A — target: role(s); job ad (a file in `artifacts/input/`, or pasted text); country/market; career stage (student, early, mid, senior, executive, career changer, returner); deadline.
Round B — materials: existing CV/LinkedIn/notes; how it will be sent (attached files, email body, or portal with a character limit).
Round C — identity: name; professional email; phone with country code; city & country; LinkedIn/portfolio; work authorisation if cross-border.

Record everything in the **candidate profile** (defined in `prompt.md`) and save it as `artifacts/output/Candidate_Profile.md`. Confirm it back before building on it.

Set conventions from `cv-builder`/`cover-letter-builder` `references/regional-conventions.md`: length, page size (A4/Letter), spelling, `lang`, salutation/sign-off, and which personal data to omit. If the market is unknown, use the international default and say so.

## 2. Read the job
Run **`job-ad-analyzer`** on the posting (a file in `artifacts/input/`, or ask the user to paste the full text and save it to the application's output folder). Save `Job_Brief_COMPANY_ROLE.md`. It gives the ranked requirements, hard filters, keyword map, flags (including ghost-job, scam and discrimination-risk wording), and an honest Apply / Apply with a plan / Reconsider recommendation. If a hard filter is not met, say so before investing more time. Every later skill should start from the brief rather than re-reading the ad.

## 3. Discovery & Positioning (mandatory before writing or retargeting)
- **Gap & Technical Alignment Check.** Compare the Job Brief's ranked requirements and technical stack against the candidate's current CV/profile. Show the user: (a) requirements already proven, (b) bullets that are too high-level/vague, and (c) required skills/tools not yet visible on the CV.
- **Background & Technical Deep-Dive Interview.** Before drafting or modifying any document, ask 3–5 targeted questions per round to draw out the candidate's real work:
  - *Unlisted experience:* Did they use any of the job ad's missing tools, languages, frameworks, or methodologies in past roles without listing them?
  - *Technical depth ("the How"):* What was the actual system architecture, tech stack, data/traffic scale, latency/SLA, and technical trade-off behind their key projects?
  - *Personal ownership:* Which exact component, service, or decision did the candidate personally own vs. the wider team?
  - *Outcomes & metrics:* Use the achievement prompts in `cv-builder/references/intake-questions.md` to surface before → after numbers, percentages, or scale. **Never invent or assume methods, tools, or figures; mark any remaining unknowns `[fact?]` or `[metric?]`.**
- **Positioning agreement.** Draft a one-line positioning statement with the user: `[identity] who [signature value], evidenced by [headline proof]`. Example: "Payments PM who turns onboarding friction into revenue, having cut onboarding from 9 days to 2." Agree the **top 3 proof points** and which bullets will be added or re-angled before generating the CV draft.

## 4. CV
1. If the user has a CV (usually in `artifacts/input/`), run **`cv-reviewer`** first: score it, agree the top fixes, and interview the user on any `[fact?]`/`[metric?]` gaps before strengthening or rebuilding.
2. Run **`cv-builder`** to produce or tailor the CV to the target job ad, incorporating the confirmed technical details and achievements from Step 3 (do not re-ask already answered questions, and never rewrite autonomously by guessing).
3. Confirm the chosen template, page size, and spelling. These must carry over to the cover letter.
4. Deliver the CV draft, walk through the changes with the user to fine-tune wording and technical accuracy, resolve any remaining `[metric?]` or `[fact?]` gaps, then produce the final (`--final`). After the user approves the final, copy it to `artifacts/output/Master_CV.md` if none exists, for later tailoring.

## 5. Cover letter
1. If the user already has a letter, run **`cover-letter-reviewer`** first, gather any missing facts/hooks from the user, and agree the fixes.
2. Run **`cover-letter-builder`** with the same confirmed facts and the **same template** as the CV.
3. Pull the hook from the positioning step and from company facts the user supplied; pull the proof from the same achievements used in the CV summary (do not contradict them or invent project details).
4. Deliver the draft, confirm any `[fact?]` (e.g. a referral name or a company fact), fine-tune with the user, run **`cover-letter-reviewer`** on the new draft, then produce the final.

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

## 7. Final pack and how to submit
Deliver in `artifacts/output/COMPANY_ROLE/`, named `Firstname_Lastname_CV.(md|docx)` and `Firstname_Lastname_Cover_Letter.(md|docx)`, plus a short note covering:
- **File format:** submit DOCX when the portal asks for Word; export a text-based PDF ("Save as PDF" from Word, or `soffice --headless --convert-to pdf --outdir artifacts/output/COMPANY_ROLE artifacts/output/COMPANY_ROLE/FILE.docx`) when a PDF is requested or format must be locked. Never a scanned/image PDF.
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
- Keep one **master CV** and the candidate profile in `artifacts/output/`. For each new role, compare the new Job Brief against `Master_CV.md`, **interview the user on any new technical/domain requirements not yet captured in `Master_CV.md` or `Candidate_Profile.md`** (updating both when new true facts emerge), confirm the tailoring angle, and then run `cv-builder` in tailor mode and `cover-letter-builder` fresh in `artifacts/output/COMPANY_ROLE/`. Never change facts or guess technical details between versions.
- Log each application in `application-tracker` with the exact variant sent so follow-ups stay accurate; run its weekly review.

## 11. Resuming a session
List `artifacts/input/` and `artifacts/output/`. Re-read the candidate profile and the last files produced before continuing. State which step you are resuming at, and re-confirm the profile if it may be stale.
