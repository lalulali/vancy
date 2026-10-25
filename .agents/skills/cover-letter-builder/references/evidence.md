# Evidence Base and Citations

Use this file to justify recommendations in **drafts** with citations. Cite **bibliography numbers** (not the finding numbers in sections 1–10) as `[^n]` with a matching definition line `[^n]: Title, Publisher, Year, URL` copied from the Bibliography at the end. **Never put citations in final documents.**

## Rules
- Cite only sources listed here. Never invent sources, numbers or URLs.
- Prefer High-confidence sources. Sources tagged `[snippet]` were checked only from search results, so quote their direction, not their exact numbers.
- State statistics with their caveats (year, country, sample size). Most hiring surveys are US-only and run by vendors.
- Do not repeat myths. "75% of resumes are rejected by ATS" is unsupported (C7). "6 seconds" describes only the first skim (C2).
- Evidence supports a writing choice. It never supports a claim about the candidate.

## Contents
1. Claims verification · 2. How screening works · 3. ATS parsing · 4. Writing strong content · 5. Length and structure · 6. Cover letters · 7. AI-generated applications · 8. Bias and accessibility · 9. Regional conventions · 10. Honesty · Bibliography

---

## 1. Claims verification (popular hiring statistics)

| # | Popular claim | Best original source found | Status | Note |
|---|---|---|---|---|
| C1 | ~250 resumes per posting, 4–6 interviewed | Glassdoor HR stats blog, Jan 2015 [1] | PARTIALLY VERIFIED | Glassdoor is the origin, but it gives no method or dataset. Glassdoor and later Jobscan repeat it, and Jobscan attributes it to *The Times* [2]. Current data varies by industry: CareerPlug reports ~180 applicants per hire and ~3% of applicants interviewed (2025) [3][snippet]. Present it as "hundreds, varies widely", not as a fact. |
| C2 | Recruiters scan resumes for 6–7 seconds | Ladders eye-tracking study: 6 s in 2012, 7.4 s in 2018 [4][5] | PARTIALLY VERIFIED | Real, but vendor-run with a small sample (~30 recruiters reported [6][snippet]). It measures only the first fit/no-fit glance. In ResumeGo's timed simulation, reviewers spent 2–4 minutes on a resume [7]. Say "the first skim is seconds long", not "your resume gets 6 seconds". |
| C3 | 58% of hiring managers dismiss resumes with typos | CareerBuilder/Harris survey, 2013 (n=2,076 US hiring managers and HR) [8] | VERIFIED (dated, US-only) | 58% named typos as a mistake that may lead to automatic dismissal. Do not confuse it with CareerBuilder's separate 2014 figure that 58% had caught a *lie* on a resume [9][snippet]. |
| C4 | 36% rejected for being too generic | Same CareerBuilder 2013 survey [8] | VERIFIED (dated, US-only) | 36% named resumes that were generic or not personalised for the role. Resume Now's 2025 report independently found 36% list generic content as a top rejection reason [10][snippet]. |
| C5 | Cover letter of 250–400 words | No empirical study found | PARTIALLY VERIFIED (convention) | Vendors agree on it (Resume Genius, Novorésumé, resume.io) [11][snippet], and it fits university and government advice: one page, 3–5 paragraphs [12][13][14]. One vendor blog claims a ResumeGo study showed 250–400 words won 53% more callbacks [15][snippet]. **This misattributes the data:** ResumeGo's 53% compares *tailored letters vs no letter* and did not test length [16]. |
| C6 | Customise 30–50% of each letter | No original source found | UNVERIFIED (heuristic) | Only vendor blogs say this (one says 30–40%) [17][snippet]. Authoritative sources say to write or tailor a letter for *every* job, with no percentage [13]. Evidence supports tailoring in general [16] but not a specific share. |
| C7 | (Common myth) "75% of resumes are rejected by ATS" | Traced to a 2012 sales pitch from Preptel, a vendor that closed in 2013 [18] | MYTH | No method was ever published. In a vendor-run (Enhancv) set of interviews with 25 US recruiters, 23 said their ATS does not auto-reject on format or content. Knockout questions were the one automatic filter recruiters described (84% rely on them; all where configured). Content-based auto-reject was configured by 2 of 25 [19]. |

---

## 2. How screening actually works: volume, skim time, ATS behaviour

