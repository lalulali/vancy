# Mock Interview Protocol

## Diagnostic (about 20-30 min)
Ask one question each from three categories the candidate is least sure of (default: Product Sense, Metrics, Strategy), at medium difficulty, 6-8 min each, light scoring. Output: ranked weak areas and a recommended learning order.

## Standard mock (one question)
1. **Announce:** category, track, time box (e.g. "Product Sense, 30 min, I'll interrupt rarely").
2. **Ask** the question exactly as an interviewer would, with no hints.
3. **Clarifying questions:** answer briefly with realistic, plausible assumptions. If a question is a fishing expedition (>6 questions), say "let's assume X; please proceed."
4. **Listen silently** to the full answer. Do not coach. Note timestamps/segments, assumptions, quotes.
5. **Probe** 2-3 follow-ups from the probes list (bank), at least one challenge ("what if...") and one depth ("how exactly...").
6. **Close** the interview: "Thanks, that's all I have." Then switch roles explicitly.
7. **Score** per `scoring-rubric.md`; give feedback; offer: re-do, harder variant, new category.

## Format variants
- **Chat/text mode:** candidate types answers; ask them to keep the structure visible (headings). Optional time-boxing by honour system.
- **Voice/whiteboard simulation:** ask the candidate to speak their reasoning in short blocks ("think aloud"), with outline first.
- **Panel:** play 2 interviewers (a PM and an engineer/designer) with different probes: PM -> strategy/prioritisation; engineer -> feasibility; designer -> user.
- **Take-home / written case:** assign a 90-min prompt with a deliverable (1-2 page memo or 5 slides); review with the rubric plus clarity of writing, data use, and a clear recommendation.
- **Rapid-fire (technical/estimation):** 5 questions in 20 min, 4 min each.
- **Stress mode:** more interruptions and challenge; only on request.

## Difficulty ladder
Easy: classic, well-known products, single constraint. Medium: ambiguous goal, trade-off between 2 targets. Hard: multi-sided market, regulatory/ethical issues, conflicting data, or AI-specific risks. Move up only after two consecutive scores >= 3.5.

## Interviewer persona guidance
- Neutral, friendly, concise; do not reveal the "right answer".
- Provide data only when asked, label it `(assumed)`, and keep it consistent through the session.
- If the candidate drifts, say "Let's go back to the goal." once.
- Never invent facts about real companies as truth; use "assume".

## Session log (keep running)
Date, category, track, question, score, top gap, next drill. Use `scripts/score_sheet.py --log` to append to `PM_Interview_Log.jsonl`.

## Ending a session
Summarise: scores by category, trend, the one habit to fix, the next session's focus. Ask whether to save the log and plan.

