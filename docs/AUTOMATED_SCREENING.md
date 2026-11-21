# Daily automatic directory checks (Naviboa v4.3)

The previously scheduled **Refresh dementia resources** GitHub workflow runs at 15:23 UTC each day. It crawls permitted public publisher pages, checks a subset of resource links, then runs `scripts/quality.py --write`. That action also runs conservative `scripts/auto_screen.py` on every current directory entry and publishes updated automated-check results, with no administrator interaction. The repository does **not** auto-generate or forge a human-reviewed record.

## Definition of the automatic badge

**Automated listing check** means only:
- The URL is HTTPS, is not a login or shopping page, and has exactly the configured hostname.
- The directory's publisher name and source category match an explicit publisher allowlist in `data/auto-screen-policy.json`. Publisher information remains based on crawler metadata; no third-party accreditation is implied.
- The crawler recorded a valid response for the link within the last seven days.
- The title, description, language tag and topics are present and meet conservative screening criteria.
- The record is not classified into medical/legally sensitive topics and has no obvious high-risk cure-claim phrase in the listing metadata.

**It does NOT mean** clinical verification, medically safe, content human-reviewed, accessibility audited, independently endorsed, or appropriate for a particular patient. The plain badge appears only if all automatic checks pass. It expires after seven days without a fresh successful link check. The manual `Human reviewed` badge is governed *only* by `data/reviews.json`.

## Automatic review outcomes and daily flow

| Outcome | Meaning | Public status |
| --- | --- | --- |
| Auto-screened | Metadata, publisher, topic and current link passed conservative rules | Automated listing check |
| Human-reviewed | Eight criteria checked and recorded by an authenticated human | Human reviewed |
| Needs correction / Excluded | Human reviewer recorded an explicit problem or exclusion | Hidden from public directory/AI |
| Review pending | Auto-screen could not establish all metadata criteria, or sensitive topic | Link checked / Review pending |

The automatic screening queue is calculated as the **resources not already human reviewed, excluded, or auto screened**. The private queue contains at most 50 prioritized items; it is not deployed to the public Pages artifact. The aggregate public quality report shows `automated_screened` and `manual_screen_pending` without showing private administrative notes.

## Changing the policy
The policy is intentionally explicit. The administrator may add a publisher by committing the exact hostname, organization name and kind to `data/auto-screen-policy.json` after an independent source check. Do not add a blanket domain suffix such as all .org sites, and do not allow automatic medical-topic approvals. All changes run the unit/browser/AI Worker checks in pull requests.

Run `python scripts/quality.py --write` to regenerate the reports locally. No secret API keys or paid LLM service is required. GitHub Actions may delay or skip a scheduled run; check the workflow's history if you need a strict operational guarantee or alerting.

## Administration and safety
Keep the reviewer dashboard off GitHub Pages. Human decisions, authenticated reviews, and approvals must follow the administrator-only route. If the automated directory badge ever suggests medical validation, revert it. Validate any change in the source policy separately from the routine daily crawl.
