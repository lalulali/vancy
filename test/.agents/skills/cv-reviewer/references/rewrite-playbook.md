# Rewrite Playbook (Strengthening)

> All names and numbers here are fictional; never reuse them or any figure the user did not give.

Use this when the user asks you to strengthen, improve or rewrite a CV, or accepts the fixes from a review.

## Principles
- **Preserve facts. Upgrade the expression — zero hallucination, zero assumption.** You may re-order, cut, merge, re-word and re-frame. Never add facts, technical implementations, tools, system architectures, or metrics that the source CV or the user hasn't confirmed.
- **Ask before rewriting.** When a stronger bullet needs a missing number or a missing technical method ("how" they did it, what tool/architecture they used, or what component they personally owned), **interview the user first** (3–5 questions per round). If showing a rewrite before the user has answered, use explicit placeholders for both the method (`[fact?: technical approach / tool used]`) and the number (`[metric?: baseline → result]`) — never invent a plausible-sounding method or number and tack `[metric?]` onto the end.
- Keep the candidate's voice and market conventions (spelling, length).
- Mark each substantive change in the draft with a short `> ` note explaining why, citing `evidence.md` where relevant.

## Order of operations (highest impact first)
1. **Target.** Fix the headline and summary to match the target role (top third of page 1).
2. **Structure.** Use standard headings. Put Key Skills near the top. Put the scope bullet first in each role. Split out a Key Achievements block.
3. **Achievements.** Convert duty bullets to XYZ using the technical details and metrics confirmed by the user. Lead with the result. Add baselines and timeframes.
4. **Relevance.** Re-order bullets by relevance to the job ad. Compress roles older than 10–15 years. Delete irrelevant content.
5. **Language.** Swap weak openers for verbs. Remove clichés, first person and filler. Keep bullets ≤2 lines.
6. **Consistency.** Make dates, tense, spelling, numbers and currency formats consistent.
7. **Format.** Re-render in an ATS-safe template.

## Transformations
| Pattern | Transform |
|---|---|
| "Responsible for managing X" | "Managed X [fact?: scope/scale], achieving [metric?: result]" (ask for scope and outcome) |
| "Helped/Assisted with X" | Ask what part the candidate actually owned and how they built it: "Built [fact?: component/service owned] for X using [fact?: stack/method], resulting in [metric?: outcome]" |
| A list of 8+ duties | Keep the 3–5 most relevant. Merge similar ones. Move results into Achievements |
| Paragraph-style role description | Scope bullet + 2–4 responsibility bullets + achievements |
| Adjective-heavy summary | Identity + years + domain → 2 signature wins → differentiator |
| Skills list of soft skills | Replace with the true hard skills/tools the job ad asks for (confirmed with the user). Prove the soft skills in bullets |
| "Increased sales / improved performance significantly" | "Improved [fact?: system/segment] [metric?: Y% / from A to B] in [fact?: period] by [fact?: technical method/action]" (ask the user for the method and numbers) |
| One generic CV for many roles | A master CV plus a tailored variant per role family |

## Before/after format in the review
Never invent fake numbers or fake methods in a review's "After" line. Show the target structure with `[metric?: ...]` and `[fact?: ...]` placeholders until the user supplies the real details:
```
- Before: "Worked on the payment service and helped improve latency."
- After:  "Reduced payment API p95 latency from [metric?: baseline ms] to [metric?: result ms] by [fact?: technical change you made, e.g. caching / indexing / async processing], handling [metric?: request volume]."
```

## Delivering a strengthened version
1. **Interview first:** Ask the user the discovery questions from your review (covering missing technical stack, architecture, personal ownership, methods, and metrics) before generating the draft.
2. Write `Firstname_Lastname_CV_DRAFT.md` (in the format from `markdown-format.md`) using the user's confirmed answers, with `> ` notes and `[^n]` citations.
3. Run `python3 scripts/render_docx.py ..._DRAFT.md -o ..._DRAFT.docx`.
4. Re-run `doc_lint.py` and re-score with the rubric. Report the before → after score and fine-tune with the user.
5. After the user approves: `--final --clean-md` → clean `.md` + `.docx`.
