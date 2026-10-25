# Negotiation Playbook

Citation numbers refer to `evidence-negotiation.md`.

## Contents
1. Principles
2. Stages
3. What can be negotiated
4. Deciding priorities and walk-away point
5. Making the counter
6. Handling responses
7. Special situations
8. Regional and cultural notes
9. Checklist

## 1. Principles
- **The goal is a good package and a good relationship.** You and the employer are on the same side of the table once an offer is made [6].
- **Be honest.** Do not bluff about competing offers, current pay, or other facts. Do not fabricate market data.
- **Be prepared.** Evidence beats confidence; the counter should rest on researched facts and your value.
- **Be warm and specific.** Show enthusiasm for the role, then ask for a specific change with a reason [9].
- **Keep it in writing.** Ask for the total package in writing and confirm the final agreement in writing [8].
- **The candidate decides.** Offer options and trade-offs; never push.

## 2. Stages
| Stage | What to do |
|---|---|
| **1. Prepare early** | Research pay (see `market-research.md`). Know your priorities and walk-away point before any pay talk |
| **2. Early pay questions** | If asked for expectations before you have an offer, ask the range for the role first. If pressed, give a researched range, not a single figure. Check local rules about past-pay questions [15][16][17] |
| **3. Receive the offer** | Thank them, show enthusiasm, ask for the details in writing, and ask for time (a few days is common) [7] |
| **4. Evaluate** | Compare the whole package (`scripts/offer_calc.py compare`), covering base, bonus, equity, benefits, leave, flexibility and growth [6][10] |
| **5. Counter** | Make one clear, justified request, by phone or email, then follow up in writing [9] |
| **6. Resolve** | Trade across items. Reach agreement. Confirm all terms in the written offer before resigning |
| **7. Accept or decline** | Courteous either way; keep the relationship |

## 3. What can be negotiated
Base salary · sign-on bonus · annual bonus target or guarantee for year one · equity (amount, vesting, refreshers) · title/level · start date · review timing (for example, a pay review after 6 months) · paid leave · remote or hybrid terms · learning/certification budget · relocation or visa support · retirement contribution · notice-period buy-out · severance terms (senior roles) · equipment/allowances.
Some employers have fixed pay bands (common in government and large organisations). Then negotiate the non-salary items [6].

## 4. Deciding priorities and walk-away point
Before countering, write down:
1. **Must-haves** (non-negotiable terms).
2. **Targets** (what you would be delighted with).
3. **Trade-offs** (what you would give up for what).
4. **Walk-away point** (the package below which you decline), based on your alternatives: the current job, other offers, or your search runway.
5. **The evidence** supporting your ask (market data, scope, results, scarce skills).

## 5. Making the counter
- Use the researched range. Evidence suggests that ambitious first numbers tend to produce better outcomes but increase the risk of impasse, so tie the number to evidence [4][5]. Aim in the upper part of the researched range, not above it.
- State one number (or a tight range) and the reason: market data, scope and level, a specific skill, and a concrete result you will deliver.
- Express enthusiasm. Say you would accept if the terms are met **only if that is true**; do not use it as a bluff.
- Offer a package: "If base is fixed, could we look at a sign-on bonus or a 6-month review?"
- Use `scripts/offer_calc.py position` to see where the offer sits in your researched range and to size the counter. Its `--offer` is a **base salary** figure: compare it with a base range, not with total compensation. The counter band it prints runs from the middle of your range (or the offer plus 5%, if that is higher) up to the top of the range; it only suggests where an evidence-backed ask could sit and is not a market figure.
- If the offer is already at or above the top of your researched range, `position` prints **no counter band**: do not counter with a token +5% on base. Negotiate non-salary terms instead (sign-on, review date, leave, equity, flexibility).
- Send emails from `scripts-and-emails.md`, adapting them to the facts.

