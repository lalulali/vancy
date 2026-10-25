# Career Consultant Agent and Skills: Design (v0.1, draft for review)

Inputs:
- `artifacts/`: 2 ResumeWriter.SG guides, 62 CV samples (58 unique), 27 cover-letter samples, 11 CV templates and 3 CL templates
- `research/corpus/*.md`: corpus analysis
- `research/external-evidence.md`: cited web research

Scope: **worldwide**. Singapore is one locale profile, not the default worldview.

---

## 1. Terminology

"Career consultant" is a correct and widely used term. ResumeWriter.SG calls its own staff "career consultants". The neighbouring terms mean different things:

| Term | Usual meaning | Fit for this project |
|---|---|---|
| Career coach | Guides decisions: direction, transitions, confidence | Partial |
| Resume/CV writer | Produces the documents | Exactly what the 4 skills do |
| **Career consultant** | Umbrella role covering documents, positioning and job-search strategy | **Good name for the agent.** It leaves room to add LinkedIn, interview prep and salary skills later |

Recommendations:
- **Agent:** `career-consultant`.
- **"CV" vs "resume":** use "CV/resume" in descriptions so both trigger the skills. Output uses the locale's word: "resume" for US/CA, "CV" elsewhere.
- **"Reviewer & strengthener":** keep the meaning but shorten the name to `*-reviewer`. The description states that it scores, redlines **and** produces a strengthened version.

## 2. How the skills are segregated

### Decision: 4 skills, split along two axes

| | Build (no document yet, or a rough one) | Review & strengthen (existing document) |
|---|---|---|
| **CV/Resume** | `cv-builder` | `cv-reviewer` |
| **Cover letter** | `cover-letter-builder` | `cover-letter-reviewer` |

Why the split holds:
- **Builders and reviewers have different inputs, workflows and outputs.**
  - A builder interviews the user, pulls out achievements, then drafts.
  - A reviewer parses a document, scores it, redlines it, then rewrites.
  - Combining them would make every trigger load both workflows.
- **CVs and cover letters follow different rules.**
  - A CV is factual, skimmable and keyword-dense.
  - A cover letter is a persuasive story of 250–400 words, built around the company's pain points.
  - Corpus finding: in 9 of 27 letters the contact details didn't match the header, and boilerplate openers were reused 15×. Those failure modes only matter for letters.

### Shared knowledge with a single source of truth

All four skills need the same locale rules, evidence, ethics and data model. Kiro skills should be self-contained (files outside the skill folder are undocumented and not portable). So:

- **Source of truth:** `kb/` at the repo root.
- **Sync step:** `scripts/sync_kb.py` copies the needed `kb/` files into each skill's `references/` (and `scripts/` where relevant). Copies are never edited by hand.
- **Builders reuse the reviewer's checks.** Each builder runs the reviewer's rubric and linter as its final QA step, so "build" output already passes "review".

### Handoffs

```
           ┌──────────── career-consultant (agent: intake, routing, memory) ───────────┐
           │                                                                            │
 user CV / notes ─► cv-builder ──► CV ──► cv-reviewer ──► strengthened CV ──┐           │
           │                                                               ├─► cover-letter-builder ─► CL ─► cover-letter-reviewer
 job ad (JD) ──────────────────────────────────────────────────────────────┘           │
           └────────── shared files: profile.yaml + target.yaml (per candidate) ───────┘
```

## 3. Knowledge each skill needs, by topic

### 3.1 CV builder

| Topic | Rule (source) |
|---|---|
| Section order | Header → Summary → Key Skills → Experience (each role: scope bullet, duties, achievements) → Education & Certifications → Technical Skills → Additional Info. Used in 55/58 corpus CVs. Graduates put Education first (corpus annotation). |
| Header | Name, target title (mirroring the JD title), phone in E.164, email, LinkedIn, city/country. Personal data is set by the locale (§5). |
| Summary | 3–5 bullets, about 100 words: identity + years + domains + brands/regions, then up to 3 metric-backed highlights. Write it **last** (guide; corpus median 4 bullets / 100 words). |
| Key Skills | 6–16 hard skills, ordered by value and grouped. Mirror JD keywords *in context*, no stuffing (corpus; E2). |
| Experience | First bullet = scope: team, budget, geography, reporting line. 3–6 bullets for the current role. Older roles shrink. Roles more than 10–15 years old get title, company and dates only (corpus). Present tense for the current role, past tense otherwise. |
| Achievements | Formula: "Accomplished X as measured by Y by doing Z", with baseline and timeframe (E5). Metric prompts: revenue, cost, time, scale, quality, risk. Ranges or % are fine for confidential figures (corpus). |
| Length | Set by locale and seniority: US juniors 1 page, otherwise 2. 2 pages is the general default (E3). 2–3 pages for senior roles in SG/UK/AU (guide; L4). Hard cap of 2 pages for US federal roles (E4). |
| Format | Single column, no tables or text boxes, standard headings, a safe font, month-name dates (E2, E11; template analysis). |

