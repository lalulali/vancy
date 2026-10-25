# Evidence: Product Manager Case and Technical Interviews

Use in **drafts** only (cite as `[^n]`, definition line copied from the Bibliography). Never cite in the final prep sheet (`--final` strips citations).

## Rules
- Sources tagged `[snippet]` were read from search snippets or publisher summaries only.
- Distinguish **peer-reviewed selection and experimentation research** from **industry frameworks** (CIRCLES, RICE, AARRR, HEART). Frameworks are widely taught practitioner scaffolds, not empirically validated laws. Say "commonly advised in PM interviews", never "proven to get an offer".
- Never promise an outcome, and never state unverified company metrics or market sizes as fact (label them illustrative assumptions or `[verify]`).

## Findings

### A. Structured and work-sample interviews
1. Sackett et al. (2022) re-analysed decades of personnel-selection research and found structured interviews and work-sample / job-knowledge tests among the strongest predictors of job performance [1]. — High (peer-reviewed). **Implication: PM case rounds (product design, metrics debugging, prioritisation, PRD take-homes) act as structured work samples scored against explicit rubrics (`scoring-rubric.md`).**
2. McDaniel et al. (1994) found structured interviews with standardized scoring rubrics significantly more valid than unstructured interviews [2]. — High (peer-reviewed).

### B. Online controlled experiments (A/B testing) and metrics
3. Kohavi, Tang & Xu (*Trustworthy Online Controlled Experiments*, 2020) document why online experiments require an Overall Evaluation Criterion (OEC / North Star), guardrail metrics, checks for Sample Ratio Mismatch (SRM) and instrumentation bugs ("Twyman's Law": any figure that looks interesting or different is usually wrong — check logging first), and full weekly cycles to account for day-of-week and novelty effects [3]. — High (authoritative practitioner & academic text).
4. Heart / AARRR / North Star / RICE frameworks (Rodden et al. 2010 for HEART; McClure for AARRR; Intercom for RICE) are industry conventions for decomposing user funnels and roadmap trade-offs [4][5]. — Medium (practitioner convention).

### C. AI risk, evaluation, and LLM security
5. The NIST AI Risk Management Framework (AI RMF 1.0, 2023) organises trustworthy AI around validity/reliability, safety, security/resilience, accountability/transparency, explainability, privacy, and fairness with socio-technical context and human oversight [6]. — High (official standard).
6. The OWASP Top 10 for Large Language Model Applications highlights Prompt Injection (direct and indirect via retrieved content), Sensitive Information Disclosure, Supply Chain, Improper Output Handling, and Excessive Agency (unbounded tool execution without human confirmation) as primary application risks [7]. — High (industry security standard).

## Bibliography
1. [Revisiting meta-analytic estimates of validity in personnel selection: Addressing systematic overcorrection for restriction of range](https://pubmed.ncbi.nlm.nih.gov/34968080/), Sackett, Zhang, Berry & Lievens, Journal of Applied Psychology, 2022. [snippet]
2. [The validity of employment interviews: A comprehensive review and meta-analysis](https://www.researchgate.net/publication/232558086_The_validity_of_employment_interviews_A_comprehensive_review_and_meta-analysis_The_Journal_of_Applied_Psychology_79_599-616), McDaniel et al., Journal of Applied Psychology, 1994. [snippet]
3. [Trustworthy Online Controlled Experiments: A Practical Guide to A/B Testing](https://experimentguide.com/), Kohavi, Tang & Xu, Cambridge University Press, 2020. [snippet]
4. [Measuring the User Experience on a Large Scale: User-Centered Metrics for Web Applications](https://research.google/pubs/measuring-the-user-experience-on-a-large-scale-user-centered-metrics-for-web-applications/), Rodden, Hutchinson & Fu, CHI, 2010. [snippet]
5. [RICE: Simple prioritization for product managers](https://www.intercom.com/blog/rice-simple-prioritization-for-product-managers/), McBride, Intercom, 2016. [snippet]
6. [Artificial Intelligence Risk Management Framework (AI RMF 1.0)](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf), NIST, US Department of Commerce, 2023. [snippet]
7. [OWASP Top 10 for Large Language Model Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/), OWASP Foundation, 2025. [snippet]

