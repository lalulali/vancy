# PM Interview Frameworks and Worked Outlines

Frameworks are scaffolds, not scripts. Adapt the steps to the prompt, announce your roadmap up front, think aloud, quantify assumptions, and always end with a clear recommendation. Citation numbers refer to `evidence-pm-interviewing.md`.

## Contents
1. Product Sense (Product Design & Product Improvement)
2. Product Strategy (Market Entry, Monetisation, Competitive Response & GTM)
3. Analytical & Metrics (Success KPIs, Metric-Drop Root Cause, A/B Testing & Trade-offs)
4. Execution & Prioritisation (Roadmap Trade-offs, Crisis Triage & Stakeholder Pushback)
5. Technical Acumen (Explaining Concepts & System Design for PMs)
6. Estimation (Fermi / Back-of-the-Envelope Math)
7. Growth, Funnel & Pricing/Packaging
8. Product Critique, App Teardown & Take-Home PRD / Case Deck
9. Time-box guide by round type

---
## 1. Product Sense (Product Design & Product Improvement)
**What it tests:** User empathy, problem framing, segmentation judgement, creative breadth, prioritisation, and product taste.
**Two classic variants:**
- **Greenfield design:** "How would you design an alarm clock for the blind?" / "Design a fridge for college students."
- **Product improvement / favourite product:** "What is your favourite product and how would you improve it?" / "Improve Spotify for runners."

**Framework (5 steps)**
1. **Clarify & set the goal (2-4 min):** Confirm scope, target platform/form factor, geography, and whether this is a startup or an existing company's product. State the mission and one primary goal (e.g., acquisition, activation, engagement, retention, or monetisation) plus key constraints.
2. **Segment users & pick ONE target persona (4-6 min):** Slice users by *behaviour and unmet need* (not broad demographics like "millennials"). Name 3 segments, pick **one** using explicit criteria (pain severity, segment size/reach, strategic fit), and walk through their step-by-step user journey to surface 3 sharp pain points.
3. **Brainstorm solutions (5-7 min):** Generate 3-5 distinct solutions mapped directly to the prioritised pain points. Include a mix of pragmatic quick wins and one ambitious "10x" bet. Avoid generic "add a social feed / add AI / add notifications" ideas unless tied to the core pain.
4. **Prioritise & specify the MVP (5-7 min):** Score solutions on **User Impact x Frequency vs. Engineering/Operational Effort & Risk**. Pick one winning solution and sketch the concrete v1 user flow, edge cases, and why a user would switch from their current workaround.
5. **Define metrics & risks (3-5 min):** State 1 North Star metric, 2-3 funnel metrics (adoption, engagement, retention), 1 guardrail metric (what must not degrade), the biggest failure risk, and the fastest way to test the hypothesis first.

**Worked outline A - "How would you design an alarm clock for the blind?"**
- *Clarify:* Hardware, mobile app, or hybrid? Assume a dedicated bedside + wearable consumer product, starting with totally blind adults living independently (highest pain severity; solutions also help low-vision and sighted light sleepers). Goal: daily reliability + independence (retention/trust).
- *User journey & pains:* (1) Setting/verifying the right time and AM/PM without visual confirmation; (2) Waking reliably without startling housemates or missing audio in noisy environments; (3) Finding snooze vs. dismiss while half-asleep without knocking the device over; (4) Battery/power-outage anxiety (a dead clock means a missed shift or flight).
- *Solutions:* (a) **Tactile Rotary + Voice-Back Bedside Hub + Haptic Wristband** (turn physical notched ring for hours/minutes with click detents; press once to hear spoken confirmation + feel wrist pulse); (b) Smart-speaker voice-only alarm (fast, but risky if Wi-Fi drops or room is noisy); (c) Braille display mat by the bed (high learning curve, not all blind adults read Braille).
- *Prioritise MVP:* Pick **(a) Tactile Hub + Haptic Wristband** - works offline, zero Braille requirement, distinct physical shapes for Snooze (concave dome) vs. Off (two-finger side squeeze), automatic battery-level voice warning at bedtime.
- *Metrics:* North Star = % of scheduled alarms that successfully wake the user on time; supporting = first-try setup success rate, 30-day active retention; guardrail = accidental-dismiss rate and false/missed alarm rate (<0.1%).

