# Rewrite Playbook (Cover Letters)

> All names and numbers here are fictional; never reuse them or any figure the user did not give.

## Principles
- Keep the candidate's facts and voice. Change the selection, order, framing and wording.
- Each paragraph gets one job. Any sentence that fails the "does this show what I'll do for them?" test is cut.
- Ask for any missing facts (company hook, referral name, metric) with `[fact?]`. Never invent them.

## Target structure (250–400 words in the body)
1. **Hook + thesis** (50–80 words): a specific reason for this company, the role named, a one-line identity, the headline metric, and the value you'll bring.
2. **Proof** (60–110 words): current or most relevant role, its scope, 1–2 requirements from the job ad, and the strongest achievement **last**.
3. **Optional second proof** (40–80 words): previous role or project, education (graduates), the bridge (career changers), or the gap (returners).
4. **Fit and value** (50–90 words): their need, a complementary skill, and a concrete first contribution.
5. **Call to action** (25–50 words): invite a conversation and thank them.

## Order of fixes
1. Wrong or missing role, company or recipient name, and leftover placeholders.
2. Specificity: add the company hook and the job ad's requirements.
3. Employer focus: reframe the "I want" sentences into "you need, I deliver".
4. Proof: one strong, relevant metric that matches the CV.
5. Opening and close.
6. Length and structure.
7. Language: clichés, spelling, tone.
8. Conventions: salutation and sign-off for the market, matching contact details.

## Transformations
| Before (pattern) | After (pattern) |
|---|---|
| "I am writing to apply for the X position I saw on [site]." | "[Company]'s [initiative] is exactly the work I have done for [N] years: [proof]." |
| "I am a hard-working team player with excellent skills." | "I led a team of [N] that [result + metric]." |
| "This role would be a great opportunity for me to grow." | "I would bring [capability] to help [Company] [goal]." |
| "Your company is a renowned leader in the industry." | "[Specific fact] → how my [experience] would help sustain or extend it." |
| A paragraph listing five past roles | One role, one achievement, plus why it matters to them |
| "I hope to hear from you." | "I would welcome a conversation about [specific topic]. Thank you for your time." |

## Phrase starters (adapt them; never paste verbatim)
- **Openers:** "When I read that [Company] is [initiative], …" · "Over [N] years in [field], I have [result]; I'd like to do the same for [Company]." · "[Referrer] suggested I contact you about …"
- **Proof:** "In my current role as [Title] at [Employer], …" · "The result I'm proudest of is …"
- **Value:** "Your focus on [priority] matches my record of [achievement]." · "In my first [90 days], I would focus on …"
- **Call to action:** "I would welcome a conversation about how I could contribute to [goal]." · "Thank you for your time and consideration."

## Delivery
1. Write `..._Cover_Letter_DRAFT.md` (format in `markdown-format.md`, layout as in the structure above), with `> ` notes and `[^n]` citations.
2. Render it with the CV's template, re-lint, re-score, and report the score before and after.
3. Once the user approves, run with `--final --clean-md` to produce a clean `.md` and `.docx`.
