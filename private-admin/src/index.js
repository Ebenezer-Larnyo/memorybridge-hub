/**
 * Authenticated Naviboa reviewer UI.
 * Cloudflare Access must protect this Worker; this handler independently
 * verifies the signed Access JWT before ANY static asset is served.
 * Fail closed when settings are unset. No public fallback or login bypass.
 */
import { createRemoteJWKSet, jwtVerify } from "jose";

const POLICY_NAME = "Cloudflare Access administrator authentication";
const PERMITTED = new Set([
  "/", "/index.html", "/review.js", "/review.css", "/favicon.svg",
  "/data/resources.json", "/data/review-queue.json", "/data/quality-index.json",
  "/data/quality-report.json"
]);
const KEYS = new Map();

function response(message, status, extra = {}) {
  return new Response(message, {
    status, headers: {
      "Content-Type": "text/plain; charset=utf-8",
      "Cache-Control": "private, no-store, max-age=0",
      "X-Content-Type-Options": "nosniff",
      "X-Frame-Options": "DENY",
      "Referrer-Policy": "no-referrer",
      ...extra
    }
  });
}

export function configFromEnv(env) {
  const team = (env?.TEAM_DOMAIN || "").trim().replace(/\/$/, "");
  const aud = (env?.POLICY_AUD || "").trim();
  const email = (env?.ADMIN_EMAIL || "").trim().toLowerCase();
  let url;
  try { url = new URL(team); } catch { return null; }
  if (url.protocol !== "https:" || !url.hostname.endsWith(".cloudflareaccess.com")
    || url.username || url.password || url.search || url.hash || url.pathname !== "/"
    || url.port || team !== url.origin
    || !/^[A-Za-z0-9_-]{16,128}$/.test(aud)
    || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return null;
  return {team: url.origin, aud, email};
}

async function validateJwt(token, cfg) {
  let jwks = KEYS.get(cfg.team);
  if (!jwks) {
    jwks = createRemoteJWKSet(new URL(cfg.team + "/cdn-cgi/access/certs"));
    KEYS.set(cfg.team, jwks);
  }
  const {payload} = await jwtVerify(token, jwks, {
    issuer: cfg.team,
    audience: cfg.aud,
    algorithms: ["RS256"]
  });
  return payload;
}

/**
 * Optional verifier parameter is only for isolated unit tests. Production
 * default uses jose's cryptographic signature/issuer/AUD/time verification.
 */
export function createHandler(verifyJwt = validateJwt) {
  return {
    async fetch(request, env) {
      const cfg = configFromEnv(env);
      if (!cfg || !env?.ASSETS || typeof env.ASSETS.fetch !== "function") {
        return response("Private portal not configured", 503);
      }

      const url = new URL(request.url);
      if (url.protocol !== "https:") return response("HTTPS required", 403);
      if (request.method !== "GET" && request.method !== "HEAD") {
        return response("Method not allowed", 405, {"Allow":"GET, HEAD"});
      }

      // No JWT, no access. Even an unprotected workers.dev alias denies all.
      const token = request.headers.get("Cf-Access-Jwt-Assertion");
      if (!token || token.length > 16000) return response("Authentication required", 403);

      let claims;
      try {
        claims = await verifyJwt(token, cfg);
      } catch {
        return response("Authentication required", 403);
      }
      if (typeof claims?.email !== "string" ||
          claims.email.trim().toLowerCase() !== cfg.email) {
        return response("Administrator access required", 403);
      }

      // Exact asset allowlist also protects against future accidental file
      // inclusion by the asset-build process or URL path discovery.
      if (!PERMITTED.has(url.pathname)) return response("Not found", 404);
      let asset;
      try {
        const pathname = url.pathname === "/" ? "/index.html" : url.pathname;
        const assetUrl = new URL(request.url);
        assetUrl.pathname = pathname;
        assetUrl.search = "";
        const forwarded = new Request(assetUrl.toString(), {method: "GET"});
        asset = await env.ASSETS.fetch(forwarded);
      } catch {
        return response("Private asset unavailable", 503);
      }

      const headers = new Headers(asset.headers);
      headers.delete("access-control-allow-origin");
      headers.set("Cache-Control", "private, no-store, max-age=0");
      headers.set("X-Content-Type-Options", "nosniff");
      headers.set("X-Frame-Options", "DENY");
      headers.set("Referrer-Policy", "no-referrer");
      headers.set("Permissions-Policy", "camera=(), microphone=(), geolocation=(), payment=()");
      headers.set("X-Robots-Tag", "noindex, nofollow, noarchive");
      headers.set("Content-Security-Policy",
        "default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' data:; " +
        "connect-src 'self'; font-src 'self'; base-uri 'none'; object-src 'none'; " +
        "frame-ancestors 'none'; form-action 'self'; upgrade-insecure-requests");
      return new Response(request.method === "HEAD" ? null : asset.body, {
        status: asset.status, headers
      });
    }
  };
}

export default createHandler();