**Worked outline B - "What is your favourite product and how would you improve it?"**
- *Structure:* Name the product -> state the job-to-be-done it solves -> explain *why* it wins against alternatives (3 specific UX/product choices) -> state its current business/user goal -> segment users and pick an underserved high-value segment -> identify their #1 friction -> propose 3 improvements -> prioritise 1 with RICE/impact-vs-effort -> define success and counter-metrics.

**Common pitfalls:** Jumping straight to features; listing personas without picking one; picking demographic buckets instead of behavioural segments; proposing "a cool app" that doesn't solve the stated pain; forgetting guardrails and trade-offs.

---
## 2. Product Strategy (Market Entry, Monetisation, Competitive Response & GTM)
**What it tests:** Long-term vision, market and profit-pool analysis, competitive moats, business model fluency, and GTM execution.
**Common prompts:** "Should [Company X] enter the [Market Y] space?" / "How would you monetise WhatsApp?" / "Competitor Z just launched a free tier - how do you respond?"

**Framework (5 steps)**
1. **Company mission, assets & strategic objective:** Why does this company exist, what are its unfair advantages (distribution, brand trust, proprietary data, balance sheet, ecosystem lock-in), and what is the objective now (new revenue stream, retention moat, TAM expansion)?
2. **Market & customer analysis:** Size/growth direction, customer segments, core unmet needs, unit economics, and regulatory or operational barriers.
3. **Competition & "right to win":** Incumbents, substitutes, switching costs, and whether our assets actually solve the hardest bottleneck in Market Y.
4. **Strategic options & trade-offs:** Lay out 3 clear options (e.g. Organic Build vs. Partner/Integrate vs. Acquire vs. Do Not Enter; or 3 monetisation models). Evaluate against revenue potential, strategic fit, time-to-market, and cannibalisation/brand risk. **Make a decisive recommendation.**
5. **Rollout / GTM & kill criteria:** Phased plan (Phase 1 pilot segment/geo -> Phase 2 scale -> Phase 3 ecosystem), pricing/packaging, leading KPIs, top risks, and the explicit threshold that would make you pivot or stop.

**Worked outline A - "Should Company X enter Market Y?" (e.g., "Should Netflix enter cloud/casual gaming?")**
- *Objective:* Reduce subscription churn between tentpole show releases and increase household time-spent without diluting core video margin.
- *Market & competition:* Mobile/casual gaming is huge (~hundreds of billions globally [verify]), fragmented, plagued by ad/IAP fatigue; console/PC AAA has high capex and incumbent moats (Steam, PlayStation, Xbox).
- *Right to win:* Netflix has 200M+ paying households [verify], top IP (Squid Game, Stranger Things), and billing relationships, but low gaming distribution habit on TV.
- *Options:* (1) AAA cloud streaming on TV (high capex, controller friction); (2) Ad-free mobile casual/narrative games bundled in subscription using Netflix IP (low capex, leverages IP, fights churn); (3) Lizenz IP only.
- *Recommendation:* Option 2 first (bundled mobile + party games using phone-as-controller on TV), partnering/acquiring indie studios; measure 30-day retention lift of game-playing subscribers vs. matched control cohort; kill criterion = if cost per retained subscriber exceeds content alternative after 12 months.

**Worked outline B - "How would you monetise WhatsApp?"**
- *Core constraint:* WhatsApp's moat is ubiquity, speed, privacy (E2EE), and trust. Banner ads in personal chats risk user backlash and churn to Signal/Telegram.
- *Who pays x How:* (1) **B2C Consumer:** freemium storage/stickers/premium themes (low ARPU, caps network effect if core features are gated); (2) **B2B Business Messaging & Click-to-WhatsApp Ads:** charge businesses per initiated conversation/support/commerce thread + payment/catalog take-rate (aligns with user desire to message merchants instead of calling); (3) **P2P/Merchant Payments & Mini-apps:** low-margin transaction rail that drives business messaging retention.
- *Recommendation:* Monetise the **Business-to-Consumer surface (Option 2)** via paid business messaging APIs, verified storefront catalogs, and appointment/order flows, while keeping P2P chat 100% free and ad-free. Guardrail: user block/spam-report rate on business messages and daily P2P messaging retention.

