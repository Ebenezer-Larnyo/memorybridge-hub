# Naviboa Hub
Research-informed dementia resource discovery prototype, based on Larnyo, Benyassine and Preece's manuscript, section 5.11. Sister project to Spectrum Hub. US-first with international starter resources. No clinical validation.

## Local use
Run python -m http.server 8000 and open http://localhost:8000. No API key needed.

## Deployment
Settings > Pages > Source > GitHub Actions. Run Publish Naviboa Hub. Refresh dementia resources is scheduled daily at 15:23 UTC (7:23 AM PST / 8:23 AM PDT). It can also be started manually. Review source-specific policies and use repository issues for crawler contact; remove sources that do not permit crawling. Scheduled runs may be delayed by GitHub. Review Actions logs and data/crawl-report.json. GitHub may disable scheduled workflows on inactive repositories.

## Crawler
Install requirements.txt and run python scripts/crawl.py. Same-host, robots-aware, rate-limited discovery from selected sources; no private data or forum collection. New entries are unreviewed, and link checks are not clinical verification. Source failures preserve old entries. Review all results manually, and remove outdated or misleading links. Run python -m unittest discover -s tests. Test search, keyboard navigation, mobile layout, and accessibility controls before launch.

## Research
Co-design with people living with dementia, caregivers and clinicians. Evaluate comprehension, task completion, resource quality, accessibility, usefulness and equity. Obtain applicable ethics approval before collecting research data. The manuscript's Reddit sample is caregiver-heavy and not representative; reconcile 664 vs 665 posts before publication. Version 2.0 includes Mira, a deterministic resource-link navigator (not a generative AI or clinician), optional browser speech input and output where supported, local opt-in checklists, simple daily orientation view, a Spanish resource guide and directory coverage dashboard. No accounts, backend, reminders, clinical decisions, or participant analytics. Browser speech may be processed remotely by its provider. See docs/EVALUATION.md and docs/MAINTENANCE.md. Full multilingual interface, generative AI, and formal clinical/participant validation remain separate future work.

## Version 3.0
Redesigned responsive interface with editorial layout, illustrated identity, paginated resource cards and dedicated Mira workspace. Mira supports guided navigation, optional browser-hosted generative resource selection and an undeployed private Cloudflare pilot. See [Naviboa AI architecture](docs/MIRA.md). No medical answer generation or clinical validation. 

## Version 3.1
Private pilot of AI-written resource summaries (Worker calls Claude; not deployed by default; see docs/MIRA.md). Voice input and read aloud rebuilt with consent box, specific error messages and fallbacks. Emergency wording broadened. Tests: `node tests/worker.test.mjs`, `python tests/voice_test.py`.

## Version 3.2 — Naviboa branding
Naviboa Hub (formerly MemoryBridge Hub) and Naviboa AI (formerly Mira) are the working public names. Tagline: **Guiding care. Connecting lives.** Naviboa is coined from navigation and inspiration from Akan *Boafo* (helper/supporter). This rebrand preserves the v3.1 functionality, data, daily crawling schedule, existing GitHub Pages URL, and technical identifiers for compatibility. Existing worker name and legacy document/test paths are intentional. Trademark clearance and domain registration are pending; no registration is claimed. See [brand transition](docs/BRAND.md).

## Version 4.0 candidate
Task-oriented four-view frontend with topic counts, compact single-column resource cards, optional additional filters, session-only comfort controls, and selectable speaking speeds. Daily crawler, resource database and AI backend remain unchanged. Human-reviewed and trusted-source filters are opt-in to avoid hiding all unreviewed entries. No clinical validation is implied. Review the pull request and validation checks before merging.

## Version 4.1 — Resource quality and research readiness
A separate human-reviewed ledger (`data/reviews.json`) controls review badges and visibility. The daily crawler cannot grant approval or edit reviewer records. `scripts/quality.py` publishes review status, metadata metrics and the top-50 manual queue in `data/quality-index.json`, `data/quality-report.json`, and `data/review-queue.json`. A failed quality audit blocks deployment. The interface hides explicitly excluded or correction-requested entries, while leaving clearly labeled unreviewed resources available. See [resource review protocol](docs/RESOURCE_REVIEW.md). The initial ledger is empty: no content has been clinically validated or human-approved.

Reviewer commands:

```bash
python scripts/review_resource.py queue --limit 20
python scripts/review_resource.py import --file my-review.json
python scripts/quality.py --write
python -m unittest discover -s tests
```

## Purple visual identity
Naviboa has a violet/lavender and warm-gold palette separate from Spectrum Hub. The compass remains an original mark. Purple refers to the broader Alzheimer's awareness tradition; no Alzheimer's Association affiliation or endorsement is claimed. Comfort themes: Lavender, Soft Pearl, Midnight Plum (legacy theme values unchanged for compatibility). The daily crawler, AI and review pipeline remain unchanged.

## Version 4.2 — Reviewer workspace and authenticated GitHub intake
The purple [Reviewer workspace](review.html) presents the prioritized 50-link queue and full directory with an eight-item evidence checklist and an approval/correction/exclusion decision. Reviewers inspect the original source before they submit. The public reviewer page **does not accept passwords or personal access tokens**; it generates a prefilled GitHub issue. GitHub then verifies that the issue author has repository write/maintain/admin permission, validates the record and opens a proposal pull request for human inspection and merge. No resource changes status until a maintainer merges the PR. The page, GitHub issue and repository are public; do not include patient/private information. See [reviewer dashboard operations](docs/REVIEWER_DASHBOARD.md).

The workflow requires GitHub Actions to have write access and to be allowed to create pull requests. Enable required independent reviews on the main branch before relying on the process for production governance. Bot-created PRs may not automatically trigger normal PR checks; the intake workflow runs schema, unit and quality tests and the Pages workflow validates again upon merge. No clinical certification is implied.

## Administrator access update
The Naviboa reviewer dashboard is **not on the public GitHub Pages site**. The public `review.html` path shows a restricted-access notice. Administrators may run `admin/review.html` locally (see [admin instructions](admin/README.md)). An owner-only GitHub Actions gate validates submitted review issues before opening a PR. The static GitHub Pages deployment does not implement login; a remotely accessible admin portal requires real server-side authentication and a private hosting/backend configuration. The GitHub repository and issue records remain public.

## Version 4.3 — automatic daily *listing* checks
Naviboa now automatically applies conservative publisher, recent-link and metadata checks after each daily crawl, with no admin clicks required. Low-risk entries passing these rules receive the distinct label **Automated listing check**. Other entries remain pending for a human review, while recorded human decisions always take precedence. **Automated listing checks are not clinical verification and never become `Human reviewed`.** The admin reviewer dashboard stays off public GitHub Pages. See [review protocol](docs/RESOURCE_REVIEW.md).

## Secure private administrator portal (v4.4)
The complete purple reviewer workspace is prepared for an **Access-protected Cloudflare Worker**, separate from the public GitHub Pages website. It validates the signed Cloudflare Access JWT and exact administrator email before serving *any* dashboard asset, including the private queue snapshot. **No public URL is activated until the owner connects Cloudflare and configures the Access application, audience, team domain and admin email.** A custom domain is not necessary; the protected `workers.dev` URL can be bookmarked on iPhone or desktop after setup. See [one-time deployment instructions](private-admin/README.md). The public GitHub review issues and ledger are still public and must never contain sensitive data. Routine daily auto-screening continues independently.
