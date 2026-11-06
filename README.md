# Vancy — AI Career Consultant & Agent Skills

> **Language**: [English](README.md) | [中文](README.zh-CN.md)  
> **User Guide**: [GUIDE.md](GUIDE.md) | [GUIDE.zh-CN.md](GUIDE.zh-CN.md)  
> **AI Workflow Specification**: [WORKFLOW.md](WORKFLOW.md) | [WORKFLOW.zh-CN.md](WORKFLOW.zh-CN.md)

**Vancy** is an open-source, full-lifecycle career consulting suite and AI agent for job seekers, software engineers, product managers, and leaders. It covers the entire journey: reading the job ad, CV and cover letter tailoring, LinkedIn presence, portfolio case studies, reference checks, behavioral and PM interviews, offer negotiation, and pipeline tracking.

Unlike generic AI tools that hallucinate skills or output buzzword-filled summaries, Vancy enforces a **Discovery-First, Truth-Based** workflow: it interviews you about your real engineering architecture, metrics, and technical contributions before authoring or modifying any document.

---

## 1. The Twelve Skills

Every skill is standalone (`SKILL.md` + `references/` + `scripts/` + `assets/`) and compliant with the [Agent Skills specification](https://agentskills.io).

| Stage | Skill | What It Does | Output Formats |
|---|---|---|---|
| **Targeting** | [`job-ad-analyzer`](.agents/skills/job-ad-analyzer) | Deconstructs job postings into a 1-page Job Brief: why the role exists, ranked requirements, hard filters, keyword map, red-flag detection (ghost jobs, scams), and an honest apply recommendation. | Markdown |
| **Documents** | [`cv-builder`](.agents/skills/cv-builder) | Builds tailored, ATS-compliant CVs from your background notes, raw resume, or LinkedIn export. Formats quantified bullets using active strong verbs. | Markdown + Word (.docx) |
| | [`cv-reviewer`](.agents/skills/cv-reviewer) | Scores a CV out of 100 across 8 dimensions (targeting, skim clarity, metrics, language, structure, ATS parsing, consistency, bias safety), ranking fixes with before/after rewrites. | Markdown + Word (.docx) |
| | [`cover-letter-builder`](.agents/skills/cover-letter-builder) | Writes a tailored 1-page cover letter matching the company's pain points, plus email and job-portal variants. Visual styles match the CV. | Markdown + Word (.docx) |
| | [`cover-letter-reviewer`](.agents/skills/cover-letter-reviewer) | Scores a letter, flags generic fluff that could be sent to any company, and rewrites it with punchy proof. | Markdown + Word (.docx) |
| **Presence** | [`linkedin-profile-builder`](.agents/skills/linkedin-profile-builder) | Generates recruiter-searchable Headline, About section, experience entries, skills, and outreach messages with character-limit linters. | Markdown + Word (.docx) |
| | [`portfolio-case-study-builder`](.agents/skills/portfolio-case-study-builder) | Turns projects into structured case studies (problem, constraints, architecture trade-offs, metrics) with confidentiality checks. | Markdown + Word (.docx) |
| | [`reference-sheet-builder`](.agents/skills/reference-sheet-builder) | Prepares professional referee sheets and outreach templates. Blocks final document generation until referee consent is recorded. | Markdown + Word (.docx) |
| **Interviews** | [`interview-prep`](.agents/skills/interview-prep) | Builds STAR story banks from your real achievements, runs interactive mock interviews with scoring and before/after rewrites, and prepares follow-ups. | Markdown + Word (.docx) |
| | [`pm-interview-prep`](.agents/skills/pm-interview-prep) | PM case-interview coaching (traditional & AI PM): Product Sense, Strategy, Metrics, Execution, Technical, Estimation, and AI-PM topics with timed mocks & rubrics. | Markdown + Word (.docx) |
| **Offers** | [`salary-negotiation`](.agents/skills/salary-negotiation) | Compares offers on Total Compensation (base, bonus, equity/RSUs, signing bonus), positions offers in researched pay ranges, and drafts counteroffer scripts. | Markdown + Scripts |
| **Tracking** | [`application-tracker`](.agents/skills/application-tracker) | Local, private CSV tracker with follow-up reminders, weekly review summaries, and pipeline conversion funnel statistics. | CSV + Terminal |

---

## 2. The Career Consultant Agent ("Clara")

A master agent orchestrates these twelve skills in sequence:

```
[Candidate Raw Inputs]
       │
       ▼
 [Intake & Discovery]  ──► artifacts/output/Candidate_Profile.md
       │
       ▼
  [Job Ad Analyzer]    ──► artifacts/output/COMPANY_ROLE/Job_Brief.md
       │
       ▼
[Discovery Interview]  ──► Clarifies domain scope, scale, tools, ownership, metrics
       │
       ▼
  [CV & Cover Letter]  ──► artifacts/output/COMPANY_ROLE/Firstname_Lastname_CV.docx
       │
       ▼
 [Consistency Check]   ──► Cross-audit: contact, dates, titles, metrics, zero placeholders
       │
       ▼
 [Selection & Offer]   ──► STAR Bank, PM Mocking, Referees, Salary Negotiation
       │
       ▼
 [Pipeline Tracking]   ──► artifacts/output/job-applications.csv
```

---

## 3. Installation & CLI (`node bin/cli.mjs`)

Clone or download the repository, then run the installer using Node.js:

```bash
# 1. Interactive setup wizard (prompts for harnesses, link method, and scope)
node bin/cli.mjs init

# 2. Or install non-interactively with all harnesses into the current directory
node bin/cli.mjs init --target . --harness all --yes

# 2b. ...and choose the document language and paper size up front
node bin/cli.mjs init --target . --harness all --yes --lang en-GB --page a4

# 3. Install into a specific target project folder
node bin/cli.mjs init --target /path/to/my-project --harness claude,opencode,github,kiro --yes

# Reconfigure harnesses anytime (add or remove Claude Code, OpenCode, Copilot, Kiro)
node bin/cli.mjs reconfigure --target .

# Update prompts, skills, and templates to the latest version
node bin/cli.mjs update --target . --yes

# Verify local file integrity against cryptographically pinned manifest
node bin/cli.mjs verify --target .

# Set the standing language and paper size for generated documents
node bin/cli.mjs config --lang en-US --page a4

# Safely uninstall Vancy (removes core files while preserving your artifacts/)
node bin/cli.mjs uninstall --target .
```

### Language and paper size

Documents render with your standing choice, stored in `.vancy/config.json`:

```bash
node bin/cli.mjs config                      # show the current setting
node bin/cli.mjs config --lang en-GB         # British English
node bin/cli.mjs config --lang en-US --page letter
```

Every renderer resolves in this order: `--lang`/`--page` on the command line, then the
document's own front matter, then `.vancy/config.json`, then the fallback (`en-US`, `a4`).
The installer lists 22 languages A–Z, including English (UK) and English (US); choose
"Other" there for any tag not listed. Any BCP 47 tag works (`en-GB`, `fr-FR`, `de-DE`,
`pt-PT`, `zh-TW`). The skills' regional conventions tables still choose structure, length
and sign-off for the target market, so a US-English user applying to a UK role still gets
British letter conventions on that document.

### Supported AI Coding Environments & Harnesses
- **Claude Code**: Scaffolds `.claude -> .agents` link + `CLAUDE.md` project memory.
- **OpenCode**: Scaffolds `.opencode -> .agents` link.
- **GitHub Copilot**: Scaffolds `.github/copilot-instructions.md` + `.github/skills`.
- **Kiro**: Scaffolds `.kiro/steering/`, `.kiro/skills/`, and `.kiro/agents/career-consultant`.
- **Any Agent Tool**: Native `.agents/` folder compatible with Codex, Cursor, Gemini CLI, Windsurf, and custom orchestrators.

---

## 4. Key Architectural Features

- **Discovery-First & Zero Hallucination**: Vancy refuses to guess your engineering choices, database sizes, or system throughput. It interviews you on the technical details first.
- **100% Local Privacy**: All candidate data lives in `artifacts/` (`artifacts/input/` and `artifacts/output/`). A dedicated `.gitignore` guarantees that resumes, notes, letters, and tracking data never leak into git.
- **ATS-Compliant Word (.docx) Engine**: Five original single-column layouts (`classic`, `modern`, `minimal`, `executive`, `compact`) using native Word styles (no unreadable tables, text boxes, or floating headers).
- **Zero Third-Party Python Dependencies**: All scripts run on Python 3.8+ using only the Python standard library. No `pip install` required.
- **Untrusted Input Isolation**: Job advertisements and recruiter texts are isolated as text data, protecting your AI session against prompt injections.

---

## 5. Bundled Scripts

All scripts can be executed directly from your terminal. Paths below assume the default `.agents/`
install; use `.claude/skills/`, `.kiro/skills/` or `~/.agents/skills/` if you installed there.

```bash
# List available Word templates
python3 .agents/skills/cv-builder/scripts/render_docx.py --list-templates

# Compile a tailored CV into a production-ready Word document
# (add --lang/--page only to override .vancy/config.json for this one file)
python3 .agents/skills/cv-builder/scripts/render_docx.py artifacts/output/Acme_SWE/Jane_Doe_CV.md \
  -o artifacts/output/Acme_SWE/Jane_Doe_CV.docx \
  --template modern --final

# Lint document for ATS compliance, white text, and placeholders
python3 .agents/skills/cv-reviewer/scripts/doc_lint.py artifacts/output/Acme_SWE/Jane_Doe_CV.docx \
  --type cv --job artifacts/input/job_ad.txt

# Inspect application follow-up reminders due within 7 days
python3 .agents/skills/application-tracker/scripts/tracker.py --file artifacts/output/job-applications.csv due --days 7

# Run PM interview response scoring
python3 .agents/skills/pm-interview-prep/scripts/score_sheet.py --category product_sense --scores structure=4,insight=4,creativity=3

# Compare multiple job offers
python3 .agents/skills/salary-negotiation/scripts/offer_calc.py compare offers.json
```

---

## 6. Development & Quality Checks

Run the automated test suite to verify frontmatter, compatibility, Python AST syntax, tarball safety, and symlink integrity:

```bash
npm run check
```

The version lives in `package.json` and nowhere else. `npm run check` fails if a copy has
drifted, and `npm version <patch|minor|major>` copies the new number into the skill
frontmatter and `.agents/manifest.json`, stages them, and tags the release. The CLI,
the installer banner and `.agents/.vancy-version` read the same value at runtime.

---

## 7. Documentation

- [**User Guide (GUIDE.md)**](GUIDE.md) | [**中文用户指南 (GUIDE.zh-CN.md)**](GUIDE.zh-CN.md): Practical tutorial, prompt templates, and interview prep.
- [**AI Workflow Specification (WORKFLOW.md)**](WORKFLOW.md) | [**AI 工作流规范 (WORKFLOW.zh-CN.md)**](WORKFLOW.zh-CN.md): Execution protocol and constraints for LLM agents.

---

## License

[MIT](LICENSE) © Vancy Contributors
