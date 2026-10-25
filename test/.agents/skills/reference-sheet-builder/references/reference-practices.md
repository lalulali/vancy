# Reference Practices

Citation numbers refer to `evidence-references.md`.

## Contents
1. What a reference sheet is for
2. When to share it
3. Choosing referees
4. Asking, briefing and thanking
5. What goes on the sheet
6. Regional and privacy notes
7. Special situations
8. Checklist

## 1. What a reference sheet is for
A reference sheet is a **separate one-page document** listing people who can vouch for your work, with their contact details and how they know you. It is shared **only when asked**, usually late in the process. It is not part of the CV: the CV should not include "References available upon request" by default [8], and it should never include referees' contact details.

## 2. When to share it
- Share it when the employer asks; some employers ask for it later in the process [4].
- Do not attach it to the first application unless the posting asks for it.
- Some employers contact referees only with your written consent. Others use a reference-check service. Ask what the process is.
- Tell referees when a check is likely, so it does not come as a surprise [2].

## 3. Choosing referees
- Pick people who have **worked with you directly** and can describe specific results: a current or former manager, a senior colleague, a client or stakeholder, a professor or supervisor (early career) [1][3][6].
- Match them to the target role. If the job brief stresses leadership, include someone who saw you lead. For stakeholder-heavy jobs, include a stakeholder.
- Avoid family and friends; they cannot give an objective view of your work [5].
- Use a mix: at least one manager, and others who show different strengths.
- Make sure they would give you a positive, specific, current reference.
- Keep two or three ready (more if asked). Consider keeping reserves.
- If your current employer must not know yet, offer former managers and say that current-employer checks may happen only after an offer.

## 4. Asking, briefing and thanking
1. **Ask permission first**, individually, in a short message or call [2]. Give them an easy way to say no. Tell them if an AI assistant helps you prepare your application documents, because their name and contact details would be processed by it, and that they may decline.
2. **Brief them:** the role, the company, the dates and the three things you would like them to mention. Share your CV and the job brief.
3. **Confirm contact details and preferences:** best email, phone, time zone, language, and the best time to call.
4. **Record consent** with a date. The linter requires it before the sheet can be shared.
5. **Update them** when you apply and when a check begins.
6. **Thank them** afterwards, and tell them the outcome [7].
Never list someone who has not agreed.

## 5. What goes on the sheet
```
---
doc: references
template: minimal
page: a4
lang: en-GB
---

# Your Name
email | phone | city, country

## Professional References
### Name | Job Title | Organisation
- Relationship: how you know them, and over which dates
- Worked together: how long
- Email: ...
- Phone: ... (with country code)
- Best contact: preferred method, hours, time zone
- Can speak to: 2-3 topics relevant to the target role
> Consent: confirmed by email 2026-10-01
```
- Same header style as the CV and letter, so the documents match.
- Professional titles, full organisation names and correct spellings.
- Phone numbers with the country code.
- Consent line grammar: `> Consent: confirmed [by email|phone|in person|message|call|video] YYYY-MM-DD`, for example `> Consent: confirmed by email 2026-10-01`. The method is optional, but when given it follows `by` (the linter does not accept `confirmed in person 2026-10-01` without it; use `confirmed by in person 2026-10-01` or leave the method out). Write it **only after the referee has actually agreed**, with the real date. It is a draft note: `--final` strips it from the output, but refuses to render a sheet if any referee lacks a valid line.
- One page for 2-4 referees.
- Read the user's material from `artifacts/input/` and save the sheet to `artifacts/output/<Company>_<Role>/` (or `artifacts/output/` for a general sheet). `artifacts/` is git-ignored, which matters because the sheet holds other people's personal data.

## 6. Regional and privacy notes
- Reference practice varies: some markets use written reference letters or certificates; some use only phone checks; some check only after an offer; some employers use third-party verification. Known local specifics:
  - **Germany (statute seen in search results; confirm the current text):** an employee has a legal right to a written reference (*Arbeitszeugnis*) when employment ends, under § 109 GewO [9]. The basic version covers the type and length of work; ask for the *qualifiziertes Zeugnis* if you want performance and conduct included. Ask the former employer for it rather than relying on a phone referee.
  - **UK regulated finance (FCA handbook seen in search results; confirm the current text):** firms under the FCA's SYSC 22 regime exchange standardised regulatory references that cover at least the previous six years [10]. For roles in banking, insurance or investment, prepare a complete six-year employment history.
  - **UK, other sectors:** many employers give only factual references (dates, title). Unverified: check locally.
  - **US:** many employers confirm only dates and job title, and route checks through HR or a verification service. Unverified: check locally.
  - **Gulf and Asia:** experience letters, relieving letters or service certificates are often requested alongside referees. Unverified convention: check locally.
- A reference sheet contains other people's personal data. Collect only what is needed, store it securely, share it only with employers who ask, and delete old copies. Data-protection rules may apply (for example, in the EU and UK). This is general guidance, not legal advice.
- Do not post the sheet publicly or on a job-board profile.
- Employers may ask for the referee's consent or send them a form. Tell referees to expect it.

## 7. Special situations
| Situation | Approach |
|---|---|
| First job or student | Professors, internship supervisors, club or volunteering leaders, part-time employers |
| Career changer | A referee who saw the transferable skills, plus someone from the new field if possible |
| Left on bad terms | Choose another senior colleague or client; ask HR what they will confirm; be honest if asked |
| Employer only confirms dates and title | Add a personal professional referee who can speak to your work |
| Confidential job search | Offer former managers; ask the employer to contact the current one only after an offer |
| Referee unavailable or abroad | Give an alternate contact and the time zone; check they can be reached |
| Reference by letter | Ask the referee to address it to "To whom it may concern" or the employer, with the date and their role |

## 8. Checklist
- [ ] Each referee has agreed, and the date is recorded.
- [ ] Each was briefed with the role, the CV and the points to cover.
- [ ] Names, titles, organisations, emails and phones are correct, with country codes.
- [ ] Relationship and dates are clear; "can speak to" matches the target role.
- [ ] The linter passes.
- [ ] The final has no consent notes or placeholders.
- [ ] The sheet is shared only when asked.
