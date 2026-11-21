# Naviboa Hub v4.2 — admin-only reviewer workspace (local interim)

## What is implemented
A reviewer interface at `admin/review.html` that is **not deployed to the public site**, styled in Naviboa purple and lavender. It reads the published prioritized review queue, full directory and sanitized review index (all public). Users can search, select a source, open its original URL, complete all eight quality checks, document evidence and request one of three decisions: approve, needs correction or exclude.

**No human approval is automatic.** The dashboard generates a prefilled GitHub issue. The reviewer then signs in to GitHub and submits it. A GitHub Actions job checks that the issue author has repository `write`, `maintain` or `admin` permission; extracts a strictly structured JSON body; derives the pseudonymous reviewer ID from the GitHub user; validates all eight criteria; checks URL membership in the current directory; and opens a proposed ledger update in a GitHub pull request. The GitHub workflow runs quality and unit tests before creating that PR. A human project maintainer must inspect and merge it. When merged, the daily quality workflow regenerates the public review badges and directory visibility.

## Reviewer instructions
1. On an administrator-controlled computer, start `python -m http.server 8765 --bind 127.0.0.1` from the repository root, then open `http://127.0.0.1:8765/admin/review.html`. The public `review.html` path shows only a restricted-access notice.
2. Browse the top 50 priority entries or select **Entire directory** and search by title, publisher or topic.
3. Select a resource, open the **original source**, and inspect the actual page. Do not rely only on the summary or on the fact that the URL opened.
4. For each of the eight criteria, choose Pass, Concern or Not applicable. **Approvals require eight passes**; correction requests need at least one Concern. Explain any Not applicable result in notes.
5. Enter an HTTPS evidence URL, 30–1200 characters of factual notes and a decision. Check the declaration that no confidential information is present.
6. Choose **Continue to GitHub sign-in**. A new browser tab opens a prefilled review issue. Sign in to GitHub and **click Submit new issue**. Merely opening the tab does not submit or approve the review.
7. If you are the GitHub repository owner with admin permission, the repository Actions workflow processes the issue and creates a PR. Other issue authors are ignored or rejected by the owner-only workflow. A maintainer then independently reviews and merges the PR.
8. After merge and successful deployment, the resource badge changes. Approved directory entries still do **not** represent clinical approval or individualized advice.

The **Download review JSON** control is an offline/export alternative; it never changes GitHub or the public website. The existing Python import script remains available to a maintainer with a local checkout.

## Repository setup required
- GitHub Issues must remain enabled.
- In GitHub **Settings > Actions > General > Workflow permissions**, permit read/write workflow token permissions and allow **GitHub Actions to create pull requests**. Repository or organization policy may prevent this; if so the automated intake will fail rather than bypass permission checks. A maintainer can use the existing offline import/PR path.
- Only the repository owner can process reviewer submissions through this route. The workflow checks the issue author against the repository owner and requires admin permission. Do not add other collaborators unless a future explicit admin policy requires it.
- Protect the `main` branch with a rule requiring at least one **independent** approving PR review, preferably preventing self-approval and direct pushes for changes to the review ledger. This is a repository policy setting, **not** enforced by frontend checkboxes.
- Confirm GitHub Pages includes only the restricted notice at `review.html`, **does not include** dashboard JavaScript, CSS, `admin/`, `data/reviews.json`, or the priority `data/review-queue.json`. The sanitized public quality-index and aggregate quality-report may remain public.

## Privacy and threat boundaries
- The admin dashboard is **local-only**, not an authenticated web login. The repository source, issue text, issue author and repository review notes remain **public**. They are not private research records. Do not enter medical identifiers, patient stories, participant interviews, reviewer emails or confidential evidence. The access gate controls who can advance a submission, **not who can view the dashboard**.
- GitHub sign-in happens on `github.com`; Naviboa never receives the user's password or token. GitHub authenticates issue creation; Actions then checks write permission server-side before accepting the JSON.
- Reviews are derived from the issue author and created-at date, rather than user-editable identity or timestamp fields. URL matching and review-schema validations reject unknown sources and unsupported approvals.
- The automation creates only a proposed PR and never merges. A human second look is essential. Without branch protection there is no technical two-person guarantee.
- Note GitHub Actions bot-created PRs can fail to trigger `pull_request` workflows due to GitHub's recursion prevention rules. Intake runs Python/unit/quality checks and the deployment job runs its own checks when approved changes merge.
- Review is a directory quality process, **not a clinical certification**. Conduct usability evaluation with appropriate participants and ethics determination before claiming validated accessibility or clinical benefit.

## Test commands
Run from the repository root:

    python -m unittest discover -s tests
    node --check review.js
    python -m http.server 8000
    python tests/reviewer_smoke.py

The reviewer browser test intercepts the GitHub-opening action; it does **not** create a real issue or contact GitHub. Perform an explicit trusted-collaborator issue-to-PR dry run before treating end-to-end intake as operational.

## Immediate access change
The public page was retired in favor of a static "restricted" notice; the real dashboard was moved into `admin/` and excluded from the GitHub Pages deployment. GitHub Pages provides no secure server-side authentication for one path. Do not treat a hidden link or JavaScript password prompt as access control. For a truly web-accessible private dashboard, deploy the administrator frontend and private data behind a server-verified identity gateway (e.g., Cloudflare Access), with a single admin identity allowlist and server-side checks on every write request. Such hosting is not configured in this repository. See [admin/README.md](../admin/README.md).
