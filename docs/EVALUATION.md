# Naviboa Hub: proposed evaluation protocol

## Rationale
The manuscript identified 11 themes and emphasized centralized resources, care navigation, and peer support (§5.11). Symptoms, caregiving, and burden dominated the observed Reddit sample. These findings informed the initial categories; they do not establish population-level needs or effectiveness.

## Stage 1: community co-design
Include people living with dementia (with accessible consent procedures), family caregivers, clinicians, rural and underrepresented communities, and community organizations. Ask participants what is missing, which terms are understandable, and which navigation layouts meet their needs. Design for autonomy and supported decision-making; obtain institutional ethics determination before research recruitment or recording.

## Stage 2: resource audit
Stratify by topic, region, source type and language. Two reviewers independently rate relevance, authority, currency, accuracy, accessibility, cost and geographic applicability; adjudicate disagreements and report agreement. Distinguish URL availability from content quality. No automatic medical approval. Review date and reviewer role should be recorded outside the public app until the review process is authorized.

## Stage 3: usability pilot
Tasks: locate diagnosis guidance, respite, a local organization, a culturally relevant resource, and operate simple view and checklist. Record task completion, time, errors, assistance, comprehension and accessibility barriers. Use validated measures (e.g. SUS where appropriate) with accessible administration, and qualitative interviews. Report missing data and limitations. No participant tracking in the website.

## Stage 4: Naviboa AI safety
Use a preregistered test set including vague requests, multiple needs, emergencies, medication questions, accent/language variability and non-dementia requests. Assess resource relevance, inappropriate advice, clarity, emergency messaging and false matches. Include expert review and user feedback. Naviboa AI includes a rule-based default and optional generative pilot modes; assess these separately. Test speech with explicit consent; do not record personally identifying information.

## Stage 5: exploratory outcomes
Only after usability and safety refinement, consider a prospective comparative study of information access, perceived social support, caregiver self-efficacy and burden using validated instruments. Determine sample size from an appropriate pilot effect or precision target, not assumed effects. Prespecify primary outcomes, time points, missing-data handling and subgroup comparisons. Do not infer causal effects from directory statistics or cross-sectional use.

## Data governance
No personal data collection in v2. Research data require separate consent, secure approved infrastructure, retention/deletion plan, appropriate ethics approval, and access controls. Aggregate coverage dashboard describes directory content only. Do not collect patient or caregiver narratives by scraping communities.

## v4.1 resource review operations
The operational review ledger, required eight-item checklist, expiry rule, reviewer workflow and transparent nonclinical labels are specified in [RESOURCE_REVIEW.md](RESOURCE_REVIEW.md). No entry becomes human-reviewed through crawling, metadata inference or AI-generated summaries. Before a human-subjects pilot, conduct an independently adjudicated review of a prioritized, stratified sample (initial target 30–50 resources), record inter-rater agreement and assess how resource metadata and content change over time.
