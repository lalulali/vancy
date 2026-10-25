# AI Product Manager (AI PM) Interview Layer

Use this reference alongside `frameworks.md` whenever the role is an **AI PM** (foundation-model lab, AI-native product, applied ML/GenAI team) or when a traditional PM interview includes an AI/ML feature, strategy, or metrics prompt. Citation numbers refer to `evidence-pm-interviewing.md`.

## Contents
1. What interviewers specifically test in AI PM loops
2. The AI Product Sense 8-step framework
3. Architecture choice matrix: Rules vs. Prompting vs. RAG vs. Fine-tuning vs. Agents
4. Designing Evals (offline, online, and release gates)
5. AI metrics, unit economics, and latency trade-offs
6. Safety, trust, human-in-the-loop UX, and governance
7. Worked AI-PM answer outlines across all categories

---
## 1. What interviewers specifically test in AI PM loops
1. **Problem-first discipline:** Can you tell when AI/LLMs are the *wrong* tool and a deterministic rule, search index, or simpler UX solves 80% of the pain at 1% of the cost?
2. **Probabilistic UX design:** Because models are non-deterministic and can hallucinate, how do you design confidence thresholds, citations, diff/preview flows, undo, and graceful fallbacks?
3. **Evaluation rigour ("Evals"):** How do you measure quality when there is no single exact-match answer?
4. **System & data fluency:** Do you understand the trade-offs between context windows, RAG, fine-tuning, tool-calling agents, data flywheels, and cold-start problems?
5. **Unit economics & latency:** Can you calculate cost per task (input/output tokens, retrieval, GPU/API cost) and prevent heavy users from destroying gross margin?
6. **Safety, security & compliance:** How do you defend against prompt injection, PII leakage, copyright/data-licensing issues, and biased outputs [3][4]?

---
## 2. The AI Product Sense 8-step framework (extends Product Sense)
1. **Clarify & define the job-to-be-done:** What is the user trying to accomplish, what is the current baseline workflow, and **what is the cost of a wrong answer** (low in creative brainstorming; critical in medical, legal, or financial actions)?
2. **Justify AI fit + non-AI baseline:** Why does this need ML/LLM (unstructured inputs, synthesis, semantic reasoning, personalisation) rather than deterministic rules or keyword search? Define the simplest non-AI baseline first.
3. **Choose the autonomy level (UX pattern):**
   - *Passive/Ambient:* Auto-tagging, ranking, smart defaults.
   - *Copilot (Human-in-the-Loop):* Drafts, suggests, or highlights with a 1-click accept/edit/reject flow.
   - *Autopilot / Agent (Human-on-the-Loop):* Executes multi-step actions within bounded permissions, pausing for human approval on high-stakes/irreversible steps (e.g., sending money, deleting data, emailing external clients).
4. **Data & model approach (§3):** Context engineering / prompting, RAG over proprietary data, fine-tuning for style/format/latency, or tool-calling agent. Address cold-start data and the feedback flywheel.
5. **Evaluation & launch bar (§4):** Offline golden set + rubric, LLM-as-judge calibrated to human experts, red-teaming, and online shadow/A-B metrics.
6. **Trust, safety & failure UX (§6):** Citations, uncertainty cues, guardrails, prompt-injection defence [4], and human escalation.
7. **Unit economics & latency budget (§5):** Target Time-to-First-Token (TTFT), end-to-end latency, token cost per successful task, caching, and model routing.
8. **Staged rollout:** Internal dogfood -> shadow mode -> trusted tester beta -> % ramp with automated rollback triggers.

---
## 3. Architecture choice matrix: Rules vs. Prompting vs. RAG vs. Fine-tuning vs. Agents

