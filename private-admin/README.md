# Naviboa secure online administrator portal (v4.4)

This is a **deployment-ready** private web application, NOT an active online URL until the repository owner configures a Cloudflare account and Access policy. The public Naviboa Hub stays on GitHub Pages; its old /review.html remains only a restriction notice.

## What this protects
- The reviewer interface, styles, scripts and a snapshot of the review queue are served by a **separate Cloudflare Worker**.
- Every request, including JS, CSS and JSON assets, runs through the Worker first (Wrangler asset option `run_worker_first=true`). The Worker refuses to serve assets unless a **Cloudflare Access-signed JWT** has a valid signature, issuer and application AUD, and its verified email exactly matches `ADMIN_EMAIL`. Missing settings fail closed (503), missing or invalid tokens return 403; even a publicly routable workers.dev URL cannot bypass these checks.
- Cloudflare Access provides the actual interactive login (such as email one-time passcode); **do not add a password form or store a password in GitHub**.
- The Worker allows only exact known asset routes and sets no-store, noindex, CSP, frame-blocking and no-CORS headers. Nothing is deployed on a public /admin path of GitHub Pages.
- The existing GitHub issue/PR workflow still checks the GitHub issue author is the **repository owner** and produces a proposal, not an automatic merge.

## One-time owner setup (Cloudflare)
1. Sign in or create an account at https://dash.cloudflare.com/ and enable Zero Trust for the account.
2. In **Workers & Pages**, create a **Worker** by connecting its GitHub repository:
   `Ebenezer-Larnyo/memorybridge-hub`. Authorize Cloudflare's GitHub integration **in the Cloudflare UI**. Avoid giving credentials or tokens to people or putting them in chat.
3. Choose worker name **naviboa-admin-portal** (must match wrangler.jsonc). Select production branch **main**, and set the Worker project's **root directory** to **private-admin**. Use build command `npm install --no-audit --no-fund && npm run build` and deploy command `npx wrangler deploy`. Cloudflare's Git integration can redeploy after future commits.
4. First deploy may return **503 Private portal not configured**. This is the expected fail-closed behavior, not a public site. Do not lower the security checks.
5. Open Workers & Pages → **naviboa-admin-portal** → **Access** → **Protect this Worker behind Access**, select **All traffic** (production AND preview routes), and configure an allow policy restricted to **your exact email address**, not an entire email domain. If using email one-time passcodes, select the email OTP login method in Cloudflare Zero Trust. Remove any broad Everyone or domain-wide Allow policies. For the account-wide Access option, ensure the application still has exactly one authorized administrator.
6. Under Zero Trust → Access → Applications → your Worker, copy the **Application Audience (AUD) Tag**. Get your team domain, e.g. `https://YOUR-TEAM.cloudflareaccess.com`. Cloudflare docs: https://developers.cloudflare.com/cloudflare-one/access-controls/applications/http-apps/authorization-cookie/validating-json/
7. Under Workers & Pages → naviboa-admin-portal → Settings → Variables and Secrets, set three **server-side values** (type Secret is acceptable):
   - `TEAM_DOMAIN`: the full team URL `https://YOUR-TEAM.cloudflareaccess.com` with **no trailing slash**
   - `POLICY_AUD`: the application's exact AUD tag
   - `ADMIN_EMAIL`: the **same single email** allowed in the Cloudflare Access policy (e.g. `you@example.org`; replace with your own private address)
   Do **not** put any of these values into source code, GitHub issues, or public deployment instructions. Configure them for each deployment environment if you enable previews.
8. Redeploy or confirm the Worker has received those bindings. Use Cloudflare's assigned `https://naviboa-admin-portal.YOUR-SUBDOMAIN.workers.dev/` address; a custom domain is **not required** to get started. Bookmark that URL on your phone. Login should appear before any dashboard data.
9. **Verify access control** before use: open the URL in a private/incognito browser while signed out and check that Cloudflare asks you to authenticate. Authenticate with your email and confirm the dashboard loads. Test a different email and confirm refusal. Verify `/data/review-queue.json` and `/review.js` cannot be retrieved anonymously. Verify `/data/reviews.json` is 404 even while signed in. If Cloudflare changes an Access policy, the Worker still validates the application AUD and exact admin email.
10. To submit a **human** resource review, inspect the actual source, complete the eight criteria and select **Continue to GitHub sign-in**. This opens a prefilled GitHub issue: you must submit that issue while signed in as the repository owner. The GitHub workflow validates it and creates a pull request; an authorized maintainer still merges it. Review issues and notes remain **public on GitHub**. Do not include sensitive patient or confidential reviewer information.

If you cannot find the GitHub integration or are unsure of a dashboard option, check:
- https://developers.cloudflare.com/workers/ci-cd/builds/git-integration/
- https://developers.cloudflare.com/workers/configuration/cloudflare-access/
- https://developers.cloudflare.com/workers/static-assets/routing/worker-script/

## Keeping data fresh
The site already has a daily GitHub crawler. The private Worker build packages the **current repository snapshot** of `data/resources.json`, `data/review-queue.json`, `data/quality-index.json` and `data/quality-report.json`. When Cloudflare's Git integration rebuilds the Worker after a data commit, the queue updates. If the Cloudflare integration skips a build or the GitHub crawl does not commit a change, the private portal keeps its last deployed snapshot; it does **not** poll the crawler. Monitor both pipelines.

## Privacy and limitations
- The public GitHub repository already contains `data/review-queue.json` and the human ledger in Git history. **This app restricts dashboard access on Cloudflare; it does not retroactively make public GitHub source or past review notes private.** A fully confidential workflow requires migrating those records to a private repository/database and avoiding public GitHub issues.
- Cloudflare Access may have plan-specific limits, but this prototype is designed to use free-tier hosting and no paid AI. Cloudflare account registration and Access setup still require the owner's action.
- No clinical validation is implied. Human/clinical reviews are never fabricated. The daily rules-based listing screen is distinct from human approval.
- Only deploy from a trusted branch; audit changes to Worker code and policy. Do not weaken `run_worker_first` or expose public asset aliases.
- This setup has **not been activated on Cloudflare** until you complete the above steps. A successful GitHub build is not evidence that a protected live URL exists.

## Local tests

From the repository root (Node.js 22+):

    cd private-admin
    npm install --no-audit --no-fund
    npm run check

This verifies the bundle and tests an unauthorized client cannot retrieve the reviewer interface, and an authorized email still cannot fetch the human ledger.
