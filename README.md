# MemoryBridge Hub
Research-informed dementia resource discovery prototype, based on Larnyo, Benyassine and Preece's manuscript, section 5.11. Sister project to Spectrum Hub. US-first with international starter resources. No clinical validation.

## Local use
Run python -m http.server 8000 and open http://localhost:8000. No API key needed.

## Deployment
Settings > Pages > Source > GitHub Actions. Run Publish MemoryBridge Hub. Confirm source policies and project contact before running Refresh dementia resources or enabling scheduled crawling. Review Actions logs and data/crawl-report.json. GitHub may disable scheduled workflows on inactive repositories.

## Crawler
Install requirements.txt and run python scripts/crawl.py. Same-host, robots-aware, rate-limited discovery from selected sources; no private data or forum collection. New entries are unreviewed, and link checks are not clinical verification. Source failures preserve old entries. Review all results manually, and remove outdated or misleading links. Run python -m unittest discover -s tests. Test search, keyboard navigation, mobile layout, and accessibility controls before launch.

## Research
Co-design with people living with dementia, caregivers and clinicians. Evaluate comprehension, task completion, resource quality, accessibility, usefulness and equity. Obtain applicable ethics approval before collecting research data. The manuscript's Reddit sample is caregiver-heavy and not representative; reconcile 664 vs 665 posts before publication. AI companion and daily care tools are future features, not deployed here.