1. Volume is now very high. LinkedIn applications rose ~45% year on year to roughly 9,500–11,000 per minute in 2025 [20][snippet][21]. — Medium
2. LinkedIn (2026) says global hiring is down ~30% and applications per applicant are up ~30% compared with before the pandemic [22][snippet]. — Medium
3. The first screen is a fast skim. Recruiters looked mainly at current and previous titles, employers, dates, then education [4][23][snippet]. — Medium
4. Resumes that held attention had simple layouts, clear section headers, bold job titles with bulleted accomplishments, and a summary at the top. The worst had clutter, multiple columns, long sentences, little white space, and keyword stuffing [5]. — Medium
5. Stanford advises that recruiters often focus on the top third of the first page, so lead with the strongest relevant content [24]. — High
6. Jobscan detected an ATS on 97.4% of Fortune 500 career sites in 2026, and 97–99% in every year it has checked since 2018 [2]. — High (descriptive)
7. Workday is used by over 40% of the Fortune 500. Across 13,000+ smaller companies, Greenhouse (19%), Workday (17.5%), Lever (15.6%) and iCIMS (14.4%) lead [2]. — Medium
8. Recruiters mainly use an ATS to *search and rank*: 76.4% search by skills from the job description, then by education, title, licences and years of experience [2]. — Medium
9. The HBS/Accenture "Hidden Workers" study (2021) found over 90% of employers use systems to filter or rank middle- and high-skill candidates first, so rigid criteria can screen out qualified people [25][snippet][2]. — High
10. Fully automatic content rejection is rare (2 of 25 recruiters had it switched on). Knockout questions (work authorisation, licences, location, education) were the one automatic filter described: 84% of recruiters rely on them, and all used them where configured [19]. — Medium (small US sample)
11. A low match score usually pushes a candidate down the review queue rather than rejecting them. In high-volume roles that can still mean nobody reads the application [19]. — Medium

**Skill implication:** Do not frighten users with "the ATS will reject you". The real risks are (a) failing knockout questions, (b) parsing failures that hide content, and (c) being ranked low on skill match.

---

## 3. ATS parsing: facts from vendor documentation

12. Greenhouse accepts doc, docx, pdf, rtf and txt uploads up to 100 MB [26][snippet]. — High
13. Greenhouse cannot parse files over 2.5 MB, which image-heavy resumes can exceed [27]. — High
14. Greenhouse lists these causes of failed or partial parses [27]. — High
    - letters separated by spaces
    - graphics, photos or word art
    - image-only files
    - tables, headers and footers
    - contact details in a header, footer or text box
    - column layouts
    - unclear or inconsistent sections
15. Greenhouse's parser also stumbles on abbreviated titles ("Sr. Account Exec") and on company names without identifiers such as Inc. or Ltd. Spelling titles out in full is safer [27]. — High
16. Greenhouse's parser skips obviously fake placeholder data. Skills should never ship with dummy names like "Company 1" in templates sent to employers [27]. — High
17. Lever cannot parse image files such as JPG or PNG. If you cannot highlight the text in a document, it probably cannot be parsed [28][snippet]. — High
18. Workday imports resumes into structured profile fields. Third-party testers report that columns, tables and text boxes cause swapped or blank fields [29][snippet]. — Low (no official Workday documentation found)
19. Harvard's career office discourages templates, text boxes, colour and shading. It recommends 10–12 pt type and margins of at least 0.75 inch [30]. — High
20. The UK National Careers Service recommends a clear font such as Arial, Times New Roman or Calibri at 11 pt or larger, one consistent style, and headings plus bullets [31]. — High
21. Hidden text and prompt injection are now an integrity issue. In Greenhouse's 2025 survey, 41% of US job seekers admitted hiding prompt injections in applications, and 22% of hiring managers had caught them [32]. — Medium

**Skill implication:** Default to one column and standard headings (Experience, Education, Skills). Keep contact details in the body, use real selectable text, export as DOCX or a text-based PDF, keep the file under 2.5 MB, and write out abbreviations. **Never add hidden or white text.**

---

## 4. Writing strong content: accomplishments, formulas, quantification

