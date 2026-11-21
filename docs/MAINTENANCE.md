# Operations and release checklist

- Daily crawl scheduled at 15:23 UTC (7:23 AM PST / 8:23 AM PDT); manual run is available under Actions > Refresh dementia resources > Run workflow. GitHub schedules can be delayed or disabled on inactive repositories.
- Review crawl-report.json, check failures and source policies, and remove disallowed sources. Use repository issues for public contact (never disclose personal health information).
- Crawler uses HTTPS same-host links, robots restrictions, bounded requests, no redirects, a 2-second minimum delay and honors crawl-delay/request-rate. On 429/503 stop further requests to that host for the run. Candidate rotation helps avoid repeatedly testing the same first links. It does not crawl private forums or store patient posts. It is not exhaustive or a medical verifier. Existing non-seed links are not systematically rechecked; manual audits remain necessary.
- Source-specific terms and permissions require review. New seed URLs are externally identified but not all individually HTTP-tested. New automatically found resources stay unreviewed. Remove incorrect or obsolete entries.
- Deployment runs after a successful crawl or push; check Actions and live page.
- Smoke-test desktop/mobile, keyboard focus, high contrast, large type, region/language search, Naviboa AI topic selection, emergency handoff wording, voice availability and consent, simple view and opt-in storage clearing. Test with assistive technologies and people living with dementia before representing accessibility as validated.
- No API keys or custom domain required for guided mode. The optional cloud AI pilot needs separate configuration. No live human chat, ambient monitoring, push reminders or medical triage. Speech features are browser-dependent, may use remote processing and require user interaction.
- Spanish guide links are available; the main interface is English. Expand country and language coverage using local partners and professional review.
- Public resource suggestions via GitHub issues are optional; never submit personal health details. 

- Browser smoke test runs in the publishing workflow using Chromium on a mobile-size viewport. It checks filtering, Naviboa AI links and urgent-message handling, local storage, simple view, accessibility controls and the Spanish page. It cannot replace human usability testing, voice-device testing or WCAG evaluation. Crawler changes or source-list changes trigger an additional run without changing the daily schedule.

## v4.1 quality operations
- Each daily crawl regenerates `data/quality-index.json`, `data/quality-report.json` and the prioritized 50-entry `data/review-queue.json`. Do not let crawler code edit `data/reviews.json`.
- Inspect the queue and review report weekly; respond to needs_revision/excluded decisions by removing the listing from public results and AI candidate pools. Both are hidden by the frontend.
- Before publishing any human-reviewed label, inspect the source, complete all eight evidence-backed checks, and have an independent reviewer check the approval. A review older than 180 days is shown as due, not currently approved.
- Language tags may be added only from the fetched page's HTML lang attribute (currently en and es) or from documented manual inspection. Never infer approval from language or source category.
- GitHub's pull request workflow regenerates QA artifacts and runs automated tests. The Pages job regenerates artifacts before deployment; an invalid review ledger will stop the build.

## v4.2 reviewer intake operations
- Verify GitHub repository Settings > Actions > General permits workflow write access and Actions-created pull requests.
- The dashboard is restricted to local administrator use at admin/review.html; GitHub Pages must not deploy its scripts/styles or prioritized review queue. Only the repository owner can process submissions. Review issues and proposed ledger changes are public. Never add patient data, confidential sources or reviewer contact details.
- On a valid issue submitted by the GitHub repository owner, the Propose human resource review workflow generates a proposal branch and pull request; a second project reviewer should inspect source evidence and merge manually. Enable a required-review branch-protection rule on main to technically enforce independent review.
- On failures inspect the workflow run. A review is not published until the corresponding PR is merged and Pages deployment succeeds.
- Check the reviewer browser smoke test on narrow phones, desktops and with assistive technologies. The interface's automatic tests do not constitute clinical or accessibility validation.

- Audit each GitHub Pages publish to ensure public `review.html` contains no form, and `review.js`, `review.css`, `admin/`, `data/reviews.json` and `data/review-queue.json` are not in the deployed artifact.
- For remote admin usage, a server-side authenticated service is needed; hiding a public URL is not security.