## 6. Handling responses
| Response | Approach |
|---|---|
| "That is our best offer." | Ask what flexibility exists elsewhere (sign-on, review date, leave, remote days, equity). Ask what would make a higher level or band possible |
| "The band is fixed." | Negotiate the non-salary items, or ask how to progress within the band and when the next review is |
| "We need an answer today." | Ask what drives the deadline, and ask for a short extension. Do not accept under unexplained pressure; if it truly cannot move, decide against your priorities |
| "What is your current salary?" | Where a salary-history ban applies you need not answer. Where one does not, decline politely or give a researched range ("I'd rather focus on the value of the role and the market range"). Never state a false current figure; pay is often verified by payslips or a background check |
| Silence | Follow up once politely after a few business days |
| They meet your number | Accept gracefully; confirm in writing |
| They counter partially | Decide using your priorities and walk-away point; trade across items |

## 7. Special situations
- **Internal promotion or raise:** gather your results and scope growth, benchmark the role, and ask your manager for a conversation, not an ambush. Use the same evidence-first approach.
- **Current employer counters your resignation:** treat it cautiously. Consider why you wanted to leave and whether the underlying issues change. There is no reliable statistic to quote either way.
- **Contract/freelance:** negotiate rate, scope, payment terms, revision limits, and kill fees in writing. Check local employment-status rules.
- **Multiple offers:** be honest about timing. Do not invent offers. Ask each employer for a decision date that works for you.
- **Early-career:** employers still expect some negotiation in many markets. Focus on non-salary items if pay is fixed. Ask for a defined review date.
- **Career changer:** the level and title matter. Negotiate level carefully and use transferable results as evidence.

## 8. Regional and cultural notes
- Negotiation norms differ: expected and routine in some markets, rare or sensitive in others. Ask the user where the job is and what is normal there.
- Pay transparency rules differ and change [11][12][13][14][15][16][17][18][19]. Ask where the job is:
  - **US:** state and city laws differ on posting ranges and salary-history questions. Check the state or city labour department page.
  - **EU:** Directive 2023/970 gives applicants the right to the initial pay or range and bars employers from asking about pay history. The transposition deadline (7 June 2026) has passed and most Member States are late (as at 12 October 2026 only Italy, Lithuania, Malta and Slovakia had met it). Where your country has transposed it, you can ask for the range before the interview and need not answer pay-history questions; where it has not, the national rules apply as before. Check the national statute that implements it [17][18][19].
  - **UK, Canada, Australia, Singapore and elsewhere:** check locally.
- **India** (convention, unsourced; check locally): offers are often framed as a percentage "hike on current CTC", and employers commonly verify pay with payslips, so never inflate a current figure. Compare fixed versus variable pay and the notice period.
- **Gulf (GCC)** (convention, unsourced; check locally): compare end-of-service gratuity, housing and other allowances, flights and visa support, not just the headline salary.
- **Equity** (check locally for tax): ask whether it is RSUs or options, the vesting schedule and any cliff, and when tax is due (often at vesting for RSUs, at exercise for options). Public-company RSUs are liquid once vested; private-company equity is illiquid and may be worth little. Working haircuts: public RSUs roughly 10–25% for price risk, private equity roughly 70–100%; options are valued on the spread over the strike, not the grant value, so `offer_calc.py` needs a value you work out yourself (unsourced working assumptions; see `evidence-negotiation.md` section D).
- Some countries pay a 13th or 14th month, statutory bonuses, mandatory retirement contributions, or long notice periods. Capture them in the comparison.
- Probation periods, notice periods, and non-compete clauses vary widely. Read the contract.
- This skill gives general career guidance, not legal or financial advice.

## 9. Checklist
- [ ] Research done with at least three independent sources; range recorded.
- [ ] Priorities, trade-offs, walk-away point written down.
- [ ] Total package received in writing; every component valued.
- [ ] Counter is specific, justified, enthusiastic, and honest.
- [ ] Every agreed term confirmed in the written offer before resigning.
