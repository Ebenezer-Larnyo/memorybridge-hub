# Cloudflare Worker administrative portal — quick deployment

**Status:** Code prepared in GitHub; activation requires the repository owner's Cloudflare login and single-email Access policy.

Use the [full setup and security checklist](../private-admin/README.md).

The public site must **not** link to this portal, and GitHub Pages must never copy `private-admin/dist` or the operational review queue. The private portal checks Cloudflare Access JWT signatures, the application audience, the issuer, and the single authorized administrator email on the server for **every** asset.

Do not use a client-side password, a secret URL, a public Cloudflare Pages deployment, or a GitHub token embedded in JavaScript. Existing review issues and audit notes are public on GitHub; do not submit private data.

After you configure and test the portal URL, bookmark it on your phone. The GitHub source does not contain the owner's private email address and cannot determine it without Cloudflare setup.
