# LinkedIn Profile Anatomy and Rules

Citation numbers refer to `evidence-linkedin.md`. Platform features change; tell the user to check the current editor.

## Contents
1. Goal and audience
2. Intake questions
3. Section-by-section rules
4. Consistency with the CV
5. Visibility, privacy and settings
6. Regional and language notes
7. Pre-publish checklist

## 1. Goal and audience
A LinkedIn profile is a **searchable, public landing page**, not a copy of the CV. Decide the single job it does:
- **Be found** by recruiters for a target role (keywords, titles, skills).
- **Convince** a visitor who arrives from an application, referral or message within seconds.
- **Make contact easy** (clear next step).

The CV is tailored per application. The profile targets a **role family**. Write it for the 1-2 role families the user wants.

## 2. Intake questions (3-5 per message)
1. Target role family and seniority? Target industries and locations (or remote)?
2. Current state: paste the existing headline, About and experience, or the CV.
3. Job-ad terms: do you have 1-3 ads for the target role? (Use `job-ad-analyzer` for the keyword list.)
4. Audience and tone: recruiters, clients, peers, hiring managers? Formal or conversational?
5. Profile language(s) and market conventions (photo, personal details).
6. What do you want visitors to do next (message you, view a portfolio, apply)?
7. Privacy: current employer sensitivity, whether you are actively or quietly searching.

## 3. Section-by-section rules
| Section | Limit (verify in editor) | Rules |
|---|---|---|
| **Headline** | 220 chars [6] | Role + niche + proof/tools. `Role | Specialism | Tools or outcome`. Use the real terms a recruiter would search [1]. Avoid "Open to work" and "Seeking..." (use the setting). No buzzwords |
| **About** | 2,600 chars [6] | Open with what you do and a number, because only the first lines show before "see more" [7]. Then proof, then how you work or what you want next. Plain first person is normal here. No cliché openers |
| **Experience** | 2,000 chars per role [6] | Same titles, employers and dates as the CV. 2-5 lines per role: scope first, then results with numbers. Move older roles to one line |
| **Skills** | 80 chars per skill [6] | 10-30 real skills in the target role's vocabulary. Pin the top 3. Do not list skills you cannot demonstrate |
| **Featured** | - | 1-3 proof items: a case study, talk, repo, publication. Links must work. Only publish what you may share |
| **Education / certifications** | - | Names exactly as issued. Add in-progress items with dates |
| **Other** | - | Languages, volunteering, recommendations, custom URL (firstname-lastname) |

Cross-section keyword coverage: use important target terms naturally in more than one section (headline, About, a role, skills) [2]. Do not stuff, repeat, or add hidden terms.

## 4. Consistency with the CV
- Titles, employers, dates, degrees and headline metrics must match the CV. Mismatches are easy to catch and erode trust [9].
- Metrics must be the same figure, unit and period everywhere.
- The profile can be a little more personal and narrative than the CV, but never contradict it.

## 5. Visibility, privacy and settings
- A public profile is searchable by anyone. Ask what the user is comfortable showing, particularly:
  - contact details in About (public)
  - employer-confidential figures (use percentages or ranges)
  - current-employer visibility if the search is confidential
- "Open to Work" can be shown to all members, to recruiters only, or only to you [11]. Recruiters-only reduces visibility, but LinkedIn cannot guarantee your employer won't see it [11]. Explain the trade-off and let the user choose. Check the current LinkedIn Help page, because settings change.
- Activity (posts, comments) is separate from profile ranking claims. Do not promise reach.
- The agent cannot edit LinkedIn. Deliver paste-ready copy and a checklist; the user applies it.

## 6. Regional and language notes
- Write in the language of the target market. A profile can have multiple language versions.
- Photo, date of birth and similar items: the user decides. Do not insist on a photo. The bias-safe default is to leave out date of birth, marital status, religion, national ID numbers and a full street address, and to add a photo or nationality only if the user's target market expects it and they want it. Ask where the job is if unsure, and never add personal details on your own initiative.
- Some markets expect a formal tone; others expect conversational.

## 7. Pre-publish checklist
- [ ] Headline <= 220 chars, role + niche + proof; no buzzwords.
- [ ] About opens with a concrete fact; no cliché; <= 2,600 chars.
- [ ] Every role matches the CV; results quantified or scoped.
- [ ] 10-30 relevant skills; top 3 pinned.
- [ ] Featured items are shareable and links work.
- [ ] No confidential data; contact details deliberate.
- [ ] Linter run: `python3 scripts/linkedin_lint.py profile.md`. Read the user's CV from `artifacts/input/` and save the draft to `artifacts/output/` (git-ignored personal data).
- [ ] Limits confirmed in the LinkedIn editor.