22. Laszlo Bock, then Google's SVP of People Operations, proposed the XYZ formula in a 2014 LinkedIn post: "Accomplished [X] as measured by [Y] by doing [Z]". It means starting with an active verb, measuring the result, giving a baseline, and saying how you did it [33][snippet][34][snippet]. — Medium (original LinkedIn post not opened; consistent copies exist)
23. MIT's career office recommends an action verb, then the project, then the result: what you did, why, and what happened [35][snippet]. — High
24. MIT's career office also says each bullet should start with an action verb that points to the skill being shown [36][snippet]. — High
25. Stanford GSB tells alumni to be as quantitative as possible, for example revenue growth, money saved or market share [37][snippet]. — High
26. CareerBuilder's HR VP advised keeping resumes succinct and personalised and always including specific, quantifiable results [8]. — Medium
27. The UK National Careers Service recommends 2–3 lines per role written with the STAR method (Situation, Task, Action, Result) [31]. It promotes STAR for both CVs and interviews [38][snippet]. — High
28. CAR (Challenge or Context, Action, Result) and PAR (Problem, Action, Result) are shorter versions of STAR. They suit one-line resume bullets, while STAR suits longer cover-letter or interview stories [39][snippet][40][snippet]. — Low (practitioner sources; these frameworks have no academic origin)
29. Harvard and Stanford both say to tailor the resume to each role and to use the job description to decide what to stress [30][24]. — High
30. CareerOneStop (US Department of Labor) advises studying job announcements to find important keywords and credentials before writing [41][snippet]. — High
31. The National Careers Service says to tailor a CV by matching it to the advert's essential criteria and highlighting the skills asked for [31]. — High
32. Copying wording from the job posting has its own risk: 32% of hiring managers named it as a mistake that may cause dismissal [8]. Ladders also listed keyword stuffing among the worst-performing traits [5]. — Medium
33. Common rejection triggers in the same survey were missing skills lists (35%), unprofessional email addresses (31%) and missing exact employment dates (27%) [8]. — Medium (dated)
34. Germany's Federal Employment Agency advises 3–5 bullet points per role, month and year dates, no false or unverifiable information, and putting soft skills in the cover letter rather than the CV [42]. — High

**Skill implication:**
- **Builder:** ask for metrics and baselines. If the user cannot quantify, use scope (team size, budget, volume) and never invent numbers.
- **Reviewer:** flag duty-only bullets, missing results, and verbatim copying from the job description.

---

## 5. Length and structure

35. CareerBuilder (2013): 66% of employers said new graduates should use one page, and 77% said experienced workers should use at least two [8]. — Medium (dated)
36. In ResumeGo's simulation (482 hiring professionals), two-page resumes were chosen 2.3 times as often and scored 8.6 vs 7.1. The preference grew with seniority. This was a lab simulation, not real hiring [7]. — Medium
37. Harvard says one page is the norm for bachelor's, master's and MBA candidates. Two pages are acceptable for advanced careers or PhDs [30]. Stanford also advises one page for undergraduate and master's students [24]. — High
38. Oxford's Careers Service recommends one or two full pages, with longer academic CVs. Oxford's own recruitment tips set a two-page limit [43][snippet][44][snippet]. — High
39. Germany's Federal Employment Agency says a CV should not exceed two pages and should be in reverse-chronological order [42]. — High
40. Academic CVs have no page limit. Harvard says graduate-student CVs typically run 2–5 pages [45][snippet]. — High
41. US career sources treat a "resume" as a short, tailored industry document and a "CV" as a full academic, medical or research record [46][snippet]. In the UK and most of Europe, "CV" means the standard job document [47][snippet]. — Medium

---

## 6. Cover letters: structure, relevance and tailoring

42. Harvard's template has three parts: why them (role, source, referral), why you (1–2 paragraphs of evidence for the skills required), and a close with thanks and follow-up [30]. — High
43. The UK National Careers Service describes a short letter of 3–5 paragraphs. It says to always include one with a CV application and to write a new, tailored letter for every job [13]. — High
44. The NCS also advises matching the employer's keywords, backing claims with STAR evidence, using the same font as the CV, and addressing a named person where possible [13]. — High
45. NCS letter conventions: try the company website for a name first; use "Dear Sir or Madam" only if no name can be found. Sign off "Yours sincerely" when the reader is named and "Yours faithfully" when you wrote "Dear Sir or Madam" [13]. — High. (US usage such as "Dear Hiring Manager" and "Sincerely", and "Kind regards" in UK business writing, are common conventions not covered by [13]: treat as unsourced.)
46. Newcastle University says to send a one-page covering letter with the CV [14][snippet]. — High
47. In ResumeGo's field experiment (7,287 applications, 2019–20), tailored letters got 53% more callbacks than no letter. Generic letters helped only slightly [16]. — Medium-High (vendor-run but a real field experiment)
48. In ResumeGo's survey of 236 recruiters, 87% said they read cover letters and 81% valued tailored letters significantly more than generic ones [16]. — Medium
49. Resume Genius surveyed 625 US hiring managers in **2022**. 94% said letters influence interview decisions, 83% said they read most letters, and 45% read the letter before the resume [48]. Later articles often call this 2025 data, but it is from 2022. — Medium
50. Novorésumé surveyed 200+ US recruiters and HR staff in December 2025 and found less reading [49]. — Medium (small vendor sample)
    - 39.1% don't read cover letters, including 51.7% of recruiters.
    - Only 25.7% think a letter can tip a decision.
    - Most who do read the letter read it after the resume.
