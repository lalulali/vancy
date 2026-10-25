# Job Brief Template

The brief is the handoff document other skills use. Save it as `Job_Brief_<Company>_<Role>.md` in `artifacts/output/<Company>_<Role>/` (the ad text it came from is read from `artifacts/input/`, or saved as `artifacts/output/<Company>_<Role>/job-ad.txt`; `artifacts/` is git-ignored personal data). It is an advisory working document: citations (`[^n]`) are allowed in it, and it needs no `--final` render. Keep it to one page where possible.

```markdown
# Job Brief: [Role] at [Company] ([Location / work mode])

**Source:** [link or "pasted"] · **Deadline:** [date or none] · **Brief date:** [YYYY-MM-DD]

## 1. Why the role exists
They are hiring because [problem], and success looks like [outcome].

## 2. Snapshot
| | |
|---|---|
| Level | [seniority signals; reporting line; team size] |
| Pay | [range / not stated] |
| Work mode | [remote / hybrid + days / on-site] |
| Application asks | [CV, cover letter, portfolio, salary expectation, knockout questions] |

## 3. Hard filters
- [licence / work authorisation / location / language] - Met / Not met / Unknown

## 4. Requirements ranked
| # | Requirement | Signal | Candidate evidence | Match |
|---|---|---|---|---|
| 1 | | hard / top / repeated | | Strong / Partial / Gap |

## 5. Keyword map (use only if TRUE of the candidate)
| Ad wording | Where to use it | True? |
|---|---|---|

## 6. Gaps and how to handle them
- [gap] -> [adjacent evidence] -> [where to address: summary / cover letter / interview]

## 7. Flags to verify
- [flag: pay, ghost-job, scam or wording signal; see `ad-anatomy.md` §7] -> [question to ask]

## 8. Recommendation
**[Apply / Apply with a plan / Reconsider]** - [two sentences of reasoning].

## 9. Handoff
- cv-builder: headline `[mirror of title if true]`; top 3 proof points: ...
- cover-letter-builder: hook = [company fact]; value paragraph = [problem + first contribution].
- interview-prep (and pm-interview-prep for PM roles): likely focus areas: ...
- salary-negotiation: pay signal: ...

[^n]: Source title, publisher, year, URL
```

Rules:
- Every "Candidate evidence" cell comes from the candidate's real CV or words. Write `[fact?]` and ask when unknown.
- Keep the quoted ad text short. Paraphrase.
- Section 8 must name the hard filters that decide the answer.