### 3.2 CV reviewer & strengthener

The reviewer needs the same knowledge as the builder, plus a **scorecard** and a **deterministic linter**. The linter's checks come from defects actually found in the corpus:
- leftover placeholders (`XX%`, `[industries]`)
- contact details that differ between sections
- summary metrics that contradict the role bullets
- "100%" claims with no baseline
- weak openers ("Responsible for", "Assisted", "Handled")
- clichés ("excellent interpersonal skills" ×25)
- spelling that mixes en-GB and en-US within one document
- inconsistent currency or dash formats
- tense slips
- a skills list copied from another CV
- typos (E7: about 6 in 10 hiring managers would dismiss for them)

### 3.3 Cover letter builder

| Topic | Rule (source) |
|---|---|
| Structure | Header (identical to the CV) → [date and recipient block, by locale] → named salutation → [subject line, by locale] → P1 hook + narrative → P2 current role + one key achievement placed last → P3 company-specific value and pain points → CTA → sign-off by locale (guide; corpus). |
| Length | 250–400 words, 4–5 blocks, 1 page maximum (guide; corpus median 341). |
| Tailoring | At least 1 verifiable company fact (web research), at least 1 JD priority addressed, 30–50% of content unique to the job (guide). Tailored letters get about 53% more callbacks; generic ones add almost nothing (E12). |
| Voice | Personable but professional. Lead with value to the employer, not the candidate's wishes. Ban the corpus boilerplate ("It is with great enthusiasm…", "ideal candidate", "renowned firm" with no evidence) (corpus; E13–E14). |
| Situations | Career switch, return after a gap, fresh graduate, referral, internal move, email-as-letter (guide FAQ; corpus Family B). |
| Never | Salary or ID numbers unless asked. Don't criticise the current employer. Don't sound desperate (guide). |

### 3.4 Cover letter reviewer & strengthener

Scorecard and linter. CL-specific checks:
- company name and role match the target in every mention
- contact details match the CV header
- the company compliment is a verifiable fact, not flattery (the guide calls this "bootlicking")
- there is exactly one CTA
- the sign-off suits the salutation (e.g. "Yours faithfully" goes with "Dear Sir/Madam" in en-GB)
- word count
- repetition of the CV (the guide says to expand on it, not copy it)

## 4. Shared data model

The files live in `candidates/<slug>/` in the workspace. They are local only, never uploaded.

```yaml
# profile.yaml: master career inventory, reused across applications
person: {name, email, phone_e164, city, country, linkedin, citizenship?, work_rights?}
headline_options: []
roles:
  - {title, employer, employer_blurb?, location, start: 2021-03, end: present,
     scope: {team: 12, budget: "USD 2M", geography: "APAC (7 markets)", reports_to: "CFO"},
     duties: [], achievements: [{x, y_metric, z_method, baseline?, timeframe?, confidential: bool, verified: bool}]}
education: [{degree, field, institution, country, year, honours?}]
certifications: [{name, issuer, year, status: done|in_progress}]
skills: {hard: [], tools: [], languages: [{name, level}]}
extras: {notice_period?, availability?, interests?, publications?, volunteering?}

# target.yaml: one per application
job: {title, company, location, locale_profile: us|uk-ie|sg|..., seniority, jd_text}
analysis: {must_have_keywords: [], nice_to_have: [], top_priorities: [], pain_points: [], company_facts: [{fact, source_url}]}
choices: {doc_length, template, spelling: en-GB|en-US|en-AU|en-CA, include: {photo: false, dob: false, nationality: false}}
```

Rules:
- **Achievements:** an achievement marked `verified: false` is never written as fact. It appears as `[[CONFIRM: …]]` until the user confirms it.
- **Company facts:** each one stores its source URL.

## 5. Locale profiles (worldwide)

Each profile is resolved from the **job's location**, not from the candidate's nationality. Every default can be overridden. Evidence IDs refer to `research/external-evidence.md`.

