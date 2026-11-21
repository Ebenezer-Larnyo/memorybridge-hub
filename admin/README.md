# Naviboa private-admin operation (local-only interim)

The production GitHub Pages website is **public** and cannot serve an authenticated admin page by itself. The public review.html address shows only a restriction notice, and its actual dashboard JavaScript/CSS plus the review queue are excluded from the Pages deployment.

Run the administrator workspace **on your own computer only**:

1. Clone the Naviboa repository to a computer under your control.
2. From the repository root, run `python -m http.server 8765 --bind 127.0.0.1`.
3. Open `http://127.0.0.1:8765/admin/review.html` on that same computer. Do not bind the web server to 0.0.0.0 or publicly expose port 8765.
4. Inspect a source, complete all eight checklist items, and select a decision.
5. The current workflow opens a **public GitHub issue**. Only the repository owner can have it processed; the issue and its notes remain public. Do not submit confidential or patient information.

**Important distinction:** local-only hosting controls access to the running interface, not the source code. The repository is public; the `admin/` files and queue can still be read in GitHub source/history. To restrict the source, queue and review records themselves, migrate them to a separate private repository or an authenticated backend.

**For convenient remote admin access:** deploy the admin UI and private data to an access-controlled service (e.g. Cloudflare Access) with server-verified sign-in, an admin allowlist, secure session cookies, and server-side authorization for all review API actions. Do not use a client-side password or hidden link. This requires account/domain access and authentication configuration and has not been set up.

Daily resource discovery, public QA counters, and Naviboa AI are unaffected. Keep the public site free of links to the admin dashboard.

## Online access option (v4.4)
For online phone/computer access without running a localhost server, a new [Cloudflare Access-protected portal](../private-admin/README.md) is ready to connect to the owner's Cloudflare account. It uses the same reviewer interface but serves it through a JWT-verifying Worker that checks a single administrator email. **It is not yet deployed or activated on Cloudflare.** Keep the local-only instructions above as a fallback. Do not copy the admin UI back into public GitHub Pages.