| Approach | Best when... | Pros | Cons / Risks |
|---|---|---|---|
| **Rules / Heuristic / Search** | Logic is deterministic, auditable, or exact-match | Fast (<20ms), cheap, 100% predictable, easy to debug | Brittle on unstructured language or novel phrasing |
| **Prompting + In-Context / Caching** | Fast MVP; general reasoning or formatting on bounded inputs | Fastest time-to-market; no training pipeline; prompt caching cuts repeat input cost | Context-window cost/latency grows; knowledge stops at cutoff |
| **RAG (Retrieval-Augmented Generation)** | Answers must be grounded in fresh, private, or rapidly changing docs with citations | Fresh data without retraining; enforces access control per user; provides verifiable citations | Retrieval quality bottleneck (chunking, hybrid BM25 + vector search, reranking needed) |
| **Fine-Tuning (SFT / DPO / LoRA)** | Need strict output schema/tone, domain jargon, or distilling a large model into a fast/cheap small model | Lower inference latency and token cost at scale; consistent style/behaviour | Does not reliably teach new factual knowledge; requires curated training data + MLOps upkeep |
| **Multi-step Agent (Tool use + Planning)** | Task requires multi-step reasoning, calling external APIs/databases, and verifying results | Automates end-to-end workflows across systems | Compounding error rates across steps (`0.9^5 = 59%`), higher latency/token cost, tool-safety risks |

*Interview rule of thumb:* Start with **Prompting + RAG** to validate user value and collect real interaction data, then **fine-tune or distil** into a smaller model once volume, latency, or unit-economics justify the investment.

---
## 4. Designing Evals (offline, online, and release gates)

Interviewers frequently ask: *"How do you know the AI feature is ready to ship, and how do you stop regressions when prompts or models change?"*
1. **Offline Golden Dataset (200-1,000+ stratified examples):**
   - *Happy path (50%):* Common high-volume user intents.
   - *Hard / edge cases (30%):* Ambiguous queries, long contexts, multi-lingual, missing retrieval context ("I don't know" expected).
   - *Adversarial / Red-team set (20%):* Jailbreaks, indirect prompt injections, PII requests, toxic/off-policy inputs [3][4].