---
## 3. Analytical & Metrics (KPIs, Root-Cause Investigation & A/B Testing)
**What it tests:** Metric architecture, causal reasoning, structured debugging, and statistical/experimentation judgement [2].

### 3A. Defining product success metrics
**Framework:** Product mission -> User value + Business value -> **1 North Star Metric** (captures repeated value delivery for both sides) -> **Funnel / AARRR breakdown** (Acquisition, Activation, Engagement/Retention, Referral, Revenue) -> **1-2 Guardrail / Counter-metrics** (quality, latency, cannibalisation, churn) -> Cohort/segment cuts.

**Worked outline - "How would you measure the success of Instagram Reels?"**
- *Goal:* Capture short-form entertainment time and creator supply within Instagram without cannibalising overall app retention or ad revenue.
- *North Star:* **Daily Reels Engaged Watch Time per DAU** (or Reels sessions >= X mins with completion/interaction, balancing passive scroll with real value).
- *Funnel breakdown ( two-sided - Viewers & Creators):*
  - *Supply (Creators):* % active creators posting >=1 Reel/week, creation completion rate, average views per new creator.
  - *Demand (Viewers):* Discovery (% DAU viewing >=1 Reel), Engagement (completion rate, shares per 1k views via DM, saves), Retention (D7/D30 Reels viewer retention).
  - *Monetisation:* Reels ad load, RPM (revenue per 1k impressions) vs. Feed/Stories.
- *Guardrails:* Total Instagram app time spent (ensure Reels adds net time rather than 100% cannibalising Feed/Stories), DM share graph health, ad skip/hide rate, app crash/video start latency.

### 3B. Investigating a metric drop (Root-Cause Analysis)
**Worked outline - "Daily Active Users (DAUs) dropped by 5% yesterday. How would you investigate?"**
1. **Clarify & verify the signal:** How is DAU defined (logged-in open vs. core action)? Was it a sudden 1-day cliff (-5% vs. same day last week, or vs. yesterday)? Is the telemetry/logging pipeline intact (delayed ETL job, tracking SDK change, bot-filtering rule update)?
2. **Isolate via segmentation (the diagnostic tree):**
   - *Geography / Region:* Concentrated in one country (holiday, telecom block, local outage, regulatory ban) or global?
   - *Platform / Client version:* iOS vs. Android vs. Web? Specific app version just rolled out?
   - *User cohort / Acquisition channel:* New users (paid marketing paused, App Store ranking drop, broken signup/OTP flow) vs. returning core users (push notification failure, auth token expiry)?
   - *Funnel step:* App open -> login -> home feed load -> core action.
3. **Compare Internal vs. External causes:**
   - *Internal:* Recent app release, feature flag / A/B test ramp, backend latency/5xx spike, push/email service outage, policy/pricing change.
   - *External:* Public holiday/weather/major event, OS privacy update, competitor launch, PR incident, ISP/cloud outage.
4. **Formulate ranked hypotheses, validate, and act:** State the top 2 most likely causes based on the cuts, how to confirm with engineering/data in 30 minutes, immediate mitigation (rollback, hotfix, status update), and a post-mortem alert to catch it earlier next time.

### 3C. Designing & interpreting A/B tests [2]
- **Design:** Hypothesis (`If we [change] for [segment], then [primary metric] will move by [MDE] because [behavioural mechanism]`) -> Primary metric + Guardrails -> Randomisation unit (user, session, geo/cluster if two-sided marketplace/social network interference exists) -> Sample size, statistical power (80%), significance (alpha 5%), runtime (at least 1-2 full weekly cycles; never stop early on a noisy spike).
- **Trade-off call ("Metric X is +3%, Guardrail Y is -1% - ship?"):** Check magnitude vs. strategic priority, segment effects (is the drop isolated to one fixable bug/device?), short-term novelty/primacy vs. long-term cohort value, and whether a tweak preserves the gain without the cost.

