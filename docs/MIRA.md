# Naviboa AI hybrid architecture

Formerly Mira. Legacy file paths, test environment variable names, and Worker service name are retained for compatibility.

Naviboa AI is a resource navigator, not a diagnostic or treatment tool. Guided mode is the default. Emergency keyword routing and deterministic directory filtering run first; they are incomplete heuristics, not medical triage. Optional generative models select up to four IDs from a bounded candidate list; the private cloud pilot can also produce bounded summaries, not medical answers. Invalid results, timeouts and lack of support fall back to guided navigation. Only existing directory links are rendered. This is AI-assisted navigation, not clinical RAG over article contents; the model receives titles and metadata, not clinical source text.

## On-device mode
Compatible browsers expose LanguageModel. The browser may need to download a model and user interaction. No key is required. Support varies substantially, and the feature is not verified on iOS. Select Hybrid on-device AI and type a non-identifying question. A successful response explicitly labels AI-assisted selection. Guided mode remains available.

## Private cloud pilot
The included Cloudflare Worker is not deployed. It requires an administrator's Cloudflare account, Workers AI permission and a supported model. From ai-worker, use npx wrangler login, then npx wrangler secret put PILOT_TOKEN (generate a long random token; never put it in the repository), and npx wrangler deploy. Set AI_ENDPOINT in app.js to the resulting HTTPS URL and commit. Use the pilot code in Naviboa AI's session-only field; do not share the token publicly. Keep the free plan or set budget/usage controls; pricing and model access vary. The per-location rate limiter is not an absolute global spending cap. CORS is not authorization; the worker also checks the token and rate limit. Review provider data terms, privacy and ethics before pilot use. Do not enable public anonymous access without abuse controls, review and a budget. No model is called from the cloud until configuration and explicit consent. No API keys are held in the browser or committed.

## Safety and evaluation
Test emergency phrases, ambiguous requests, adversarial prompts, out-of-range IDs, offline/device failure, consent and source relevance. Do not claim clinical safety from these controls alone. All links, including AI-selected ones, need human quality review. For richer conversational answers, build a reviewed evidence corpus and validate citation accuracy, disclosure, medical boundaries and adversarial robustness before enabling any free-form generation.

## Generative answers (private pilot, v3.1)
In the private pilot, Naviboa AI can write a short summary of why the selected directory entries fit a question. The Worker (`ai-worker/index.mjs`) calls the Anthropic API; the key lives only as a Cloudflare secret.

Controls: the page and the Worker both route emergency phrases away from the model; the model sees only the question and candidate metadata (title, organization, a short description, topics) and must choose IDs from that list; the Worker discards invalid IDs, replies that contain web addresses, dosing, treatment-change or diagnosis wording, and falls back to links only. The reply is shown as AI-written, with a medical disclaimer, and Guided mode remains available. Nothing is logged by the Worker.

Setup (administrator): `cd ai-worker`, then `npx wrangler login`, `npx wrangler secret put PILOT_TOKEN`, `npx wrangler secret put ANTHROPIC_API_KEY`, `npx wrangler deploy`. In the Anthropic console, set a monthly spend limit on the key. Put the Worker URL in `AI_ENDPOINT` in `app.js` and commit. Share the pilot code privately with testers.

Before wider use: run `MIRA_URL=... PILOT_TOKEN=... node tests/eval_live.mjs`, have a clinician and a caregiver read every reply in `tests/eval_results.json`, expand `tests/mira_eval_cases.json`, review the provider's data terms, and obtain ethics approval before keeping any transcripts. Automated tests (`node tests/worker.test.mjs`, `python tests/voice_test.py`) check mechanics, not clinical safety. The per-pilot rate limiter is global, not per person; for any public version add Cloudflare Turnstile and a daily cap.

## Voice features
Voice input uses the browser's SpeechRecognition and needs the consent box ticked. It is unavailable in many in-app browsers, Firefox and some iPhone browsers; the page says so and suggests the phone keyboard's microphone key. Read aloud uses speechSynthesis, speaks sentence by sentence, and tells the user if the browser did not start audio.