2. **Grading stack:**
   - *Deterministic code checks:* JSON schema validity, citation link existence, forbidden words, latency, token count.
   - *LLM-as-Judge (with rubric):* Score faithfulness/groundedness (does the answer contradict or invent beyond retrieved chunks?), completeness, and tone on a 1-3 or pass/fail scale. **Crucial caveat:** always validate LLM-as-judge agreement (e.g., Cohen's kappa / precision-recall) against a human-annotated subset, and mitigate judge biases (verbosity bias, position bias in pairwise comparisons).
   - *Human expert review:* Domain specialists audit disagreements and refresh the golden set monthly from production failures.
3. **Online Production Signals:**
   - *Implicit user feedback (high volume, high signal):* Acceptance rate, **edit distance** between AI draft and final sent text, copy/share rate, immediate re-prompt or query reformulation rate, manual override/undo rate.
   - *Explicit feedback (low volume, biased toward extremes):* Thumbs up/down with reason tags.

---
## 5. AI metrics, unit economics, and latency trade-offs

| Metric family | Core KPIs to name | Typical Guardrails |
|---|---|---|
| **Task Quality** | Task completion rate, groundedness / citation accuracy, win-rate vs. human or previous model, edit distance | Hallucination / ungrounded-claim rate, "I don't know" false-refusal rate |
| **User Value & Adoption** | % DAU adopting feature, retained weekly AI-assisted tasks per user, time-to-complete task | User override/revert rate, support escalation rate |
| **Business & Efficiency** | Ticket deflection rate, conversion lift, net revenue retention, gross margin per AI user | Customer CSAT/NPS on deflected vs. human-handled sessions |
| **System & Cost** | Time-to-First-Token (TTFT p50/p95), end-to-end latency, cost per *successful* task (not just per query) | API error/timeout rate, token spend per user per month |
| **Safety & Policy** | Red-team pass rate, PII redaction recall | Policy-violation rate (<0.01%), prompt-injection success rate |

### Back-of-the-envelope AI unit economics levers
- **Formula:** `Daily AI Cost = Daily Queries x [(Avg Input Tokens x Input Price) + (Avg Output Tokens x Output Price)] + Retrieval/Infra Overhead`.
- **5 Levers to cut cost & latency without hurting quality:**
  1. **Model routing / cascading:** Route 70-80% of simple classification/FAQ queries to a small/fast model, reserving the frontier model for complex reasoning.
  2. **Prompt & semantic caching:** Cache system prompts/static context (KV cache) and frequent identical/near-identical queries.
  3. **Tighter RAG chunking & reranking:** Pass the top 3-5 reranked chunks instead of stuffing 50k tokens into every prompt.
  4. **Output length control & structured decoding:** Constrain output tokens; stream responses so perceived latency (TTFT < 500ms) feels instant.
  5. **Fine-tuning / distillation:** Distil a frontier model's outputs on your specific task into a smaller open-weights or mini model.

---
## 6. Safety, trust, human-in-the-loop UX, and governance [3][4]
- **Hallucination design:** Never promise 100% accuracy. Ground answers via RAG, show inline clickable source citations, train/prompt the model to abstain when retrieval confidence is low, and show a visual diff before applying changes.
- **Prompt injection (direct & indirect) [4]:** Treat retrieved web pages, emails, PDFs, and third-party plugin outputs as **untrusted data**. Isolate system instructions, strip or sandbox untrusted instructions, and require explicit user confirmation before any state-changing tool call (e.g., sending an email, transferring funds, modifying records).
- **Privacy & IP:** Zero-data-retention (ZDR) agreements with model providers, PII scrubbing before logging/training, tenant-isolated vector indexes (respecting RBAC/ACLs at retrieval time so User A cannot retrieve User B's docs), and opt-in training controls.

---
## 7. Worked AI-PM answer outlines across categories

- **Product Sense (AI):** *"Design an AI clinical-note assistant for doctors."*
  - *Persona & pain:* Outpatient primary-care physicians spending 2 hours/night on EHR charting ("pajama time"). High cost of error (medication dosage or missed allergy).
  - *Solution (Copilot, not Autopilot):* Ambient patient-consented audio capture -> structured SOAP note draft with inline audio-timestamp links for every clinical claim -> mandatory physician review/sign-off with 1-tap edit before writing to EHR.
  - *Evals & Metrics:* Offline clinical-accuracy rubric graded by physician panel (especially drug/dosage recall and zero fabricated findings); North Star = chart-closure time saved per visit; Guardrail = physician edit rate on medication/allergy fields and post-visit addendum/correction rate.
- **Product Strategy (AI):** *"How should we price an enterprise AI copilot (per seat vs. usage vs. outcome)?"*
  - *Trade-off:* Per-seat ($X/user/mo) is predictable for IT buyers but risks negative gross margin if power users run 500 heavy agent tasks/day; pure usage (per token) creates buyer "meter anxiety" and stalls adoption; outcome-based (per resolved support ticket) aligns value when attribution is clear (like customer support deflection) but fails for open-ended knowledge work.
  - *Recommendation:* **Hybrid tiered seat + pooled usage allowance** for knowledge work (or **per-verified-resolution** for support bots), paired with model routing to protect a >70% gross margin floor.
- **Analytical & Metrics (AI):** *"Hallucination complaints spiked 30% this week. Investigate."*
  - *Diagnostic tree:* (1) Measurement check (did the LLM-as-judge prompt or user feedback UI change?); (2) Model/Prompt change (silent provider model weight update, system prompt edit, temperature change); (3) Retrieval/Data pipeline change (broken document ingestion, stale embeddings, chunking bug, missing ACL filter returning empty context); (4) Query mix shift (new campaign or viral topic outside knowledge base). Mitigate via immediate rollback to pinned model/prompt + add failing queries to regression eval suite.
- **Execution (AI):** *"Model accuracy is 85%; safety wants 95%; sales promised a launch next week."*
  - *Resolution:* Slice the 85% by query risk tier and confidence score. Launch next week **in scoped Copilot/draft-only mode** for high-confidence queries where 85% saves time and human review catches the 15%, while hard-blocking or routing low-confidence/high-risk intents to deterministic fallbacks or humans. Agree on the quantitative gate to unlock Autopilot in Phase 2.
