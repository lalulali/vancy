# Confidentiality, Credit and Ethics

The author is responsible for deciding what may be published. This is general good practice, not legal advice. Employment contracts, NDAs and client agreements differ.

## Contents
1. Before you write
2. Ways to share work you cannot show
3. Redaction checklist (including the linkage check)
4. Crediting others
5. Honesty
6. AI-generated material

## 1. Before you write
- Re-read your contract, NDA and client agreement. Ask the employer or client for written permission when in doubt.
- Do not publish: client names under NDA, non-public financials, personal data, credentials, internal URLs, unreleased products, security details, or screenshots that show any of these.
- Work you did for an employer is usually the employer's, not yours, unless your contract expressly allows it, so get **written permission** before publishing it, even anonymised.
- If you cannot get permission, use an anonymised version or a different piece.

## 2. Ways to share work you cannot show
| Option | How |
|---|---|
| Anonymise | "A payments company (name withheld by agreement)" with the industry and size |
| Ranges and percentages | Replace exact revenue or volumes with percentages, ratios or ranges |
| Rebuild with synthetic data | Recreate the flow, dashboard or model with invented data and say so |
| Redact visuals | Blur or replace logos, names and numbers; recreate wireframes |
| Describe instead of show | A written case study with a diagram you drew |
| Private link | A password-protected or time-limited link shared with interviewers, if permitted |
| Interview-only | Keep a detailed version ready to talk through, with nothing published |
State clearly when something is anonymised or synthetic. Never present invented data as real.

## 3. Redaction checklist
Run `scripts/case_study_lint.py CASE.md --redact "ClientName,InternalTool,PersonName"` and also check by eye:
- [ ] Client, brand, product and project code names
- [ ] People's names and faces, usernames, emails and phone numbers
- [ ] Internal tool names, URLs, ticket numbers, repository names
- [ ] Exact numbers that reveal revenue, headcount or pricing
- [ ] Metadata in images and files (author, location, comments)
- [ ] Alt text and file names, which can leak names too
- [ ] **Linkage check.** Compare the case study against your CV, LinkedIn and dates. An anonymised label plus your named employer, your dates and unique figures can re-identify the client ("a payments company" + "Payly, 2024" + "9 days to 2"). Round the numbers or give ranges, drop the dates, or treat the detailed version as interview-only. Then get written permission.

## 4. Crediting others
- Say what you did and what others did. Name collaborators by role (or by name with their permission).
- Do not claim a team result as solely yours. Interviewers will probe it.
- Credit sources, photographers, templates and open-source libraries as their licences require.

## 5. Honesty
- Every claim, number and date must be true and defensible in an interview.
- Mark estimates ("about", "estimated") and say how you measured the outcome.
- Do not exaggerate impact or hide failed attempts that shaped the result.
- Do not invent clients, projects or outcomes.

## 6. AI-generated material
- If AI tools produced images, text or code in the work, disclose it where it is relevant to the claim or to the employer's policy.
- You must be able to explain every decision in your own words. Employers may test it.
- Do not paste confidential material into third-party AI tools without permission.