51. Taken together: letters matter more to hiring managers and HR leads than to front-line recruiters, and only tailored letters carry value [49][16]. — Medium (synthesis)
52. Yale/Freelancer.com research (arXiv, 2025): an AI cover-letter tool made letters more tailored and raised callbacks. The link between tailoring and callbacks then fell by about 51% (offers by about 79%), so employers shifted to other signals such as past reviews [50]. The callback gain is significant only at the 10% level, not 5%; the fall in tailoring's predictive power is reported with robustness checks [50]. — Medium (working paper on a freelance marketplace)
53. In the same study, workers who spent more time editing the AI draft had higher hiring success [50]. — Medium

**Skill implication:**
- **Builder:** default to one page and 3–5 paragraphs (≈250–400 words is a reasonable convention). Use the role-specific evidence the user provides. Shorten when the letter goes into an email or a form field.
- **Reviewer:** score specificity, meaning company- and role-specific facts that a generic letter could not contain.

---

## 7. AI-generated applications: recruiter attitudes (2024–2026)

54. TopResume (May 2025, 600 US hiring managers) [51]. — Medium
    - 19.6% would reject a fully AI-generated resume or cover letter.
    - 52% accept AI for proofreading or drafting support.
    - 25% say cover letters should stay AI-free.
55. In the same test only about a third (33.5%) correctly identified AI-written resumes. Human detection is unreliable, even though many managers claim they can tell [51]. — Medium
56. Insight Global (Nov 2024, 1,005 US hiring managers): 99% use AI in hiring, yet 54% said they care if a candidate's resume or cover letter was written by AI [52]. — Medium
57. Resume Now (2025): 62% say AI-generated resumes without customisation are more likely to be rejected, and 78% treat personal details as a sign of genuine interest [10][snippet]. — Low-Medium
58. Greenhouse (Nov 2025, 4,136 respondents in the US, UK, Ireland and Germany) [32]. — Medium-High
    - 65% of US hiring managers caught deceptive AI use.
    - 74% are more worried about misrepresented experience than a year earlier.
    - 39% are doing more in-person interviews to check authenticity.
59. AI-text detectors are unreliable. A peer-reviewed test of 14 tools found none reached 80% accuracy, with a bias toward labelling text human-written, and paraphrasing made them worse [53][snippet]. — High
60. Jobscan says no major ATS (Workday, Greenhouse, iCIMS, SuccessFactors, Lever, Taleo) is built to detect AI authorship; their AI is for matching and ranking [54][snippet]. — Low-Medium (vendor claim)
61. Harvard's career office supports *responsible* use of generative AI for career materials [30]. — High

**Skill implication:**
- The risk is not "AI detected". It is generic output, invented claims, and content the candidate cannot defend in an interview.
- Skills must ground every claim in user-supplied facts and ask questions rather than invent detail.
- Skills should push for personal specifics and encourage the user to edit the draft themselves [50].

---

## 8. Bias-avoiding content and accessibility

62. The EEOC bans discrimination in US hiring based on race, colour, religion, sex, national origin, age (40+), disability or genetic information [55][snippet]. — High
63. The US age law (ADEA) does not itself ban asking for a birth date, but such requests get scrutiny. Leaving age out of a resume removes the cue [56][snippet]. — High
64. In a field experiment of 40,000+ applications, older women faced strong age discrimination, especially near retirement age. The effect on men was weaker [57][snippet]. — High
65. Résumés with white-sounding names got 50% more callbacks than identical ones with African-American-sounding names [58][snippet]. — High
66. A cross-country European field experiment (GEMM) found discrimination based on racial appearance, using photos on CVs. Black applicants had the lowest callback rates [59][snippet]. — High
67. Attractiveness in CV photos changes callbacks, and not consistently: attractive men gained, while women without a photo were called back more often than attractive women [60][snippet]. — Medium
68. The UK National Careers Service says not to include age, date of birth, marital status or nationality [31]. Oxford's recruitment tips also exclude gender and photos [44][snippet]. — High
69. In the 2013 CareerBuilder survey, 13% of US employers named including a photo as a mistake that may lead to dismissal [8]. — Medium
70. Accessible documents need the following [61][62][snippet][63][snippet]. — High
    - real heading styles and a logical reading order
    - lists made with the built-in list tool
    - descriptive link text instead of raw URLs
    - alt text for any images
    - a tagged, text-based PDF (an untagged or scanned PDF fails screen readers)
71. Accessibility checklists say not to use tables for layout or colour alone to carry meaning. These are the same features that break ATS parsing, so the two goals agree [63][snippet][27]. — High
72. The NCS says disclosing a disability in a cover letter is optional and the candidate's choice [13]. — High

**Skill implication:**
- Default to no photo, date of birth, marital status, religion, national ID number or full street address.
- Ask before adding any of these, and only when the target market expects them (§9).
- Never fill these fields in automatically.

---

## 9. Regional conventions: when the skill must ask

