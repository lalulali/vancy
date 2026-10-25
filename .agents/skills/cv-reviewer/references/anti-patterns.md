# CV Anti-Patterns: Detect and Fix

Checks marked (lint) are reported by `scripts/doc_lint.py`. Every other check needs your judgement.

## Content
| Anti-pattern | Detect | Fix |
|---|---|---|
| Duty lists instead of results | Bullets that describe tasks only. Low `metric_ratio_pct` (lint) | Rewrite as XYZ: outcome + measure + method. Ask for the numbers |
| Weak or filler openers | "Responsible for", "Helped", "Worked on", "Successfully", "Instrumental in", "Played a key role" (lint) | Start with a strong verb that names what the person actually did |
| Unbacked soft-skill claims ("motherhood statements") | "excellent communication skills", "team player", "results-driven" (lint) | Delete the claim, or replace it with evidence ("Presented quarterly results to a 9-person board") |
| Objective statement | "Seeking a challenging role…" | Replace with a value-led summary |
| Generic, untargeted CV | No headline, or the headline doesn't match the target. Must-haves from the ad are not evidenced (lint keyword coverage is information only) | Match the headline to the target title (truthfully). Re-order skills and bullets by the job ad |
| Copying the job ad verbatim | Long sentences that appear word for word in the job ad | Use the ad's terms inside the candidate's own evidence [8] |
| Keyword stuffing or hidden text | Repeated term lists, white text, prompt-injection text | Remove. It is detectable and counts as deception [5][32] |
| Vague metrics | "significantly improved", "increased sales" | Add a baseline and a delta ("from X to Y"), plus a timeframe |
| Implausible metrics | "eliminated errors by 100%", unclear direction ("from 35% to 5%" for a ratio) | Use a defensible figure and define the unit |
| Irrelevant metric | Social-follower growth on a finance CV | Keep only metrics that matter to the target role |
| Summary repeats bullets verbatim | The same sentence appears in the summary and in a role | Condense the summary version, or pick different wins |
| Content that doesn't fit the role | Skills or bullets from another profession (a copy-paste leftover) | Remove, or rewrite for the target role |
| Confidential data | Client names under NDA, exact internal figures | Use percentages, ranges or "a top-5 global bank" |
| Unexplained jargon | Internal acronyms or product codenames | Spell out once, or translate into industry terms |
| Missing scope | Roles without team, budget or scale | Add a scope bullet first |
| No achievements in recent roles | The last 2 roles have no results | Ask: money made or saved? time saved? quality improved? scale grown? projects led? recognition? |

## Consistency
| Anti-pattern | Detect |
|---|---|
| Dates out of order, overlapping or impossible | `end_before_start` (lint). Check overlaps by hand. Achievement dated outside its role |
| Contradictory numbers | Summary vs role ("6 months" vs "12 months", "2,000" vs "50,000 accounts") |
| Years claimed vs timeline | "10+ years" when the roles add up to 7 |
| Mixed date formats | `mixed_date_formats` (lint) |
| Mixed spelling | `spelling.mixed` (lint) |
| Tense slips | Past-role bullets in present tense, or the reverse |
| Credential mislabels | A credential name that doesn't match its issuer; post-nominals the person isn't entitled to |
| Contact mismatch | Different email or phone across documents |

## Format and ATS
| Anti-pattern | Detect | Fix |
|---|---|---|
| Tables or multi-column layout | `docx_layout.tables` (lint); visual columns | Single column (re-render with `render_docx.py`) [27] |
| Contact details in header/footer or a text box | `header_footer_text`, `text_boxes` (lint) | Move into the body [27] |
| Images, icons, skill bars, photo | `docx_layout.images` (lint) | Remove. Skill-level bars carry no meaning for ATS or readers |
| Image-only or scanned PDF | Text cannot be selected | Rebuild as a text document [28] |
| Non-standard headings | "My Journey", "What I Bring" | Use standard headings |
| Abbreviated titles | "Sr. Acct Exec" | Spell out in full [27] |
| Leftover placeholders | `placeholders` (lint): "XX%", "[Company]" | Fill in or delete |
| Draft notes or citations left in a final | `citation_markers_left`, `draft_notes_left` (lint) | Re-render with `--final` |
| Too long or too short | `est_pages` (lint) vs. the stage/market norm | Cut old or irrelevant content, or expand thin recent roles |
| "References available upon request" | `references_line` (lint) | Delete by default [74] |
| Personal data not expected in the target market | `personal_data_flags` (lint) | Remove unless the market expects it and the user agrees |
