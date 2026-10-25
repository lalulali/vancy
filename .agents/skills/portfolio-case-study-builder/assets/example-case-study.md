---
doc: case-study
template: modern
page: a4
lang: en-GB
---

> All names and figures in this file are fictional; never reuse them. Any resemblance to real people or companies is coincidental. The figures are deliberately rounded or given as ranges so they cannot be matched to a CV or LinkedIn profile (see the linkage check in `confidentiality-and-ethics.md`).

# Cutting merchant onboarding time by about three quarters
Product manager | Recent project | Squad of about 15 (engineering, design, data, risk) | Payments company (name withheld by agreement)

## Overview
A payments company was losing new small-business customers during sign-up: it took more than a week on average to start taking payments, and fewer than half of applicants activated. I led the redesign of onboarding and identity checks. Onboarding time fell by about three quarters, activation rose by roughly 15 percentage points, and support tickets about onboarding dropped by more than a third, with fraud losses unchanged.

![Before and after view of the onboarding funnel, showing onboarding time falling by about three quarters](img/funnel-before-after.png)

## My role
I was the product manager and owned the onboarding funnel metrics. I wrote the problem statement and success criteria, ran customer discovery, led prioritisation with a squad of about 15, and negotiated the rollout plan with risk and compliance. Engineering built the verification integration, design owned the new status screens, and data built the funnel dashboard.

## The problem
New merchants waited days to take their first payment. I interviewed a few dozen merchants and reviewed several hundred support tickets. Three findings stood out:
- Most delays (roughly 60%) came from manual identity checks, not from merchant errors.
- Merchants received no status updates, so many contacted support or abandoned the sign-up.
- Fraud checks were applied identically to low-risk and high-risk applicants.

## Constraints
- Two quarters to deliver and no increase in fraud losses.
- A regulatory requirement to verify identity before activation.
- A small data team, so reporting had to reuse existing tools.

## Process
1. **Mapped the funnel** end to end and measured time spent at each step.
2. **Ran merchant interviews** and tagged support tickets to size each cause.
3. **Defined success** with risk and compliance: activation rate, time to first payment, and fraud loss rate as a guardrail.
4. **Piloted** automated checks on 10% of traffic for four weeks.
5. **Scaled** in stages once the guardrail held, and rebuilt the status emails and screens.

## Key decisions
- **Automate rather than hire.** Adding reviewers would have cut waiting time by about a third but would not scale. I chose automation with a manual fallback because it solved the cause, not the symptom.
- **Risk-tiered checks instead of one flow.** Low-risk applicants went through the lightest compliant path, which kept fraud flat because high-risk cases still received full review.
- **Pilot before launch.** I accepted a four-week delay so risk and compliance could review real data, which shortened sign-off later.

## Outcome
- Onboarding time: down by about three quarters.
- Activation rate: up by roughly 15 percentage points within two quarters.
- Onboarding support tickets: down by more than a third.
- Fraud losses: unchanged against the agreed guardrail.

## What I learned
I should have agreed the risk metric with compliance before proposing the change, not after. Next time I would involve them in discovery from day one, and test status messaging earlier, because it drove a large share of the drop in tickets.