| Region | Usual name | Photo | DOB / personal data | Typical length | Page size | Confidence |
|---|---|---|---|---|---|---|
| US / Canada | Resume (CV = academic/medical) [46] | No. Canadian guidance says photos are not the norm [64][snippet][65][snippet] | Omit. US anti-discrimination law [55][56]; Canadian guidance omits age and marital status [65] | 1 page early career; 2 pages experienced [8][30] | US Letter [66][snippet] | High |
| UK / Ireland | CV | No [44] | Omit DOB, marital status, nationality [31] | 2 pages (1–2) [43][44] | A4 [66] | High |
| EU / Germany | CV / Lebenslauf (Europass optional) [42] | Not mandatory but still expected by most German employers [42]. Europass tips suggest a professional photo [67][snippet] | Germany: DOB and place of birth often included; marital status and religion not required [42] | ≤2 pages [42] | A4 | High for Germany; **other EU countries vary, so ask** |
| Australia / NZ | Resume (CV also used) | No [68][snippet] | Omit gender, age, religion, marital status [68] | 2–3 pages typical; 1–3 by industry [69][snippet][70][snippet] | A4 | Medium (NZ not separately verified) |
| Asia (general) | CV / resume; local forms (e.g. Japan's rirekisho) | **Varies.** Japan's rirekisho expects a formal photo [71][snippet]. Indeed SG/HK advise leaving it out to avoid bias [72][snippet] | Varies; DOB is common in some markets | 1–2 pages; local forms are fixed | A4 (Letter in the Philippines) [66] | Low-Medium: **always ask** |
| Middle East (GCC) | CV | Commonly included | Nationality and visa status often expected | ~2 pages | A4 | Low (vendor sources only [73][snippet]): **ask** |

**Rule for skills:** if the target country or employer is unknown, ask. If the user doesn't know, use the bias-safe international default: no photo or DOB, two pages at most, A4 unless the target is North America.

Reference lines differ too. The UK NCS accepts "references available on request" [31], while US sources call the phrase outdated [74][snippet].

---

## 10. Honesty and verification

73. In a 2014 CareerBuilder/Harris survey, 58% of hiring managers had caught a lie on a resume [9][snippet]. Germany's Federal Employment Agency says to list only references and experience you can verify [42]. — Medium/High
74. Greenhouse reports more in-person interviews and more checks on misrepresented experience [32]. Inflated or AI-invented claims now carry a higher risk of being caught. — Medium

**Skill implication:** never fabricate metrics, titles, dates or credentials. Mark unknowns and ask the user to supply or confirm them.

---

## Bibliography

1. [50 HR & Recruiting Stats That Make You Think](https://www.glassdoor.com/blog/50-hr-recruiting-stats-make-think/), Glassdoor, 2015-01. [snippet]
2. [2026 Applicant Tracking System (ATS) Usage Report](https://www.jobscan.co/blog/fortune-500-use-applicant-tracking-systems/), Jobscan, 2026. [opened]
3. [Recruitment Funnel Benchmarks 2026 (citing CareerPlug 2025)](https://www.pin.com/blog/recruitment-funnel-benchmarks/), pin.com, 2026; see also [CareerPlug Recruiting Metrics 2025](https://www.careerplug.com/recruiting-metrics-and-kpis/). [snippet]
4. [TheLadders Reveals That Job Seekers Have Six Seconds To Succeed](http://www.prnewswire.com/news-releases/theladders-reveals-that-job-seekers-have-six-seconds-to-succeed-143629046.html), Ladders/PR Newswire, 2012-03-21. [snippet]
5. [Ladders Updates Popular Recruiter Eye-Tracking Study](https://www.prnewswire.com/news-releases/ladders-updates-popular-recruiter-eye-tracking-study-with-new-key-insights-on-how-job-seekers-can-improve-their-resumes-300744217.html), Ladders/PR Newswire, 2018-11-06. [opened]
6. [Do Recruiters Really Only Look at Your Resume for 6 Seconds?](https://simplify.jobs/blog/6-second-resume-rule), Simplify, 2026. [snippet]
7. [One Or Two Page Resumes](https://www.resumego.net/research/one-or-two-page-resumes/), ResumeGo, 2018. [opened]
8. [CareerBuilder Releases Study of Common and Not-So-Common Resume Mistakes](https://www.prnewswire.com/news-releases/careerbuilder-releases-study-of-common-and-not-so-common-resume-mistakes-that-can-cost-you-the-job-223251611.html), CareerBuilder/Harris Interactive, 2013-09-11. [opened]
9. [Ridiculous Lies People Told on Resumes](https://www.businessinsider.com/ridiculous-lies-people-told-on-resumes-2014-8), Business Insider (CareerBuilder data), 2014-08. [snippet]
10. [62% of Employers Reject AI-Generated Resumes Without Personalization](https://www.resume-now.com/job-resources/careers/ai-applicant-report), Resume Now, 2025-06; 36% figure via [Staffing Industry Analysts](https://www.staffingindustry.com/news/global-daily-news/hr-pros-say-ai-cant-replace-the-human-touch-survey-says), 2025-07. [snippet; 403 on fetch]
11. [How Long Should a Cover Letter Be?](https://resumegenius.com/blog/cover-letter-help/how-long-should-a-cover-letter-be), Resume Genius, 2026. [snippet]
12. [Career guides: cover letters](https://guides.library.harvard.edu/gsd/write/career), Harvard Library (GSD), n.d. [snippet]
13. [How to write a cover letter](https://nationalcareers.service.gov.uk/careers-advice/covering-letter), National Careers Service (UK Gov), n.d. [opened]
14. [CV and covering letter workbook](https://www.ncl.ac.uk/media/wwwnclacuk/careersservice/files/CV%20and%20covering%20letter%20workbook%20accessible%20version.pdf), Newcastle University Careers Service, n.d. [snippet]
15. [How Long Is a Cover Letter: Guidelines & Examples](https://coverlettercopilot.ai/blog/how-long-is-a-cover-letter), Cover Letter Copilot, 2026. [snippet; claim judged unreliable]
16. [Cover Letters: Just How Important Are They?](https://www.resumego.net/research/cover-letters/), ResumeGo, 2020 (field work 2019-07 to 2020-01). [opened]
17. [Should I Write a Cover Letter for Every Job?](https://coverlettercopilot.ai/blog/should-i-write-a-cover-letter-for-every-job), Cover Letter Copilot, 2026. [snippet]
18. [The ATS Resume Rejection Myth](https://blog.theinterviewguys.com/ats-resume-rejection-myth/), The Interview Guys, 2026 (relays a LinkedIn article; secondary source); also [HR Gazette](https://hr-gazette.com/debunking-the-ats-rejection-myth/), 2025. [opened (Interview Guys); HR Gazette snippet only]
19. [Does the ATS Reject Your Resume? 25 Recruiters Explain](https://enhancv.com/blog/does-ats-reject-resumes/), Enhancv, 2025-11. [opened]
20. [Recruiters are 'drinking through a fire hose' of job applications](https://www.cnbc.com/2025/10/29/recruiters-are-drinking-through-a-fire-hose-of-job-applications-experts-say.html), CNBC, 2025-10-29. [snippet]
21. [Are Cover Letters Dead in 2026? (Novorésumé release; cites LinkedIn +45%)](https://natlawreview.com/press-releases/are-cover-letters-dead-2026-new-survey-reveals-most-recruiters-ignore-them), EIN Presswire via NatLawReview, 2025-12-16. [opened]
22. [LinkedIn Announces Hiring Assistant 2](https://news.linkedin.com/2026/hiring-assistant-2), LinkedIn, 2026. [snippet]
23. [You have 7.4 seconds to make an impression](https://www.theladders.com/career-advice/you-only-get-6-seconds-of-fame-make-it-count), Ladders, updated 2026. [snippet]
24. [Resume FAQs for Undergraduate and Master Students](https://careered.stanford.edu/sites/g/files/sbiybj22801/files/media/file/resume_faqs_handout.pdf), Stanford Career Education (BEAM), n.d. [opened]
25. [Hidden Workers: Untapped Talent](https://www.hbs.edu/faculty/Pages/item.aspx?num=61232), Harvard Business School & Accenture, 2021-09. [snippet]
26. [Supported formats for resumes, cover letters and other candidate uploads](https://support.greenhouse.io/hc/en-us/articles/360052218132-Supported-formats-for-resumes-cover-letters-and-other-candidate-uploads), Greenhouse Support, 2026. [snippet]
27. [Unsuccessful resume parse](https://support.greenhouse.io/hc/en-us/articles/200989175-Unsuccessful-resume-parse), Greenhouse Support, 2026. [opened]
28. [Understanding resume parsing](https://help.lever.co/hc/en-us/articles/20087345054749-Understanding-resume-parsing), Lever Help Center, 2024-09. [snippet; 401 on fetch]
29. [Workday Resume Format: What the Parser Reads](https://resumeoptimizerpro.com/blog/workday-resume-format), ResumeOptimizerPro, 2026. [snippet; third-party]
30. [Harvard Griffin GSAS Master's Resume & Cover Letter Guide](https://cdn-careerservices.fas.harvard.edu/wp-content/uploads/sites/161/2025/08/MASTERS-RESUME-COVER-LETTER-GUIDE.pdf), Harvard FAS Mignone Center for Career Success, 2025-08. [opened]
31. [How to write a CV](https://nationalcareers.service.gov.uk/careers-advice/cv-sections), National Careers Service (UK Gov), n.d. [opened]
32. [An AI Trust Crisis: Greenhouse 2025 AI in Hiring Report](https://www.greenhouse.com/uk/newsroom/an-ai-trust-crisis-70-of-hiring-managers-trust-ai-to-make-faster-and-better-hiring-decisions-only-8-of-job-seekers-call-it-fair), Greenhouse, 2025-11-19. [opened]
33. [My Personal Formula for a Winning Resume (Laszlo Bock, copy)](https://scitechmn.org/wp-content/uploads/2017/04/Formula-for-a-Winning-Resume.pdf), originally LinkedIn, 2014-09-29. [snippet]
34. [A Google Executive Reviewed More Than 20,000 Resumes](https://www.inc.com/peter-economy/a-google-executive-reviewed-more-than-20000-resumes-heres-his-surprising-secret-for-writing-a-winning-one.html), Inc., 2019-10. [snippet]
35. [Resumes: Writing about your skills](https://capd.mit.edu/resources/resumes-writing-about-your-skills/), MIT CAPD, 2022. [snippet]
36. [Resume action verbs](https://capd.mit.edu/resources/resume-action-verbs/), MIT CAPD, 2021. [snippet]
37. [Resumes (Alumni career resources)](https://www.gsb.stanford.edu/alumni/career-resources/job-search/resumes), Stanford GSB, n.d. [snippet]
38. [The STAR method](https://nationalcareers.service.gov.uk/careers-advice/interview-advice/the-star-method), National Careers Service (UK Gov), n.d. [snippet]
39. [How to Write a STAR Method Resume](https://www.tealhq.com/post/star-method), Teal, 2026. [snippet]
40. [PAR Method vs STAR Method](https://starmethod.org/blog/interviewing/par-method-vs-star-method), starmethod.org, 2024. [snippet]
41. [Federal resume tips](https://www.careeronestop.org/Veterans/JobSearch/FederalHiring/federal-resume-tips.aspx), CareerOneStop (US DOL), n.d.; [Resume guide](https://www.careeronestop.org/JobSearch/Resumes/resumes.aspx). [snippet; 403 on fetch]
42. [Application process in Germany, Part 1: curriculum vitae](https://www.arbeitsagentur.de/vor-ort/zav/working-and-living-in-germany/iss-en/issue-01-2026/application-cv), Bundesagentur für Arbeit (ZAV), 2026. [opened]
43. [CVs](https://www.ox.ac.uk/careers/careers-guidance/job-search-and-applications/writing-applications/cvs), University of Oxford Careers, 2026. [snippet; 403 on fetch]
44. [CV tips](https://www.jobs.ox.ac.uk/tss-cv-tips), University of Oxford Jobs (Temporary Staffing Service), n.d. [snippet]
45. [GSAS CV & Cover Letter Guide](https://careerservices.fas.harvard.edu/resources/gsas-cv-cover-letter-guide-2/), Harvard FAS, 2026. [snippet]
46. [Resume vs. CV: Key Document Differences](https://www.indeed.com/career-advice/resumes-cover-letters/difference-between-resume-and-cv), Indeed, 2023. [snippet]
47. [Resume vs. CV: What are the differences?](https://uk.indeed.com/career-advice/cvs-cover-letters/resume-vs-cv), Indeed UK, 2026. [snippet]
48. [50+ Cover Letter Statistics for 2026](https://resumegenius.com/blog/cover-letter-help/cover-letter-statistics), Resume Genius (2022 survey, n=625), updated 2026. [opened]
49. Same as [21]: Novorésumé recruiter survey, 2025-12-16. [opened]
50. [Signaling in the Age of AI: Evidence from Cover Letters](https://arxiv.org/html/2509.25054v1), Yale (Cowles) researchers, arXiv, 2025-09. [opened]
51. [Survey: Where Employers Draw the Line on the Use of AI in Hiring](https://topresume.com/career-advice/ai-in-hiring-survey), TopResume, 2025-06. [opened]
52. [Insight Global "AI in Hiring" Survey](https://insightglobal.com/press-release/insight-global-ai-in-hiring-survey-highlights-essential-role-of-tech-enabled-people/), Insight Global, 2025. [opened]
53. [Testing of detection tools for AI-generated text](https://edintegrity.biomedcentral.com/articles/10.1007/s40979-023-00146-z), Weber-Wulff et al., Int. J. for Educational Integrity, 2023-12. [snippet]
54. [Can ATS Detect AI Resumes in 2026?](https://www.jobscan.co/blog/can-ats-detect-ai-resume/), Jobscan, 2026. [snippet]
55. [Prohibited Employment Policies/Practices](https://www.eeoc.gov/prohibited-employment-policiespractices), US EEOC, 2025. [snippet]
56. [Fact Sheet: Age Discrimination](https://www.eeoc.gov/laws/guidance/fact-sheet-age-discrimination), US EEOC, 2025. [snippet]
57. [Is It Harder for Older Workers to Find Jobs?](https://www.nber.org/papers/w21669), Neumark, Burn & Button, NBER WP 21669. [snippet]
58. [Are Emily and Greg More Employable than Lakisha and Jamal?](https://www.nber.org/papers/w9873), Bertrand & Mullainathan, NBER/AER, 2003–04. [snippet]
59. [Catching up with GEMM: racial discrimination in job recruitment in Europe](http://cordis.europa.eu/article/id/446731-catching-up-with-gemm-uncovering-racial-discrimination-in-job-recruitment-in-europe), CORDIS (European Commission), 2023-09. [snippet]
60. [Are Good-Looking People More Employable?](https://www.researchgate.net/publication/228279644_Are_Good-Looking_People_More_Employable), Ruffle & Shtudiner, working paper, ~2010. [snippet]
61. [A Guide to Creating an Accessible Resume](https://career.stthomas.edu/resources/a-guide-to-creating-an-accessible-resume/), University of St. Thomas Career Development Center, 2024-01. [opened]
62. [Creating PDF & Microsoft Office Documents](http://www2.cuny.edu/accessibility/content/pdf-microsoft/), CUNY Accessibility, n.d. [snippet]
63. [Document Accessibility Checklist](https://accessibility.ucmerced.edu/digital-accessibility/creating-content-checklists/document-accessibility-checklist), UC Merced, n.d. [snippet]
64. [How do I create a Canadian-style resume?](https://settlement.org/ontario/employment/find-a-job/resume/how-do-i-create-a-canadian-style-resume/), Settlement.org (Ontario), 2023. [snippet]
65. [What Is the Canada Resume Format?](https://ca.indeed.com/career-advice/resumes-cover-letters/canada-resume-format), Indeed Canada, 2026. [snippet]
66. [Paper sizes: Globalization](https://learn.microsoft.com/en-us/globalization/locale/paper-size), Microsoft Learn, 2025-04. [snippet]
67. [Create your Europass CV](https://europass.europa.eu/en/create-europass-cv), Europass (European Commission), n.d. [snippet]
68. [Resume Checklist](https://students.unimelb.edu.au/__data/assets/pdf_file/0008/3317291/Careers_ResumeChecklist.pdf), University of Melbourne Careers, n.d. [snippet]
69. [How to write a resume](https://www.sydney.edu.au/careers/students/applying-for-jobs/how-to-write-a-resume.html), University of Sydney Careers, n.d. [snippet]
70. [Your Resume Toolkit](https://www.jobsandskills.wa.gov.au/sites/default/files/uploads/Jobs&Careers/Your_resume_toolkit_online.pdf), Jobs and Skills WA (Govt of Western Australia), n.d. [snippet]
71. [Rirekisho guide](https://www.daijob.com/en/guide/tipsadvice/resume/rirekisyo/), Daijob, 2024. [snippet]
72. [Should You Include a Resume Photo?](https://sg.indeed.com/career-advice/resumes-cover-letters/resume-photo), Indeed Singapore, 2025; [Indeed Hong Kong](https://hk.indeed.com/career-advice/cvs-cover-letters/photo-on-cv), 2025. [snippet]
73. [Gulf CV format](https://blog.loopcv.pro/gulf-cv-format/), LoopCV, 2026; [Bahrain CV](https://www.visualcv.com/international/bahrain-cv/), VisualCV. [snippet; vendor]
74. ["References Available Upon Request": Is It Needed?](https://www.indeed.com/career-advice/resumes-cover-letters/references-available-upon-request), Indeed, 2023. [snippet]
75. [Are You Ready for the Workplace Fairness Act](https://www.tal.sg/tafep/resources/articles/2026/are-you-ready-for-the-workplace-fairness-act), TAFEP (Singapore), 2026-04-20. [opened; says the Act takes effect at the end of 2027]
76. [Anrede Brief/E-Mail: Geschlecht unklar oder divers](https://www.uwefreund.com/fraguwe-de/briefe-emails/korrekte-anrede-in-brief-und-e-mail-wenn-sie-das-geschlecht-des-adressaten-nicht-kennen/), Uwe Freund, n.d. [opened; language guide]
77. [Formules de politesse pour lettres et mails](https://www.laposte.fr/conseils-pratiques/rediger-une-lettre-formelle-quelles-formules-de-politesse), La Poste, n.d. [opened; language guide]
