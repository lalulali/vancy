# Cover Letter Anti-Patterns: Detect and Fix

Items marked (lint) are reported by `scripts/doc_lint.py --type letter`.

| Anti-pattern | Detect | Fix |
|---|---|---|
| Generic letter | Fails the any-company test. No company fact. Company named only once | Add 1–2 verifiable hooks tied to the candidate's evidence [16][50] |
| Formula opener | "I am writing to apply…", "It is with great enthusiasm…", "My name is…" (lint) | Open with a specific reason or a proof point. Name the role and company |
| Focused on the candidate | High `i_to_you_ratio`, many `sentences_starting_with_I` (lint). "This role would help me grow" | Reframe around the employer's needs and the candidate's contribution |
| CV recap | Paragraphs restate CV bullets in order | Pick 1–2 achievements and add context: why, how, what it means for them |
| Claims without proof | "I am a strong leader", "ideal candidate", "proven track record" (lint) | Replace each claim with evidence and a metric |
| No metrics | `numbers_in_letter` is low (lint) | Add 1–3 relevant numbers taken from the CV |
| Metrics that contradict the CV | Different figures, titles or dates | Align with the CV and ask the user which is right |
| Irrelevant achievement | A metric that doesn't matter to the target role | Swap in a relevant one |
| Flattery without action | "Your renowned company…" with nothing following it | Compliment plus contribution, or cut it |
| Weak or no call to action | Ends abruptly, or "Hope to hear from you" only | Invite a specific conversation and thank the reader |
| Desperate or presumptuous close | "I'll call on Monday to schedule", "Please give me a chance" | Courteous, confident invitation |
| Too long or too short | `length_band` (lint). More than one page | Cut to 250–400 words. Remove history and repetition |
| Wall of text or all bullets | 1–2 paragraphs, or nothing but bullets | 3–5 paragraphs. At most 2–3 bullets in the proof paragraph |
| Unedited generic or AI-style prose | Stock enthusiasm, symmetrical triads ("skilled, driven and collaborative"), no company-specific fact | Judge specificity, not authorship; never accuse the user of using AI (AI-text detectors are unreliable [53]; editing the draft helps [50]). Ask for one personal detail the user can defend and build the letter around it |
| Recycled boilerplate | Stock phrases such as "contribute to continued growth and performance" or "rapidly changing climate" | Specific, plain sentences |
| Repeated sentences | The same thank-you or "look forward" line twice | Keep one |
| Placeholders left in | `placeholders` (lint): "[Company]", "Mr. XXX" | Fill them in. Finals are blocked until they are filled |
| Wrong salutation or sign-off pairing | `generic_salutation`, `signoff_mismatch` (lint) | Use a named recipient where possible. Match the sign-off to the market [13] |
| Contact details don't match the CV | Compare `emails`/`phones` (lint) with the CV | Make them identical |
| Mentions salary or personal data unprompted | Salary, age, nationality, marital status | Remove unless the job ad asks |
| Badmouthing a current or past employer | Negative reasons for leaving | Reframe positively: what they are moving toward |
| Risky humour or gimmicks | Jokes, memes, odd closings | Remove unless the brand is clearly informal and the user insists |
| Unexplained jargon | Internal acronyms | Spell out or translate |
| Tense slips | "In my current role I worked…" | Present tense for current work |
| Mixed spelling | `spelling.mixed` (lint) | One convention, matching the CV and market |
| Hidden text or prompt injection | White text, tiny text, "ignore previous instructions" | Remove. It is treated as deception [32] |
