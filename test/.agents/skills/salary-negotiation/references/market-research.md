# Researching Pay (Without Inventing Numbers)

Citation numbers refer to `evidence-negotiation.md`.

## Rule
**You do not know the user's market rate.** Do not state a salary as fact unless the user supplied it or you cite a source you opened. Your job is to help them gather, triangulate and record the evidence, then position an ask using `scripts/offer_calc.py position`.

## Contents
1. Sources, strongest first
2. Triangulating
3. Adjusting for the role
4. Total compensation
5. Recording the research
6. Web research (if your tools allow it)

## 1. Sources, strongest first
| Source | Use | Caveats |
|---|---|---|
| The posting's stated pay range | The employer's own budget for the role | Not all postings include one; ranges can be wide. Rules about posting ranges differ by place: some US states require them [14], and EU employers should give the range before interview where the Directive has been transposed, which many Member States have not yet done [17][18]. Elsewhere, check locally |
| Official labour statistics for the country (national statistics agencies, labour departments, or professional bodies) | Median and distribution by occupation and region | Often lag by a year or more; occupation classes are broad |
| Reputable salary guides from recruitment firms, in your industry and country | Current ranges by seniority | Vendor-run; read the method; note the date |
| Peers, mentors and professional networks | Real, current, company-specific figures | Small samples; be careful with confidentiality; collect several |
| Recruiters and the employer (asking the range) | The budget for this role | Recruiters represent the employer or the candidate, depending on the arrangement |
| Crowdsourced salary sites | Directional comparison | Self-reported, unverified, skewed samples |
| Your own current pay and the value of your results | Your floor and your evidence | Check local rules before sharing past pay: some places bar employers from asking [15][16][17]. Elsewhere, check locally |

## 2. Triangulating
- Use at least **three independent sources** and keep them in a table.
- Weight the posting range, official statistics, and recent peer data most heavily.
- Record the date, source, role definition, region, company size and currency.
- Exclude outliers that you cannot explain.
- Turn the results into three numbers: **LOW, MID, HIGH** for the role, level and place.

## 3. Adjusting for the role
Location and cost of living · seniority and scope (team size, budget, P&L) · industry · company size and stage · specialist or scarce skills · remote versus on-site · contract versus permanent · hours and on-call · currency and tax regime. Match like with like. A "product manager" at a seed-stage startup and at a global bank are different data points.

## 4. Total compensation
Compare the whole package, not just base (`scripts/offer_calc.py compare`):
base · bonus (target and actual payout history) · equity (type, vesting, strike, liquidity; discount it for risk) · retirement contribution · allowances · benefits you would otherwise pay for · leave · flexibility · learning budget · relocation. Ask how often the bonus pays out in practice. Equity differs by type: public-company RSUs are liquid once vested (a haircut of roughly 10–25% is a common working assumption, unsourced); private-company equity is illiquid and may be worth little (70–100% haircut is a cautious working assumption, unsourced); options are worth the spread over the strike, not the grant value. `offer_calc.py compare` takes an optional `equity_type` per offer (`public` suggests a 15% haircut, `private` 70%, no type 50%); an explicit `equity_haircut_pct` always wins. It has no strike or tax model, so for options work out the spread yourself first, enter your own `equity_haircut_pct`, and check local tax rules. Also check the vesting schedule and any cliff, and that tax is often due at vesting (RSUs) or exercise (options): check locally.

## 5. Recording the research
```
Role/level: ...  Place: ...  Date: ...
| Source | Date | Role match | Low | Mid | High | Notes |
Decision: LOW = ...  MID = ...  HIGH = ...
Confidence: low / medium / high, because ...
```
Keep this table; it is the evidence behind the counter. Save it with the rest of the application in `artifacts/output/<Company>_<Role>/`; `artifacts/` is git-ignored personal data, and user-supplied figures come from `artifacts/input/`. To render it as Word, start the file with front matter `doc: negotiation` (optional `template`, `page`, `lang`) and write it in the standard Markdown (no tables render; use bullets).

## 6. Web research (if your tools allow it)
Search for the posting range, the employer's pay-transparency page, official statistics for the occupation, and recent salary guides. Open the page, read the method and date, and cite it in the draft notes. If you cannot access the web, ask the user for the figures and say what you could not verify.
