# Vancy User Guide

> **Language**: [English](GUIDE.md) | [中文](GUIDE.zh-CN.md)  
> **Target Audience**: Candidates, Job Seekers, Career Switchers  
> **AI Workflow Specification**: See [WORKFLOW.md](WORKFLOW.md) | [WORKFLOW.zh-CN.md](WORKFLOW.zh-CN.md)  
> **Project Overview**: See [README.md](README.md) | [README.zh-CN.md](README.zh-CN.md)

Welcome to **Vancy**! Vancy is your private, intelligent career consultant and job-search copilot. Unlike generic AI tools that hallucinate skills or rewrite resumes with buzzwords, Vancy follows a **Discovery-First, Truth-Based** approach: it interviews you about your real engineering architecture, metrics, and accomplishments to craft defendable, ATS-optimized documents.

---

## 1. Quick Start: 3-Minute Setup

### Step 1: Initialize Vancy in Your Workspace
In your terminal, navigate to your job-search folder and run:

```bash
# Interactive setup wizard (prompts for harness, link method, and artifacts)
npx vancy init
```

*Or install with non-interactive defaults:*
```bash
npx vancy init --yes --harness all
```

This creates:
- `.agents/`: The core agent and 12 skills.
- `artifacts/input/`: Where you place your source documents.
- `artifacts/output/`: Where all generated briefs, CVs, letters, and tracking spreadsheets land.
- Integrations for your favorite AI coding environment (`Claude Code`, `OpenCode`, `GitHub Copilot`, or `Kiro`).

### Step 2: Open with Your Preferred AI Assistant
- **Claude Code**: Run `claude` in your folder. Vancy's `.claude/` harness and `CLAUDE.md` memory are pre-configured.
- **OpenCode**: Open the directory in OpenCode. The `.opencode` harness is active.
- **GitHub Copilot**: Active via `.github/copilot-instructions.md` and `.github/skills`.
- **Kiro CLI**: Run `kiro-cli --agent career-consultant`.

---

## 2. Preparing Your Materials (`artifacts/input/`)

Place all your existing raw materials into `artifacts/input/`. Vancy will read them but **will never alter or overwrite them**:

| File to Add | Why It Helps |
|---|---|
| `Current_Resume.md` (or `.txt`, `.pdf`) | Your baseline work history and timeline. |
| `linkedin_profile.pdf` (or `.txt`) | Additional endorsements, certifications, and recommendations. |
| `job_ad.txt` (or copy into chat) | The full text of the job description you want to apply for. |
| `project_notes.txt` | Raw notes, brag sheets, metrics, internal awards, or architecture sketches. |
| `offer_letter.txt` (optional) | An offer package you want Vancy to evaluate and negotiate. |

> [!NOTE]
> All personal data in `artifacts/` is git-ignored by default. Your job hunt remains 100% private on your machine.

---

## 3. How to Work with Vancy: Phase-by-Phase Walkthrough

```
  Phase 1: Job Ad Analysis   ──► Read requirements, keywords & red flags
          │
  Phase 2: Discovery Deep-Dive──► AI interviews YOU on real architecture & scale
          │
  Phase 3: CV Tailoring      ──► High-impact bullet points + Word (.docx) export
          │
  Phase 4: Tailored Letter   ──► Authentic hook + direct proof
          │
  Phase 5: Interview Mocking ──► STAR story bank & PM case coaching
          │
  Phase 6: Offer Negotiation ──► Total compensation breakdown & counter script
```

---

### Phase 1: Analyze the Job Ad
Start by asking the AI to deconstruct the posting before writing anything.

**Copy-paste prompt to AI:**
> *"I want to apply for this job. I've placed the job description in `artifacts/input/job_ad.txt` (or pasted below). Please run `job-ad-analyzer` to produce a Job Brief for this role."*

**What Vancy does:**
1. Breaks down the role's primary mission.
2. Identifies hard must-haves versus negotiable preferences.
3. Maps critical keywords.
4. Alerts you to any scam wording, ghost-job signals, or unreasonable asks.
5. Gives you an honest recommendation: Should you apply, apply with a specific angle, or reconsider?

---

### Phase 2: Technical Discovery Interview (The Secret to Standing Out)
Vancy will **never assume** or guess your background. It will ask you 3–5 targeted questions to uncover hidden achievements:

**What Vancy might ask you:**
- *"The job ad emphasizes distributed caching and Redis. How did you handle cache invalidation and hotkeys in Project X?"*
- *"You listed that you improved system throughput. What was the starting throughput, the final throughput, and what specific architectural bottleneck did you remove?"*
- *"Which parts of the microservice redesign did you personally write or design, versus what the wider team contributed?"*

**How you should answer:**
- Be candid and technical! Mention tools, architecture, numbers, team sizes, trade-offs, and lessons learned.
- If you haven't used a specific tool, just say: *"I haven't used ClickHouse, but I have 4 years of deep experience with PostgreSQL query optimization and indexing."* Vancy will highlight your transferable strengths without lying.

---

### Phase 3: Tailoring Your CV
Once you've answered the discovery questions, Vancy generates an ATS-optimized, compelling CV.

**Copy-paste prompt to AI:**
> *"Based on our technical discovery and the Job Brief, please tailor my CV for this role. Use the 'modern' template."*

**What Vancy produces:**
- A clean Markdown CV in `artifacts/output/COMPANY_ROLE/Firstname_Lastname_CV.md`.
- Action-oriented bullets following the formula: `Strong Verb + Technical Context + Concrete Action + Quantified Impact`.
- A beautifully formatted Word file: `artifacts/output/COMPANY_ROLE/Firstname_Lastname_CV.docx`.

