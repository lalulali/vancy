# Keyword Tailoring: Reading a Job Ad and Matching Honestly

> All names and numbers here are fictional; never reuse them or any figure the user did not give.

Tailoring is the single highest-leverage edit. The goal: make a true document that visibly answers *this* ad, in its own vocabulary, without fabrication or stuffing. Source numbers refer to `evidence.md`.

## Contents
1. Deconstruct the job ad
2. Build a term map
3. Prioritise requirements
4. Place terms where they belong
5. Honest-match rules
6. Gap handling
7. Worked example

## 1. Deconstruct the job ad
Read the ad twice and extract:
- **Exact job title** (for your headline, if it's truthful).
- **Must-haves**: the first-listed duties, anything repeated, and anything phrased "required", "must", "essential".
- **Nice-to-haves**: "preferred", "bonus", "a plus".
- **Hard skills / tools / methods / certifications / domains** (the keyword core).
- **Soft/behavioural signals** ("cross-functional", "ownership", "fast-paced").
- **Seniority signals** (team size, budget, scope, stakeholder level).
- **Implied pain points** ("improve", "scale", "turn around", "establish", "clean up").

## 2. Build a term map (and verify with the user before writing)
Make a three-column map comparing the ad against the candidate's current materials:

| Ad term (their wording) | True of me? | My evidence (role + technical context + metric) |
|---|---|---|
| "stakeholder management" | yes | Aligned 6 department heads on the 2024 roadmap |
| "experimentation" | yes | Ran 40+ A/B tests; +6.4pt conversion |
| "Kubernetes" | ask user (partial?) | Not on old CV — ask if used in any project, what scale, and what they owned |
| "German (fluent)" | ask / no | — |

Use the ad's exact phrasing in the "Ad term" column; that is the wording to mirror where true. **Never assume a missing term means "no", and never assume it means "yes".** Candidates routinely leave tools, architectures, and methods off old CVs. Show the term map to the user and ask about every "ask user" or under-explained technical requirement before writing the draft.

## 3. Prioritise requirements
Address every **must-have** that is true of you, explicitly, high in the document (summary, skills, first bullets). Nice-to-haves come after. If a must-have is only partly met, address it honestly (see §6).

## 4. Place terms where they belong
- **Headline**: mirror the job title.
- **Summary**: weave in 2–5 of the most important true terms.
- **Key Skills**: the hard-skill terms, in the ad's wording, ordered by relevance.
- **Scope bullet + achievements**: embed terms inside real evidence ("led *stakeholder management* across 6 teams to…").
- Spell out acronyms once ("CI/CD (continuous integration and delivery)") so both forms match.

## 5. Honest-match rules (zero assumption, zero hallucination)
- Add a missing keyword only after the user confirms it is true of their experience and tells you how they used it. Listing skills you lack or grafting keywords onto bullets where they weren't used fails in technical interviews and is a credibility risk [9][32].
- Never autonomously rewrite a technical bullet to swap in the job ad's stack, architecture, or methodology. Ask the user first: *"Did you use [Ad Term] in this project, and what did that look like technically?"*
- Coverage is information, not a score target: a term-map gap is a discovery question for the user, never a licence to guess.
- Mirror wording; do **not** paste whole sentences from the ad [8].
- No repetition purely for density, and never hidden text [5][32].
- Keep it readable for the human: the recruiter reads the same words the parser indexes.

## 6. Gap handling
| Situation | Do |
|---|---|
| Term missing from old CV | **Ask the user first** — they may have done the work without writing it down. If confirmed, capture the exact technical implementation and metric |
| Must-have you partly meet | Name the adjacent/true experience plainly ("exposure to K8s in one project; primary stack ECS") — don't overstate |
| Must-have you lack but could learn | Don't claim it. Decide with the user whether to apply; a cover letter can address learning intent honestly |
| Different vocabulary, same thing | Confirm with the user that the concept is genuinely identical ("ad: 'demand generation' = my 'lead gen'"), then translate into their term |
| Confidential metric | Use % / ranges / magnitude confirmed by the user, keep the keyword |

## 7. Worked example
**Ad (excerpt):** "Senior Product Manager. Required: 5+ yrs B2B SaaS, experimentation, stakeholder management, pricing. Preferred: payments domain."

**Weak bullet (generic):** "Worked on product improvements and worked with different teams."

**Tailored, true bullet:** "Led **pricing** and **experimentation** for a B2B SaaS checkout product, running 40+ A/B tests and aligning 6 department heads (**stakeholder management**) to lift conversion from 71% to 77.4%."

Every bolded term is an ad must-have, placed inside real evidence — not a keyword list.
