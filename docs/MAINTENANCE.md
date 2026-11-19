# Operations and release checklist

- Daily crawl scheduled at 15:23 UTC; manual run is available under Actions > Refresh dementia resources > Run workflow. GitHub schedules can be delayed or disabled on inactive repositories.
- Review crawl-report.json, check failures and source policies, and remove disallowed sources. Use repository issues for public contact (never disclose personal health information).
- Crawler uses HTTPS same-host links, robots restrictions, bounded requests, no redirects, a 2-second minimum delay and honors crawl-delay/request-rate. On 429/503 stop further requests to that host for the run. Candidate rotation helps avoid repeatedly testing the same first links. It does not crawl private forums or store patient posts. It is not exhaustive or a medical verifier. Existing non-seed links are not systematically rechecked; manual audits remain necessary.
- Source-specific terms and permissions require review. New seed URLs are externally identified but not all individually HTTP-tested. New automatically found resources stay unreviewed. Remove incorrect or obsolete entries.
- Deployment runs after a successful crawl or push; check Actions and live page.
- Smoke-test desktop/mobile, keyboard focus, high contrast, large type, region/language search, Mira topic selection, emergency handoff wording, voice availability and consent, simple view and opt-in storage clearing. Test with assistive technologies and people living with dementia before representing accessibility as validated.
- No API keys or custom domain required. No live human chat, ambient monitoring, push reminders, generative AI or medical triage. Speech features are browser-dependent, may use remote processing and require user interaction.
- Spanish guide links are available; the main interface is English. Expand country and language coverage using local partners and professional review.
- Public resource suggestions via GitHub issues are optional; never submit personal health details. 

- Browser smoke test runs in the publishing workflow using Chromium on a mobile-size viewport. It checks filtering, Mira links and urgent-message handling, local storage, simple view, accessibility controls and the Spanish page. It cannot replace human usability testing, voice-device testing or WCAG evaluation. Crawler changes or source-list changes trigger an additional run without changing the daily schedule.