| Profile | Doc name / length | Photo | DOB / marital | Nationality / work rights | Spelling | Letter specifics | Evidence |
|---|---|---|---|---|---|---|---|
| `us` | Resume, 1 p (<5–10 yrs) to 2 p. Federal: 2 p hard cap | No | No | Work authorisation if relevant | en-US | No subject line; "Sincerely" | L1, E3, E4 |
| `ca` | Resume, 2 p | No | No | Work permit if relevant | en-CA | As US | L3 |
| `uk-ie` | CV, 2 p | No | No | Right to work if relevant | en-GB | "Yours sincerely" (named) or "Yours faithfully" (Sir/Madam) | L2 |
| `au-nz` | Resume/CV, 2–3 p; government roles may need selection criteria | No | No | Visa/work rights common | en-AU | Referees often named or "on request" | L4 |
| `sg` | CV, 2 p (≤3 senior) | No | No | Nationality/PR commonly shown (work-pass rules). WFA takes effect by end-2027: show only if useful | en-GB | Subject line "Application for the Position of …"; notice period in Additional Info | Corpus, L5 |
| `de-dach` | Lebenslauf, tabular, 1–2 p | Optional (common) | Optional | Optional | de / en | Formal; date and place line | L6 |
| `fr` | CV, 1–2 p | Optional | Optional | Optional | fr / en | Formal *lettre de motivation* | L7 |
| `eu-europass` | Europass structure | Optional | Optional | Optional | per language | — | L8 |
| `in` | Resume, 1–2 p; freshers lead with objective + projects | Optional | Optional | — | en-IN (≈ en-GB) | Optional declaration line | L11 |
| `gcc` | CV, 2 p | Common | Sometimes | Nationality and **visa status** expected | en-GB | Notice period / availability | L10 |
| `jp` | Rirekisho (JIS form) + shokumu keirekisho | Required (rirekisho) | Required (rirekisho) | Visa status | ja / en | **v1: shokumu keirekisho in English only; rirekisho is out of scope** | L9 |
| `intl` (fallback) | CV, 2 p | No | No | Work rights only if asked | user choice | Neutral | — |

Rows graded C in the evidence file are conventions. The skills present them as "common practice", never as law.

## 6. Skill designs

All four skills share three rules:
- Ask only for what is missing.
- Never invent employers, titles, dates, metrics or company facts.
- Output Markdown first, then optionally a DOCX built by script.

### 6.1 `cv-builder`
**Triggers:** write, create, build or tailor a CV/resume; convert a CV to another country's format; turn a LinkedIn profile or notes into a CV.

**Workflow:**
1. Intake: target role/JD, job location (→ locale profile), seniority, existing material.
2. Analyse the JD → `target.yaml`.
3. Achievement interview using metric prompts (≤5 questions per round) → `profile.yaml`.
4. Draft experience → achievements → skills → summary, writing the summary last.
5. Apply the locale profile.
6. Self-QA with the reviewer linter and rubric; fix everything the rubric marks as must-fix.
7. Render: `.md` → `.docx` (style-donor template).
8. Hand off: offer a cover letter.

