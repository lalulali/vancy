# Building a Story Bank

Citation numbers refer to `evidence-interviewing.md`.

## Contents
1. Why a story bank
2. Competencies to cover
3. Mining the candidate's experience
4. Writing a story
5. Mapping stories to questions
6. Weakness, failure and sensitive stories
7. Delivery rules
8. Practice routine

## 1. Why a story bank
Structured interviews ask every candidate the same questions and score answers against set criteria, and they are the strongest single predictor of job performance in the research [1]. Strong answers draw on **real, specific, well-practised stories**. A bank of 6-8 flexible stories covers almost any question; memorising 30 scripts does not.

## 2. Competencies to cover
Tag every story with 2-4 of these. The linter checks coverage:
leadership · conflict · failure · initiative · teamwork · problem-solving · influence · pressure · ambiguity · customer · learning

Add role-specific ones from the job brief (for example: technical depth, data judgement, safety, sales closing, creativity).

## 3. Mining the candidate's experience
Ask in small rounds [11]:
- A project you are proud of: what was the problem, what did you decide?
- A time something went wrong: what did you do next?
- A disagreement with a colleague, manager, client or stakeholder.
- A time you led without authority, or led a team through change.
- A time you had to learn something fast.
- A time you went beyond your job scope.
- A time you worked under a hard deadline or with limited information.
- Examples from outside work (study, volunteering, community, clubs) if the candidate has little experience.
Pull the numbers: scale, time, money, quality, headcount.

## 4. Writing a story
Format (the linter reads it). To render the bank as Word, start the file with this front matter (`doc: interview` sets the Word title; `template`, `page` and `lang` are optional):
```
---
doc: interview
template: minimal
page: a4
lang: en-GB
---

# Your Name - Story Bank

### Short title
**Competencies:** tag, tag
**S:** Situation - 1-2 sentences of context.
**T:** Task - what you were accountable for.
**A:** Action - what YOU did, step by step; decisions and reasons.
**R:** Result - outcome with a number or observable change, plus what you learned.
```
Read the candidate's material from `artifacts/input/` and save the bank to `artifacts/output/<Company>_<Role>/` (it is personal data in a git-ignored folder).

Rules [5][7][9]:
- Keep setup (S+T) near a quarter to a third of the words. Spend most words on Action.
- Use "I" for your own decisions and actions ("I decided to stage the release"), name other people's roles and contributions ("my engineering lead flagged the risk"), and use "we" only for the team result. The "I" advice reflects US-style interviews [9]. In team-oriented markets (for example many East Asian and Nordic workplaces; a convention, unsourced) a modest "we" is normal, so credit the team and still say what you personally did ("I drafted the plan; we shipped it in March"). Ask the candidate which style the employer's market expects.
- Give the result a number, a before/after, or a clear observable change. Estimates are fine if you say they are estimates.
- Finish with one line on what you learned or changed.
- A commonly advised length is about two minutes per story at most [10]. Aim for 1-2 minutes spoken, roughly 120-300 words at a normal speaking pace (the word range is our estimate, not from the source).
- Truth only. Use only things the candidate did. Never invent, inflate, or borrow someone else's story.

## 5. Mapping stories to questions
| Question theme | Typical prompts | Best-fit story tags |
|---|---|---|
| Leadership | "Tell me about a time you led a team" | leadership, ambiguity |
| Conflict | "A time you disagreed with a colleague" | conflict, influence |
| Failure | "A mistake you made" | failure, learning |
| Initiative | "Went beyond your job" | initiative, customer |
| Teamwork | "Worked with a difficult team" | teamwork, conflict |
| Problem-solving | "A hard problem you solved" | problem-solving |
| Pressure | "Tight deadline" | pressure, ambiguity |
| Influence | "Persuaded someone" | influence, customer |
| Learning | "Learned something quickly" | learning, ambiguity |
One story can serve several themes by changing the emphasis. Do not reuse the exact same story twice in one interview unless unavoidable.

## 6. Weakness, failure and sensitive stories
- **Failure:** choose a real, modest failure with a clear lesson and a changed behaviour. Do not pick a disguised strength. Do not blame others.
- **Weakness:** name a real weakness that is not central to the role, show the step you are taking, and the effect so far.
- **Layoff, gap, firing:** state it briefly and factually, then pivot to what you did and what you are looking for. Never badmouth a former employer.
- **Confidential material:** keep employer secrets out; use ranges or percentages.

## 7. Delivery rules
- Answer the question asked first, then add the story.
- Pause before answering; ask a clarifying question if the prompt is vague.
- Stay specific: names of tools, numbers, and decisions beat adjectives.
- Check in at the end: "Would you like more detail on any part?"
- Do not read from a script.

## 8. Practice routine
1. Write and lint the bank (`scripts/story_lint.py`).
2. Say each story aloud and time it. Cut anything that does not carry the point.
3. Run a mock interview with questions from `question-bank.md` and the job brief; answer out loud.
4. Record one answer and listen for filler words, "we", and missing numbers.
5. Repeat the weakest three stories.