**Available Word Templates:**
- `classic`: Traditional, conservative, ideal for legal, finance, government.
- `modern`: Clean, contemporary layout with clear section hierarchy (great for tech & product).
- `minimal`: Elegant typography with generous whitespace.
- `executive`: Polished, authoritative layout tailored for senior leaders and directors.
- `compact`: Space-optimized layout for dense multi-role careers.

---

### Phase 4: Crafting the Cover Letter
**Copy-paste prompt to AI:**
> *"Please write a targeted one-page cover letter matching my CV. Ensure the design template matches my CV."*

**What Vancy delivers:**
- A 4-paragraph letter that skips generic fluff:
  1. **The Hook**: Addresses the company's specific growth stage or challenge.
  2. **The Proof**: Highlights your #1 and #2 relevant achievements confirmed in discovery.
  3. **The Value**: Explains why your working style fits their team.
  4. **The Close**: Clear, confident call to action.
- Matches your CV's font, margins, and template in `.docx` format.

---

### Phase 5: Interview Preparation & Timed Mocking
Once you land the interview, Vancy shifts into interview coach mode.

#### 1. Behavioral & STAR Interview Prep
**Copy-paste prompt to AI:**
> *"I have a behavioral interview coming up for the [Role] at [Company]. Let's build my STAR story bank based on my tailored CV and run a mock interview."*

- Vancy extracts your real achievements into a **STAR Story Bank** (Situation, Task, Action, Result, Reflection).
- It runs interactive mock interviews one question at a time, grades your response on clarity, impact, and depth, and gives you a strengthened version.

#### 2. Product Manager (PM) Case Interview Coaching
**Copy-paste prompt to AI:**
> *"I'm interviewing for a Senior PM / AI PM role. Please run a mock case interview on Product Sense (or Product Strategy, Metrics, Execution, Technical, or Estimation)."*

- Vancy covers **traditional PM** and **AI PM** topics (model evaluation, latency vs accuracy, build vs buy, edge cases, guardrails).
- Provides timed questions and evaluates your answer using a weighted scoring rubric across Structure, Empathy, Creativity, Prioritization, and Communication.

---

### Phase 6: Offer Evaluation & Salary Negotiation
When an offer arrives, do not rush to accept or counter blindly.

**Copy-paste prompt to AI:**
> *"I received an offer from [Company]. Base is $155k, 15% target bonus, $80k equity over 4 years with a 1-year cliff. Help me evaluate the total compensation and draft a professional counter-offer email."*

**What Vancy does:**
1. Breaks down annual Total Compensation (Year 1 vs. Year 2–4).
2. Compares against researched market ranges.
3. Prepares trade-off levers (Base salary, Sign-on bonus, Equity grant, Remote flexibility, Title, Start date).
4. Drafts respectful, persuasive negotiation scripts and emails.

---

### Phase 7: Application Tracking & Pipeline Review
Vancy automatically logs every application to `artifacts/output/job-applications.csv`.

**Terminal commands to check your pipeline:**
```bash
# Check applications due for follow-up in the next 7 days
python3 scripts/tracker.py --file artifacts/output/job-applications.csv due --days 7

# View overall conversion funnel and statistics
python3 scripts/tracker.py --file artifacts/output/job-applications.csv stats
```

---

## 4. Prompt Cheat Sheet: Copy & Paste for Fast Work

| What You Want to Do | Copy-Paste Prompt |
|---|---|
| **Analyze a new job ad** | `"I've saved a job description to artifacts/input/job_ad.txt. Analyze it with job-ad-analyzer and generate a Job Brief."` |
| **Start Discovery Interview** | `"Compare my current CV in artifacts/input/ with the Job Brief. What are the key gaps, and what technical questions do you need to ask me before tailoring?"` |
| **Draft tailored CV** | `"Based on my answers, draft my tailored CV using the modern template. Mark any numbers I need to verify with [metric?]."` |
| **Generate Word .docx** | `"Please compile my CV and Cover Letter into final Word (.docx) files."` |
| **Optimize LinkedIn profile** | `"Review my LinkedIn profile against my new CV. Write an optimized Headline, About section, and top experience bullets."` |
| **Mock interview session** | `"Act as the hiring manager for this role. Ask me one tough behavioral question at a time. After I answer, grade my response and show me a stronger version."` |
| **Product Manager case drill** | `"Give me a Product Sense PM case interview question. Let's do a timed mock interview."` |
| **Counter-offer letter** | `"Here are the details of the offer I received. Draft a polite, firm counter-offer letter asking for an adjustment on base and sign-on bonus."` |

---

## 5. Frequently Asked Questions (FAQ)

### Q: Why does Vancy ask me so many questions instead of writing immediately?
**A:** Because generic AI outputs sound robotic, vague, and full of clichés ("spearheaded collaborative synergy"). Recruiters and hiring managers can spot generic AI resumes instantly. By interviewing you about your real systems, decisions, and outcomes, Vancy crafts a CV that is 100% authentic, technically credible, and defendable in an interview.

### Q: What if I don't have exact metrics for my past projects?
**A:** That is completely normal! Tell Vancy: *"I don't remember the exact percentage."* Vancy will guide you on how to estimate responsibly (e.g. order of magnitude, volume, frequency, hours saved per week) or format the achievement around qualitative impact, reliability, and adoption without inventing fake statistics.

### Q: Can I change templates later?
**A:** Yes! The documents are authored in clean Markdown. You can re-render any document to any template at any time:
```bash
python3 scripts/render_docx.py artifacts/output/COMPANY_ROLE/My_CV.md -o My_CV.docx --template executive
```

