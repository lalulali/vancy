# Case Study Structure

Citation numbers refer to `evidence-portfolio.md`.

## Contents
1. Choosing what to feature
2. Skeleton
3. Section guidance
4. Adapting by field
5. Visuals, links and accessibility
6. Intake questions
7. Portfolio-level decisions
8. Pre-publish checklist

## 1. Choosing what to feature
A portfolio is evidence for a **target role**. Feature three to five pieces that prove the skills the job brief ranks highest [5]. Sources disagree on the number; choose by quality and by what the target role needs [2][5].
Pick pieces that: show your own contribution, have a measurable result, show a decision with trade-offs, are recent, and are shareable. Drop weak or half-finished work.

## 2. Skeleton
```markdown
---
doc: case-study
template: modern
---

# Title that states the result
Role | Year | Team | Client or "Confidential client: <descriptor>"

## Overview
What it was, who used it, why it mattered, and the headline result in 3-4 lines.

![Alt text describing the image](img/file.png)

## My role
What you owned. Who you worked with. What others owned.

## The problem
The user or business problem and the evidence for it.

## Constraints
Time, budget, technology, policy, data.

## Process
What you did, in order.

## Key decisions
Options considered, what you chose, and why (trade-offs).

## Outcome
Results with numbers, or a clear observable change.

## What I learned
What you would do differently.
```
Read the user's material from `artifacts/input/` and save the case study to `artifacts/output/` (a case study is cross-application, so it does not go in a `<Company>_<Role>/` folder; `artifacts/` is git-ignored personal data). Run `scripts/case_study_lint.py`. It accepts common alternative headings (for example "Challenge", "Impact", "Approach").

## 3. Section guidance
- **Title:** state the outcome, not the topic ("Cutting merchant onboarding from 9 days to 2").
- **Overview:** two or three short sentences of scene-setting, then the headline result [6]. A skimmer should understand the whole story from here [1].
- **My role:** specific verbs and ownership. Credit the team separately. Use "I" for what you did.
- **Problem:** evidence (interviews, tickets, data), not assertion. Say how you knew it was the right problem.
- **Constraints:** make the decisions believable.
- **Process:** a short numbered sequence of what you did, not a diary. Show the key moments, not every step [4].
- **Key decisions:** the heart of the piece. For each, name the options, the choice, the reason and the trade-off [3].
- **Outcome:** numbers, before/after, timeframe, and a guardrail. If you do not have final numbers, say what you measured and the direction, and label estimates.
- **What I learned:** one honest lesson and one change you would make.

## 4. Adapting by field
| Field | Emphasise | Typical evidence |
|---|---|---|
| UX / product design | Research, insights, design decisions, testing | Flows, prototypes, usability results |
| Product management | Problem framing, prioritisation, experiments, trade-offs | Metrics, roadmap decisions, experiment results |
| Software engineering | System goals, architecture choices, scale, trade-offs | Diagrams, performance numbers, repositories with permission |
| Data / analytics / ML | Question, data, method, validation, decision impact | Dashboards, model metrics, business effect |
| Marketing / content | Audience, strategy, execution, results | Campaign metrics, samples, A/B results |
| Writing / journalism | Brief, audience, process, outcome | Published links, readership, awards |
| Consulting / strategy | Problem structure, analysis, recommendation, impact | Redacted slides, outcomes |
| Research / academia | Question, method, findings, impact | Papers, datasets with permission |
| Architecture / engineering | Brief, constraints, design response, delivery | Drawings, photos with permission |
Always translate the skeleton into the field's own words.

## 5. Visuals, links and accessibility
- Use a few meaningful images with captions and alt text, not a gallery [8]. The skeleton uses `![alt](path)`.
- Use headings in order (## then ###, never skipping), short paragraphs, descriptive link text, and good contrast [7][8].
- Check every link works and points to what you intend to share.
- The Word export from `render_docx.py` is text-only and prints a figure caption in place of each image. Add real images in your website, slide deck or PDF.

## 6. Intake questions (3-5 per message)
1. Which role are you targeting, and what do you want the case study to prove?
2. Which project? What was it, when, and who used it?
3. Your exact role. What did you personally decide or build? Who did the rest?
4. The problem and the evidence for it.
5. Constraints and options considered. What did you choose and why?
6. The outcome: numbers, timeframe, any guardrails. What would you change?
7. Permission: can you publish it? What must be anonymised or removed?
8. Which images or links exist, and are they cleared?

## 7. Portfolio-level decisions
- Order the pieces by relevance to the target role, strongest first.
- A short landing page: who you are, the kind of work you do, 3-5 case studies, contact.
- One case study per page; consistent structure.
- Link from the CV and LinkedIn Featured section.
- Keep a PDF version for applications that cannot take links, with the same redactions.
- Check hosting and privacy: no analytics that capture visitors without notice, where local law requires it.

## 8. Pre-publish checklist
- [ ] Permission confirmed; all sensitive names, data and URLs removed (`--redact` terms checked).
- [ ] Overview contains the headline result.
- [ ] "My role" separates your work from the team's.
- [ ] Decisions show options and trade-offs.
- [ ] Outcome has numbers or a clear observable change.
- [ ] Images have alt text; headings are in order.
- [ ] Linter run with no problems.