**Bundled files:**
- `references/`: cv-rules.md, section-patterns.md, achievement-prompts.md, verb-bank.md, locales/*.md, rubric.md, evidence.md
- `scripts/`: build_docx.py, lint_cv.py
- `assets/templates/`: 3 ATS-safe templates (§7)

### 6.2 `cv-reviewer`
**Triggers:** review, critique, score, improve, strengthen, "why am I not getting interviews", ATS check.

**Workflow:**
1. Extract text from PDF/DOCX (fitz/zipfile).
2. Detect or confirm the locale and target JD.
3. Run `lint_cv.py`, which does the deterministic checks.
4. Score against the rubric.
5. Write a prioritised redline: must-fix → high-impact → polish. Each item shows the issue, why it matters (with a cited reason) and the rewrite.
6. Produce the strengthened version. Unconfirmed metrics appear as `[[CONFIRM]]`.
7. Before/after score.

**CV rubric (100):**

| Dimension | Points |
|---|---|
| Targeting & keywords | 20 |
| Impact & evidence | 25 |
| Top-third skimmability | 15 |
| Language & clarity | 15 |
| ATS/format | 10 |
| Locale & compliance | 10 |
| Integrity/consistency | 5 |

**Gates** that cap the score at 60 until fixed: typos, placeholders, contradictions, prohibited personal data for the locale.

### 6.3 `cover-letter-builder`
**Triggers:** write or tailor a cover letter, motivation letter, application email or *lettre de motivation*.

**Prerequisites:** a CV/profile and a JD. If the CV is missing, build a minimal profile first.

**Workflow:**
1. Pick the situation type: standard, switcher, gap, graduate, referral, internal, email.
2. Research the company on the web: 2–3 verifiable facts with URLs.
3. Map JD priorities and pain points → CV proof points.
4. Draft P1 hook, P2 proof, P3 value, CTA.
5. Apply locale header, salutation and sign-off.
6. Anti-boilerplate pass.
7. QA with the CL linter and rubric.
8. Render.

**Bundled files:**
- `references/`: cl-rules.md, situations.md, phrase-bank.md (adapted, tagged by locale), banned-phrases.md, locales/*.md, rubric.md, evidence.md
- `scripts/`: lint_cl.py, build_docx.py

### 6.4 `cover-letter-reviewer`
**Workflow:** same as `cv-reviewer`, with these differences:

**CL rubric (100):**

| Dimension | Points |
|---|---|
| Company & role specificity | 25 |
| Value to employer | 20 |
| Evidence | 20 |
| Hook & structure | 15 |
| Authentic voice (no boilerplate or AI tells) | 10 |
| Length/locale/format | 10 |

**Gates:** wrong company or role name, contact mismatch with the CV, placeholders, more than 1 page.

## 7. Templates and IP

- **No verbatim copies.** ResumeWriter.SG samples and templates are third-party copyrighted material. Professional Black also carries a Hloom copyright footer, and Timeless Black has an advert page. The skills ship **derived patterns and our own example text**, not verbatim samples. Short quotes stay in `research/` only.
- **Generation method.** Placeholder replacement doesn't work: the template text is split across XML runs (see the template analysis). Instead, use our own clean template inspired by the ATS-safe layouts (Simple Green, Professional Blue, Simple Violet) as a style donor, and generate `document.xml` from Markdown/YAML.
- **Variants:** `classic` (conservative industries), `modern` (tech), `graduate` (education first). Page size follows the locale: Letter for US/CA, A4 elsewhere.

## 8. Agent: `career-consultant`

- **Files:** `.kiro/agents/career-consultant.json` + `.kiro/agents/prompts/career-consultant.md`
- **Resources:** `skill://.kiro/skills/*/SKILL.md`. Skills are listed explicitly because the docs disagree on whether they are inherited.
- **Tools:** read, write (restricted to `candidates/**`), shell (render/lint scripts), web (company research).
- **Behaviour:**
  1. Intake: goal, target role, **job country**, seniority, documents.
  2. Route to the right skill.
  3. Keep `profile.yaml` as memory across applications.
  4. Enforce the ethics rules below.
- **Ethics (system prompt):**
  - Never fabricate.
  - Flag claims that can't be verified.
  - Respect NDAs (use ranges).
  - Don't add personal data the locale treats as discriminatory.
  - Say clearly that output is AI-assisted and must be edited in the user's voice (E13).
  - Not legal or immigration advice.
- **Future skills:** LinkedIn profile, interview prep (an `interview-prep-generator` skill already exists in this environment), salary negotiation, selection-criteria responses (AU government), academic CV.

## 9. Repo layout (target)

```
.kiro/agents/career-consultant.json
.kiro/agents/prompts/career-consultant.md
.kiro/skills/{cv-builder,cv-reviewer,cover-letter-builder,cover-letter-reviewer}/
kb/                      # source of truth: locales/, rubrics/, rules/, evidence.md, linters/
scripts/sync_kb.py       # copies kb → each skill's references/ and scripts/
research/                # evidence and corpus analysis (not shipped)
candidates/              # user data (gitignored)
evals/                   # 3 personas × 4 locales × 4 skills test prompts and expected checks
```

## 10. Build plan

| Phase | Deliverable | Exit check |
|---|---|---|
| 1 ✅ | Research: corpus analysis, cited evidence, this design | User approval of this doc |
| 2 | `kb/`: locale profiles, rubrics, rules, linters (with tests) | Linters catch the 10+ defect types found in the corpus samples |
| 3 | `cv-builder` + `cv-reviewer` + DOCX renderer | `quick_validate.py` passes. Evals: fresh grad (in), mid-level (uk-ie), senior (sg), switcher (us) |
| 4 | `cover-letter-builder` + `cover-letter-reviewer` | Same eval personas. Letters score ≥80 and pass all gates |
| 5 | `career-consultant` agent + end-to-end eval | Full flow JD → CV → CL → review in one session |

## 11. Open decisions for the user

1. **Output formats:** Markdown + DOCX (proposed)? Do you also need PDF? PDF needs LibreOffice, which isn't checked yet.
2. **Languages:** English only in v1 (proposed), with German/French/Japanese output later?
3. **Japan:** is the rirekisho in scope, or English shokumu keirekisho only (proposed)?
4. **Templates:** OK to design our own clean templates instead of redistributing the ResumeWriter/Hloom files (proposed)?
5. **Location:** workspace-level skills (`.kiro/skills/`, proposed) or global (`~/.kiro/skills/`)?
