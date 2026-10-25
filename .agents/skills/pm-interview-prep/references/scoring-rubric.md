# PM Interview Scoring Rubric

Score each dimension 1-5 with a quoted piece of evidence from the candidate's answer. Be calibrated: **3 = solid/competent**, **4 = strong hire signal**, **5 = exceptional (rare)**. Most first attempts land between 2.0 and 3.2. Citation numbers refer to `evidence-pm-interviewing.md`.

## Dimensions and anchors (1 / 3 / 5)
| Dimension (`key`) | 1 (Weak) | 3 (Solid) | 5 (Exceptional) |
|---|---|---|---|
| **Structure** (`structure`) | Rambling, jumps straight to solutions, no signposting | Announces a logical framework, follows it, states a conclusion | Tailors structure to the prompt, signposts transitions, adapts smoothly to interruptions, closes with a crisp recommendation |
| **Insight & rigour** (`insight`; aliases: `user_insight`, `business_insight`, `data_rigour`, `analytical`) | Generic personas ("all users"), surface-level market/data claims, unlabelled guesses | Behavioural user segments, sound market/funnel logic, or clear technical/estimation breakdown | Non-obvious user/market/system insight, quantified assumptions, checks data integrity and edge cases |
| **Creativity & depth** (`creativity`) | Only obvious copycat ideas or shallow 1-line answers | 3-4 distinct ideas or options with reasonable depth on the chosen one | Novel yet feasible ideas tied to root pain; concrete MVP flow, system architecture, or experiment design |
| **Prioritisation & judgement** (`prioritisation`) | Lists everything equally; refuses to choose ("it depends") | Picks one segment and one solution/option with stated criteria | Explicit trade-off matrix (RICE, moat, cost/risk), names what is cut, sets guardrails and kill criteria |
| **Communication** (`communication`) | Hard to follow, defensive when probed, silent math | Clear, states assumptions aloud, collaborative with interviewer | Concise, executive-ready, checks in at transitions, handles adversarial probes with poise and data |
| **AI depth** (`ai_depth` - AI track only) | "Add an LLM" with no baseline, evals, or failure handling | Covers baseline, RAG vs. fine-tuning, hallucination risk, and basic evals | Specifies offline/online eval rubric, confidence UX/human-in-the-loop, latency/token unit economics, and safety/prompt-injection guardrails [3][4] |

## Category weights (traditional track, summing to 100)
| Category (`--category`) | Aliases | Structure | Insight | Creativity | Prioritisation | Communication |
|---|---|---|---|---|---|---|
| `product_sense` | `design`, `product_design`, `improvement` | 20 | 30 | 20 | 15 | 15 |
| `strategy` | `product_strategy`, `business`, `monetisation`, `gtm` | 20 | 30 | 15 | 20 | 15 |
| `metrics` | `analytical`, `analytics`, `kpi`, `ab_test` | 25 | 30 | 10 | 20 | 15 |
| `execution` | `prioritisation`, `prioritization`, `roadmap`, `tradeoffs` | 25 | 20 | 10 | 30 | 15 |
| `technical` | `technical_acumen`, `system_design`, `architecture` | 20 | 35 | 10 | 15 | 20 |
| `estimation` | `fermi`, `market_sizing` | 25 | 35 | 5 | 15 | 20 |
| `growth` | `pricing`, `funnel` | 20 | 30 | 15 | 20 | 15 |
| `critique` | `teardown`, `take_home`, `prd` | 20 | 30 | 15 | 20 | 15 |

**AI track (`--track ai`):** Adds `ai_depth` at weight **20** and scales the five base weights by **0.8** (total weight = 100).

## Level bands and target bars (`--level`)
| Weighted score | Practice band | Target bar by role level |
|---|---|---|
| `< 2.0` | No hire - needs fundamentals | — |
| `2.0 - 2.9` | Lean no hire | — |
| `3.0 - 3.4` | Borderline / lean hire | **APM / Rotational PM** target bar: `>= 3.2` (strong structure, user empathy, coachability) |
| `3.5 - 3.8` | Hire | **PM (IC)** target bar: `>= 3.5` (sharp prioritisation, metrics rigour, clear MVP) |
| `3.9 - 4.2` | Strong PM / Senior hire | **Senior PM** target bar: `>= 3.9` (strategic framing, non-obvious trade-offs, handles ambiguity) |
| `> 4.2` | Exceptional / Group hire | **Group / Principal / Director** target bar: `>= 4.2` (portfolio vision, unit economics, org/ecosystem leverage) |

*Note:* These bands are a structured practice heuristic [1], not a guarantee of any employer's hiring decision.

## Red flags (`--flags` in `score_sheet.py`)
When a red flag occurs, cap the affected dimension(s) at **2.0** until the habit is fixed:
- `no_clarify` — Jumps into solutions or math without clarifying scope/goal (caps `structure` and `communication` at 2.0).
- `no_recommendation` — Ends with "it depends" or lists options without choosing (caps `prioritisation` at 2.0).
- `no_metrics` — Proposes a product or launch with no success metric or no guardrail/counter-metric (caps `insight` at 2.0).
- `ignored_constraints` — Ignores stated constraints or interviewer hints (caps `communication` at 2.0).
- `fabricated_facts` — Presents invented company/market statistics as certain fact instead of labelled assumptions (caps `insight` at 2.0).
- `ai_handwaving` — Says "use AI/LLM" with no non-AI baseline, eval plan, failure UX, or cost thinking (caps `ai_depth` at 2.0).
- `defensive` — Argues defensively when challenged on a follow-up probe (caps `communication` at 2.0).

## Scorecard feedback format
```markdown
**Category:** [category] | **Track:** [traditional / ai] | **Level target:** [apm / pm / senior / group]
**Weighted score:** X.XX / 5.00 ([Band] - [meets / below level target])
**Red flags triggered:** [none or list]

| Dimension | Raw -> Effective | Weight | Quoted evidence from answer | Specific gap |
|---|---|---|---|---|
| Structure | ... | ... | "..." | ... |

### What worked (keep doing)
- ...

### Top 3 fixes (ranked by score impact)
1. **[Dimension]**: ...
   - *Before (your answer):* "..."
   - *After (stronger outline):* "..."

### Next 5-minute drill
- ...
```
