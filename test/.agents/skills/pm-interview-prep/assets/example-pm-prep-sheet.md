---
doc: interview
template: modern
page: a4
lang: en-GB
---

> All names, company details, and figures in this file are fictional examples for study; never reuse them as real facts.

# Alex Morgan - PM Interview Prep Sheet (Northwind Payments, Senior PM)

**Track:** Traditional + AI PM · **Target level:** Senior PM · **Loop format:** 4 x 45-min virtual rounds (Product Sense, Analytical & Metrics, Strategy & AI, Execution)

## 1. Product & Market Positioning Notes
- **Core product job-to-be-done:** Help small and mid-sized online merchants accept cross-border payments and settle in local currency with predictable fees.
- **North Star metric hypothesis:** Weekly settled cross-border payment volume (GMV) from active merchants with zero unrecovered chargebacks.
- **Primary user segments:** (1) Micro-exporters (<£20k/mo volume, price- and setup-sensitive); (2) High-growth D2C brands (£20k-£500k/mo, care about authorisation rates and payout speed); (3) B2B SaaS platforms (care about API reliability, webhooks, and reconciliation).

## 2. Three Product Improvement Ideas (Ready for Product Sense / Strategy)
- **Quick win (Activation):** Replace manual PDF bank-statement upload during KYB onboarding with instant open-banking verification and live status milestones, targeting the 40% drop-off between signup and first transaction.
- **Core bet (Growth & Retention):** Intelligent payment routing that retries soft-declined cross-border cards via local acquiring rails, lifting authorisation rate by an estimated 1.5-2.5 percentage points.
- **AI PM bet (Copilot with Guardrails):** Dispute-response Copilot that drafts chargeback evidence packets from order, shipping, and communication logs using RAG, with mandatory merchant 1-click review before submission to card schemes.

## 3. Metric Tree & Diagnostic Checklist (Ready for Analytical Round)
- **Acquisition & Activation:** Sign-ups -> KYB verified rate -> time-to-first-live-payment -> D7 activation rate.
- **Engagement & Monetisation:** Active merchants (MAU) -> average transactions per merchant -> authorisation success rate -> net take rate after scheme fees and fraud losses.
- **Guardrails:** Checkout p95 latency (<400ms), false-positive fraud decline rate, chargeback ratio (<0.5%), support tickets per 1,000 transactions.
- **5% metric drop checklist:** (1) Telemetry/logging delay -> (2) Geo/acquirer/card-scheme cut -> (3) Client SDK/API version cut -> (4) Recent fraud-rule or pricing deployment -> (5) External payment-rail outage.

## 4. AI Evals & Unit Economics Cheat Card
- **Offline evals:** 300-case golden set of historical disputes (happy path, missing tracking info, adversarial prompt injection in customer emails); graded on citation faithfulness and scheme-rule compliance.
- **Online metrics:** Draft acceptance rate, edit distance before submission, dispute win-rate lift vs. manual baseline, cost per accepted packet (<£0.08 target via small-model routing + prompt caching).

## 5. Questions to Ask the Interviewers
- **Product direction:** Where do you see the biggest friction today between merchant onboarding speed and risk/compliance thresholds?
- **Metrics & trade-offs:** When authorisation rate and fraud loss move in opposite directions on an experiment, how does the team make the shipping call?
- **AI roadmap:** Which merchant or internal operations workflows have the strongest data flywheel for AI assistance over the next 12 months?

