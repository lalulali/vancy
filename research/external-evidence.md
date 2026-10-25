# External Evidence Base (cited)

Purpose: every rule the skills enforce should trace to either the local corpus (`research/corpus/*`) or a source below. Content is paraphrased; short quotes are marked.

Evidence grade:
- **A**: government, statute, regulator, or peer-reviewed or preprint research with a disclosed method
- **B**: a field experiment or survey with a disclosed sample, run by an industry body
- **C**: vendor blog or secondary reporting. Treat as directional only.

Research date: 16 Oct 2026. Re-verify anything legal before each release.

## 1. How documents are read

| # | Claim used by skills | Grade | Source |
|---|---|---|---|
| E1 | Average initial resume screen is about 7.4 s (6 s in 2012). Recruiters scan job titles, layout, text flow and keywords. | B | [Ladders 2018 Eye-Tracking Study, PR Newswire](https://www.prnewswire.com/news-releases/ladders-updates-popular-recruiter-eye-tracking-study-with-new-key-insights-on-how-job-seekers-can-improve-their-resumes-300744217.html) |
| E2 | The best-performing resumes have simple layouts with clear section and title headers, bold job titles, bulleted accomplishments and an overview at the top. The worst have multiple columns, long sentences, little white space and keyword stuffing. The study recommends using keywords only in context. | B | Same as E1 |
| E3 | Recruiters chose 2-page resumes 2.3× as often as 1-page ones (482 hiring professionals, about 20k resumes), and the preference was stronger for senior roles. | B | [ResumeGo: One or Two Page Resumes](https://resumego.net/research/one-or-two-page-resumes/); [CNBC coverage](https://www.cnbc.com/2018/12/19/resumego-hiring-managers-prefer-candidates-with-two-page-resumes.html) |
| E4 | US federal jobs: from 27 Sep 2025, USAJOBS accepts resumes of 2 pages maximum. Exceptions include some CV-type roles. | A | [OPM Applicant Guidance on the Two-Page Limit](https://www.opm.gov/policy-data-oversight/hiring-information/merit-hiring-plan-resources/applicant-guidance-on-the-two-page-resume-limit/); [USAJOBS Help Center](https://usajobshelp.opm.gov/hc/en-us/articles/52839989720851-How-do-I-write-a-resume-for-a-federal-job) |
| E5 | Achievement formula: "Accomplished [X] as measured by [Y] by doing [Z]". Start with an active verb, quantify, give a baseline, state the method. | B | Laszlo Bock (ex-SVP People Ops, Google) via [Business Insider](https://www.businessinsider.com/laszlo-bock-gives-key-to-perfect-resume-2016-10) and [Inc.](https://www.inc.com/peter-economy/a-google-executive-reviewed-more-than-20000-resumes-heres-his-surprising-secret-for-writing-a-winning-one.html) |
| E6 | University guidance: tailor to the role, use action verbs, be fact-based, and put keywords from the job description in context. | A | [Harvard FAS Career Services – resumes & cover letters](https://careerservices.fas.harvard.edu/resources/hes-create-impactful-resumes-and-cover-letters/); [Harvard FAS – AI for resumes](https://careerservices.fas.harvard.edu/ai-resumes-and-cover-letters/); [Harvard Law action verbs](https://hls.harvard.edu/bernard-koteen-office-of-public-interest-advising/opia-job-search-toolkit/action-verbs/) |
| E7 | Nearly 6 in 10 (about 58–61%) hiring managers say they would dismiss a resume with typos. | C | CareerBuilder survey via [Computerworld](https://www.computerworld.com/article/1393490/the-8-most-common-reasons-your-resume-is-tossed.html) and [ERE](https://www.ere.net/we-tried-to-avoid-the-typos-in-todays-roundup/). This corroborates the "58%" figure in the ResumeWriter guide. |
| E8 | About half of employers would dismiss a candidate caught lying on a resume. | C | CareerBuilder via [Adweek](https://www.adweek.com/performance-marketing/new-study-shows-majority-of-employers-catch-lies-on-resume/) |

## 2. ATS

| # | Claim | Grade | Source |
|---|---|---|---|
| E9 | About 97–98% of Fortune 500 companies use a detectable ATS. | B | [Jobscan ATS Usage Report](https://www.jobscan.co/blog/fortune-500-use-applicant-tracking-systems/) |
| E10 | "75% of resumes are auto-rejected by ATS" is a myth. In interviews, 23 of 25 US recruiters said their ATS does not auto-reject on formatting or content. Real automatic knockouts come from screening questions such as work authorisation or location. | B/C (n=25) | [Enhancv: Does ATS reject resumes?](https://enhancv.com/blog/does-ats-reject-resumes/) |
| E11 | Multi-column layouts are a known parsing challenge. Even market-leading parsers have to apply special handling to them. | C (vendor) | [Textkernel: Improving extraction from column resumes](https://www.textkernel.com/learn-support/blog/improving-extraction-from-column-resumes/) |

**Design implication:** optimise for human skim (E1–E2) and for keyword *search* inside the ATS (E9). Do not scare users with auto-reject claims (E10). Default to a single-column layout with no tables (E2, E11, corpus template analysis).

## 3. Cover letters

| # | Claim | Grade | Source |
|---|---|---|---|
| E12 | Field experiment with 7,287 applications. A tailored cover letter gave about 53% more callbacks than no letter, and a generic letter added little. 87% of 236 surveyed hiring professionals read cover letters, and 81% value tailored letters significantly more than generic ones. | B | [ResumeGo: Cover Letters – Just How Important Are They?](https://www.resumego.net/research/cover-letters/) |
| E13 | When an AI cover-letter tool was introduced on a large freelance platform, letters aligned more closely with job posts, but the link between that alignment and callbacks fell by 51%. Employers shifted weight to other signals such as work history. Time spent editing the AI draft correlated with hiring success. | A (preprint) | [Cui et al., "Signaling in the Age of AI: Evidence from Cover Letters", arXiv:2509.25054](https://arxiv.org/abs/2509.25054) |
| E14 | Most US hiring managers say they can spot AI-written resumes. Generic, metric-free phrasing is the giveaway. | C | [Forbes on Resume Genius survey, Mar 2026](https://www.forbes.com/sites/rachelwells/2026/03/19/8-in-10-hiring-managers-spot-ai-resumes-these-3-mistakes-give-it-away/); [TopResume AI-in-hiring survey 2025](https://topresume.com/career-advice/ai-in-hiring-survey) |

**Design implication (E13, E14):** keyword matching alone is no longer a differentiator. The skills must force *specific, verifiable* content: real metrics, named company facts and the candidate's own voice. They must also prompt the user to edit the draft, and never ship generic AI phrasing. The house-template boilerplate found in the corpus (e.g. "It is with great enthusiasm…" ×15) should be flagged.

## 4. Personal data and anti-discrimination by market

| # | Market | Rule / norm | Grade | Source |
|---|---|---|---|---|
| L1 | **US** | Federal law (ADEA) protects people aged 40+. Asking for date of birth is not itself illegal, but it is scrutinised. US norm: no photo, DOB or marital status. | A | [EEOC: Age Discrimination](https://www.eeoc.gov/laws/guidance/age-discrimination); [29 CFR §1625.7](https://www.gpo.gov/fdsys/pkg/CFR-2012-title29-vol4/pdf/CFR-2012-title29-vol4-sec1625-7.pdf) |
| L2 | **UK** | Equality Act 2010. Employers should collect DOB only on a separate equality-monitoring form that selectors don't see. University careers services advise against putting a photo, DOB, gender or nationality on a CV. The National Careers Service lists CV sections as contact details, introduction, education, work history and references. | A | [GOV.UK: Discrimination in recruitment](https://www.gov.uk/employer-preventing-discrimination/recruitment); [Univ. of Edinburgh Careers](https://careers.ed.ac.uk/cvs-and-applications/building-your-cv); [National Careers Service: CV sections](https://nationalcareers.service.gov.uk/careers-advice/cv-sections) |
| L3 | **Canada** | No photo, age, marital status or SIN. Use Canadian spelling. | C (consistent across sources) | [CanadaVisa](https://www.canadavisa.com/resume.html); [Indeed CA](https://ca.indeed.com/career-advice/resumes-cover-letters/canada-resume-format) |
| L4 | **Australia** | 1–3 pages depending on experience. Use headings and dot points. Public-sector roles may require responses to selection criteria. | A (state gov) | [Queensland Government: resume & cover letter](https://www.qld.gov.au/jobs/finding/resume); [NSW DCJ](https://dcj.nsw.gov.au/content/dcj/dcj-website/dcj/about-us/careers-at-dcj/applying-for-dcj-jobs/preparing-your-cover-letter-and-resume.html); [ASIC resume tips](https://careers.asic.gov.au/pdf/Resume_tips.pdf) |
| L5 | **Singapore** | The Workplace Fairness Act 2025 lists 11 protected characteristics: age, nationality, sex, marital status, pregnancy, caregiving, race, religion, language ability, disability and mental health. It is expected to take effect by **end-2027**. TAFEP guidance already says employers should not ask for irrelevant personal information. Nationality/PR is still commonly shown because of work-pass rules (corpus: 60/62 CVs). | A | [Workplace Fairness Act 2025 (AGC)](https://sso.agc.gov.sg/Acts-Supp/8-2025/Published/20250213?DocDate=20250213&ViewType=Pdf&_=20250228130405); [CNA: takes effect 2027](https://www.channelnewsasia.com/singapore/landmark-workplace-fairness-law-passed-take-effect-in-2027-5444626); [TAFEP: fair application forms](https://www.tal.sg/tafep/employment-practices/recruitment/preparing-job-application-forms?); [law.asia summary](https://law.asia/singapore-workplace-fairness-act-2025/) |
| L6 | **Germany / DACH** | Since the AGG (2006), employers may not require a photo. A photo remains common but optional. Tabular Lebenslauf, often 1–2 pages. | C (consistent) | [berufe.eu](https://www.berufe.eu/bewerbungsfoto/); [ankommo](https://app.ankommo.de/german-cv-builder) |
| L7 | **France** | Photo and DOB are optional. Age-based hiring discrimination is illegal. | C | [cv.fr – photo](https://www.cv.fr/conseils/photo-cv); [Indeed FR](https://fr.indeed.com/conseils-carrieres/cv-lettres-motivation/cv-age) |
| L8 | **EU (Europass)** | Official EU CV format. A photo is optional (the builder suggests a professional one if used). | A | [Europass: Create your CV](https://europass.europa.eu/en/create-europass-cv) |
| L9 | **Japan** | Two documents: *rirekisho*, a standardised JIS-style form with DOB and a photo, and *shokumu keirekisho*, a free-form career history. | C (consistent) | [TokyoDev guide](https://www.tokyodev.com/articles/japanese-resumes); [Japan Dev](https://japan-dev.com/blog/japanese-cv-shokumu-keirekisho) |
| L10 | **GCC (UAE etc.)** | A photo, nationality and **visa status** plus notice period are commonly expected. Keep a single-column layout. | C | [VisualCV UAE](http://www.visualcv.com/international/uae-resume/); [Jobseeker Dubai](https://jobseeker.com/en/cv/articles/dubai-cv) |
| L11 | **India** | Fresher resumes often use a career objective, projects and a closing declaration (date, place, signature). | C (major local job board) | [Naukri: declaration](https://www.naukri.com/campus/career-guidance/declaration-for-resume-for-freshers); [Naukri: fresher format](https://www.naukri.com/campus/career-guidance/resume-format-for-freshers) |

Grade C rows reflect convention, not law. The skills should present them as defaults the user can override.

## 5. Verification of the ResumeWriter.SG guides (local artifacts)

| Guide claim | Status |
|---|---|
| Recruiters scan for "6–7 seconds" | **Supported** by E1 (7.4 s, 2018) |
| "58% dismiss for typos" | **Supported** by E7 (≈58–61%) |
| Achievement formula X/Y/Z | **Supported**, originally from Bock (E5) |
| "250 resumes per posting, 4–6 interviewed" | **Unverified**: no source given. Widely repeated online but untraceable. Don't present it as fact. |
| "36% of resumes rejected for being too generic" | **Unverified**: no source given. Don't cite it. |
| "Keep CV under 3 pages; <5 yrs → 2 pages" | Matches SG practice and E3. US norms are shorter for juniors, and the US federal limit is 2 pages (E4). |
| "Don't include photo/DOB/address" | Aligned with L1, L2, L3 and L5. Conflicts with DE, JP and GCC norms, so it needs a locale switch. |
| Cover letter 250–400 words, 1 page | Corpus median is 341 words. No contrary evidence found. |
| "Always submit a cover letter, even if optional" | Supported by E12, with the caveat in E13: it pays off only if specific. |