---
## 4. Execution & Prioritisation (Roadmaps, Trade-offs & Stakeholder Pushback)
**What it tests:** Decision-making under scarcity, roadmap rigor, crisis triage, and constructive influence.

**Worked outline A - "You have 5 major features and engineering capacity for only 2. How do you decide?"**
1. **Anchor on the quarterly/annual North Star & non-negotiables:** First check if any of the 5 is a hard regulatory, security, or critical reliability requirement (if so, it's a constraint, not a nice-to-have).
2. **Align on a transparent scoring framework (RICE + Strategic Fit):**
   - **R**each (how many users/customers affected this quarter)
   - **I**mpact (expected lift on the target KPI: 3x=massive, 2x=high, 1x=medium, 0.5x=low)
   - **C**onfidence (backed by data/experiments vs. gut feel)
   - **E**ffort (engineering person-weeks, including QA and dependencies)
   - Plus **sequencing/dependency check**: does Feature A unlock Feature B?
3. **Challenge the "fixed scope" assumption:** Ask engineering if reducing two features to 20%-effort MVPs lets us validate 3 bets instead of building 2 bloated ones.
4. **Communicate the cut list:** Share the scored trade-off table with stakeholders; show what condition or metric would pull #3 into the next cycle.

**Worked outline B - "How do you handle a stubborn stakeholder or an engineering pushback?" (Hypothetical execution approach)**
*(Note: If asked "Tell me about a time you handled pushback", use a real STAR story via `interview-prep`. If asked "How do you handle...", use this 5-step operational playbook:)*
1. **Diagnose the root concern in 1:1:** Separate position from interest. Is an engineer pushing back because of unstated tech debt, on-call burnout, vague specs, or low conviction in user value? Is a VP pushing a pet feature because of a promised enterprise deal or quarterly revenue pressure?
2. **Anchor on shared goals and constraints:** Agree on the metric and customer problem before debating the solution.
3. **Turn opinions into testable hypotheses:** Propose the smallest possible experiment (painted-door test, 5-customer prototype, 10% canary, or 1-week spike) so evidence decides rather than hierarchy.
4. **Offer explicit trade-off options:** Never just say "no". Say: *"We can ship X by Friday if we drop Y, or keep both and move the date by 2 weeks - which trade-off works better for our Q3 goal?"*
5. **Disagree and commit, then review:** Document the decision, owner, and review date.

---
## 5. Technical Acumen (Explaining Concepts & System Design for PMs)
**What it tests:** Ability to reason about architecture, latency, scale, reliability, APIs, and product-engineering trade-offs without pretending to write production code.

**Worked outline A - "Explain how a URL loads in a browser to a non-technical person."**
- *Analogy + 4 plain steps:* Compare it to ordering a custom book from a specialist shop across town:
  1. **Look up the address (DNS):** Your browser doesn't know where `example.com` lives, so it checks the internet's phonebook (DNS) to turn the name into a numeric street address (IP address).
  2. **Open a secure phone line (TCP + TLS/HTTPS):** Your device rings that address and agrees on a secret code (encryption handshake) so nobody in the coffee shop can eavesdrop.
  3. **Place the order and get the kit (HTTP Request & Response):** The browser asks for the page; the company's server (or a nearby local warehouse called a CDN) sends back a blueprint (HTML), styling instructions (CSS), and interactive scripts (JavaScript).
  4. **Assemble on screen (Rendering):** Your browser paints the layout, fetches images, and makes buttons clickable in a fraction of a second.
- *PM connection:* Explain why a PM cares (every step adds milliseconds of wait time that can hurt conversion or SEO).

**Worked outline B - "How would you design the system architecture for a real-time messaging app?"**
1. **Requirements:** Functional (1:1 and group chat, delivery/read receipts, offline sync, media attachments); Non-functional (sub-200ms latency, high availability, ordering guarantees, E2EE/privacy, 50M DAU).
2. **Core components:**
   - **Client + Persistent Connection:** WebSockets (or MQTT) for bidirectional low-latency push while online, falling back to APNs/FCM push notifications when backgrounded.
   - **Connection Gateway / Session Service:** Tracks which user is connected to which gateway server (backed by an in-memory store like Redis).
   - **Message Service + Message Queue (Kafka/pub-sub):** Decouples ingestion from fan-out (critical when a group has 500 members).
   - **Storage:** Wide-column/NoSQL store (e.g., Cassandra/DynamoDB) partitioned by `conversation_id` + `timestamp` for fast chronological reads and high write throughput; blob storage (S3) + CDN for images/video.
3. **PM trade-offs to highlight:** Max group size cap (fan-out cost vs. user need), message history retention vs. storage cost, E2EE vs. server-side search/multi-device cloud backup.

---
## 6. Estimation (Fermi / Back-of-the-Envelope Math)
**What it tests:** Structured decomposition of ambiguous problems, realistic assumptions, clean mental arithmetic, and sanity checking.

**Worked outline A - "How many Uber drivers are active in Singapore right now?"**
1. **Clarify:** "Active right now" = logged into the driver app and on a trip or waiting for a ping during a typical weekday daytime hour (say 2 PM; peak vs. off-peak noted). *(Note: in reality Uber exited Southeast Asia via the Grab deal in 2018; flag that fact briefly and treat "Uber" as "major ride-hailing platform in Singapore" or solve for all ride-hailing x platform share.)*
2. **Demand-side equation:** `Active drivers now = (Rides in this hour) / (Rides completed per active driver per hour)`.
3. **Assumptions (labelled illustrative):**
   - Singapore population ~ **6M** [verify]. Exclude young children/elderly/visitors net -> ~**5M** transport-using residents.
   - Daily ride-hailing users: assume **15%** take a ride-hailing trip on an average day = **750k** riders; at ~1.3 riders/car and some taking 2 trips/day -> roughly **800k - 1M** ride-hailing trips/day across all apps.
   - Assume the target app has **50%** market share -> **450k** trips/day.
   - Hourly share: a typical daytime hour carries ~**6%** of daily volume (peak hour ~10%) -> **27k** trips/hour off-peak (**45k** peak).
   - Driver throughput: average trip is 20 min drive + 5 min pickup + 5 min idle = 30 min -> **2 trips/hour** per online driver.
4. **Compute:** `27,000 / 2` = **~13,500 drivers active off-peak** (and `45,000 / 2` = **~22,500 at peak**). If solving for a 30%-share player, scale by 0.6 (~8k off-peak, ~13.5k peak).
5. **Supply-side sanity check:** Total licensed private-hire + taxi fleet in SG is roughly 70k-90k vehicles [verify]; if half are on this platform and 30-50% are online at once, that lands in the **10k-20k** range. Consistent.

**Worked outline B - "Estimate the daily revenue of Google Play."**
1. **Clarify:** Gross consumer spend vs. Google's net revenue (after the ~15-30% platform take rate)? Solve for **Gross Merchandise Value (GMV)** and then apply the blended take rate (~20%). Exclude China (Android devices there use third-party stores).
2. **Top-down decomposition:**
   - Global population ~8B -> Smartphone users ~4.5B -> Android share ~70% (~3.1B) -> Ex-China Android with Google Play ~**2.2B active devices** (illustrative assumption [verify]).
   - Split into 3 spending tiers:
     - **Non-payers (70% = 1.54B):** $0 direct Play Store billing.
     - **Casual payers / subscribers (25% = 550M):** spend ~$5/month ($60/yr) on subscriptions/small IAP = **$33B/year**.
     - **Heavy mobile gamers / power users (5% = 110M):** spend ~$35/month ($420/yr) = **$46B/year**.
   - **Total annual gross billing:** ~$33B + $46B = **~$79B/year** (round to **~$75B-$80B/year**).
   - **Daily gross billing:** `$75B / 365` ≈ **$205M/day**.
   - **Google Play net daily revenue (at ~20% blended take rate):** `~$205M * 0.20` ≈ **~$40M/day** (illustrative estimate [verify]).
3. **Sanity check:** Compare against ~2.2B users -> ~$35 gross spend per Android user per year (~$0.10/day), which is plausible across developed + emerging markets.

---
## 7. Growth, Funnel & Pricing/Packaging (`growth`)
**What it tests:** Funnel diagnostics, growth loops (viral, content, paid, sales), retention cohort analysis, and pricing/monetisation mechanics.
**Framework:**
1. **Map the growth model:** Is growth driven by a viral loop (invite/share), user-generated content/SEO loop, paid acquisition loop (LTV > 3x CAC), or sales-led motion?
2. **Find the leaky bucket:** Break down `Impression -> Visit -> Signup -> Setup -> Habit Moment (Aha!) -> D7/D30 Retention -> Paid Conversion -> Expansion/Referral`. Fix **activation and retention** before pouring money into top-of-funnel acquisition.
3. **Cohort analysis:** Check whether the retention curve flattens (product-market fit for a core segment) or decays to zero.
4. **Pricing & packaging:** Match the **value metric** (per seat, per active user, per usage/API call, per transaction, outcome-based) to how customers perceive value. Design Free / Pro / Enterprise tiers so the paywall triggers *after* the user experiences the core "Aha!" moment.

---
## 8. Product Critique, App Teardown & Take-Home PRD (`critique`)
**What it tests:** Product taste, ability to reverse-engineer incentives and trade-offs in live products, and crisp written/visual communication.

### Live app teardown structure (10-15 min)
1. **Job-to-be-done & target user:** What core anxiety or habit does this app solve, and for whom?
2. **Business model & incentive alignment:** How does it make money, and where does monetisation reinforce or clash with UX?
3. **3 things it gets right:** Specific onboarding, information hierarchy, default, or habit-loop choices.
4. **2 structural weaknesses:** Where a specific user segment drops off or feels friction.
5. **1 prioritised bet + metric:** What you would ship next quarter and how you would test it.

### Take-home PRD / Written case structure (1-2 pages or 6-8 slides)
1. **Executive Summary / TL;DR:** Problem, target persona, recommended solution, expected impact (3 bullets).
2. **Problem Statement & Evidence:** User pain + market/funnel data + why now.
3. **Goals, Non-Goals & Success Metrics:** North Star, primary KPI, guardrails, and explicit out-of-scope items.
4. **User Personas & Use Cases:** Primary user journey and edge cases.
5. **Options Considered & Why We Chose X:** Trade-off matrix showing alternatives rejected.
6. **Product Requirements / MVP Scope (P0 vs. P1/P2):** User stories, wireframe/flow description, technical/AI constraints.
7. **Rollout, Experiment Plan & Risks:** Phased launch, A/B test setup, pre-mortem risks and mitigations.

---
## 9. Time-box guide (typical 30-45 min PM round)
| Category | Clarify & Goal | Core Analysis & Options | Prioritise & Deepen | Metrics, Risks & Summary |
|---|---|---|---|---|
| Product Sense | 3-4 min | 10-12 min (users + ideas) | 8-10 min (MVP + flow) | 5 min |
| Strategy | 3-4 min | 12-15 min (market + moats + options) | 6-8 min (choice + GTM) | 4-5 min |
| Analytical & Metrics | 2-3 min | 12-15 min (funnel / root-cause tree) | 6-8 min (test / decision) | 3-4 min |
| Execution | 2-3 min | 10-12 min (criteria + scoring) | 8-10 min (trade-offs + comms) | 3-4 min |
| Technical | 3-4 min | 12-15 min (architecture + flow) | 6-8 min (scale/trade-offs) | 3-4 min |
| Estimation | 1-2 min | 3-4 min (equation + assumptions) | 4-5 min (math) | 2-3 min (sanity check) |
| Growth / Critique | 2-3 min | 10-12 min (loop / teardown) | 8-10 min (bet / paywall) | 3-4 min |
