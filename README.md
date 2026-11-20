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
