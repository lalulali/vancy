# CV Review Rubric

Score each dimension 0–5 and multiply by its weight to get a total out of 100. Base every score on evidence from the document, quoting the line or giving the section. Source numbers refer to `evidence.md`.

| # | Dimension | Weight | 5 = | 0–1 = |
|---|---|---|---|---|
| 1 | **Targeting & keyword fit** | 4 | Headline matches the target title. Every must-have in the job ad is evidenced. Key terms appear naturally. (`doc_lint` keyword coverage is information, not a score threshold) | Generic CV with no target. Must-haves are missing [8][24][30] |
| 2 | **First-skim clarity** | 3 | Top third shows identity, years, domain and 2–3 signature wins. Titles, employers and dates can be scanned [4][5][24] | Wall of text. Key facts buried on page 2 |
| 3 | **Achievement focus & quantification** | 4 | Each recent role has a scope bullet and a Key Achievements block. ≥60% of bullets quantified, with baselines and timeframes [33][37] | Duty lists ("Responsible for…"). No numbers |
| 4 | **Language quality** | 2 | Strong, varied verbs. No clichés or first person. ≤2 lines per bullet. One spelling convention. No typos [8] | Clichés, filler, typos, mixed tense |
| 5 | **Structure & length** | 2 | Standard sections in a logical order. Length fits stage and market. Older roles compressed [7][42] | Wrong length for stage. Irrelevant or very old detail |
| 6 | **ATS & accessibility** | 3 | Single column. Real text. Standard headings. No tables, text boxes, images or header/footer text. Titles spelled out [27][28][63] | Contact details in header. Image or multi-column layout. Scanned PDF |
| 7 | **Consistency & credibility** | 1 | Summary, roles, dates and metrics agree. Metrics are plausible and defensible [9][32] | Contradictions, overlaps, implausible "100%" claims |
| 8 | **Compliance & bias safety** | 1 | No unnecessary personal data for the target market. No salary. No confidential employer data | Photo, DOB or marital status where not expected. Confidential figures |

Total = Σ(score × weight). Show the sum line in the report (for example `1×4 + 3×3 + … = 62`); the headline score must equal it. Bands:
- **85+**: ready to send.
- **70–84**: good, needs targeted fixes.
- **50–69**: significant rewrite.
- **<50**: rebuild (offer cv-builder).

## How to judge targeting without a job ad
Ask for the target role. If the user cannot give one, score dimension 1 against a typical posting for the CV's own headline. Say clearly that you did this.

## Severity labels for findings
- **Critical**: likely to cause rejection or an unreadable parse. Examples: no contact details, image-only file, missing must-have, glaring typos in the header, false or contradictory data.
- **High**: substantially weakens the CV. Examples: duty-only bullets, no summary, generic headline, length far off.
- **Medium**: noticeable polish issue. Examples: weak verbs, inconsistent dates, clichés.
- **Low**: nice to have.

## Report template (draft, with citations)
```markdown
# CV Review: [Name], target: [Role] ([Market])

**Score: NN/100 ([band])**: [one-sentence verdict]

| Dimension | Score | Key evidence |
|---|---|---|
| Targeting & keyword fit | n/5 | … |
| … | | |

## Top fixes (ranked by impact)
1. **[Severity] [Issue]**: where; why it matters[^n]; fix.
   - Before: "…"
   - After: "…" (new facts needed are marked [metric?])

## What's working (keep)
- …

## Keyword coverage (if a job ad was given)
Present: … | Missing but true? (ask): … | Missing, no evidence: …

## Questions for you
- …

[^n]: Source title, publisher, year, URL
```
Limit the review to the top 5–10 fixes. Prioritise; do not list every nit.
