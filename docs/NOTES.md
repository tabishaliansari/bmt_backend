# BMT · Notes

Scratchpad for the team: logistics, open questions, links, ideas that are not in scope yet.

## Event

- Venue check-in 08:00–09:00 Fri 20 Nov. Bring government ID, the entry QR code (each member
  accepts their own RSVP email), charged laptops, chargers, extension board, hotspot.
- Day 1: 09:00 intro, 10:00 build starts, 11:30 mentor round 1, 13:30 lunch,
  16:00 tea and mid-day check-in, 18:00 Day 1 wrap-up, **23:00 submission opens**.
- Day 2: **09:00 submission closes (no extension)**, 10:00–13:00 mentor evaluation,
  14:00–17:30 startup showcase, 17:30 jury, 18:00 results.
- Antigravity credits: given to the team leader (Tabish) on request during Day 1.
- Google Cloud credits: redeem on a billing account with a card. Valid 24 h. Redeem ~10:00 Day 1.
- After Pune: regional showcase Mumbai 25 Nov, grand finale Google Bengaluru 2 Dec.
  Top 10 teams: USD 5,000 cash + USD 5,000 Google AI and Cloud credits each.

## Judging criteria

1. Founder profile 2. Product potential 3. Market viability
4. Technical architecture 5. Use of Google AI and Google Cloud

## Open questions

- [ ] Does the venue stay open after 18:00 on Day 1, or do we build remotely? Ask at the intro.
- [ ] What exactly does the submission need (repo, live URL, video, deck)? Ask at the intro.
- [ ] Which Gemini models are available on Vertex AI in `asia-south1`?

## Links

- Event site: https://startupbuildathon.com/
- Cloud credits: https://g.dev/credits/startup-buildathon-india-2026
- Virtual session slides: https://goo.gle/data-ai-biz
- Mock UI (live): GitHub Pages URL of the mock-ui repo
- Figma: "BMT · App Design"

## Q&A prep

- **How does Ramp pay Indian editors?** Ramp Bill Pay supports international transfers in
  local currency, but Ramp serves US-registered businesses. Plan: a US entity for BMT and a
  partnership conversation with Ramp. For the buildathon, the payout is simulated and labelled.
- **Why not Upwork or Fiverr?** Video-only focus, verified credits instead of self-uploaded
  portfolios, Gemini in the workflow (brief, review), and a two-sided guarantee.
- **What stops someone from claiming a fake credit?** Channel confirmation plus Gemini
  cross-checking the editor's export against the published video (Proof Engine, roadmap).
- **What was built before the event?** The UI prototype and the local happy path. Google Cloud
  integration and deployment were built on-site. Say this plainly.

## Parking lot (not in scope)

- Taste Match at scale with Vector Search
- Proof Engine with the YouTube Data API
- Gemini Live voice briefs, Nano Banana thumbnails, Lyria music
- Editor onboarding, chat, notifications, auth

## Security TODOs (before any public / production use)

Found 2026-11-20 by a local security pass (live probing of `localhost:8080` + code review).
The gstack `/cso` helper couldn't run here (needs Docker + a git snapshot it was denied), so this
was done by hand. Verified **safe**: SQL injection, path traversal, mass assignment (client can't
set price/status/payout), secret logging, CORS. Functional happy path passed 23/23 (`smoke.sh`).

Findings 1, 2 and 5 share one root cause: **there is no auth or per-user ownership** (listed as
out of scope in `PRD.md`). Fine for the buildathon demo; must be fixed before the app is public,
including the Cloud Run URL if it is shared.

- [ ] **High — No authz + enumerable IDs.** `GET /orders` returns every order unauthenticated;
  order ids are sequential (`BMT-<2481+count>`, `orders.py`), so they can be walked. Exposes each
  client's note, brief, totals and payout. Fix: auth + ownership filter on orders, briefs, uploads.
- [ ] **High — Unauthenticated, unthrottled paid Gemini calls.** `POST /briefs` and
  `POST /orders/{id}/review` each make a live Gemini call with no auth or rate limit → cost-DoS
  once a key is set. Fix: auth + per-IP/user rate limit on the AI endpoints.
- [ ] **Med — Upload size checked only after the full body is buffered** (`uploads.py`); no
  streaming cap, and if `file.size` is `None` the check is skipped. `media.py` also reads the whole
  file into memory. Fix: a streaming size limit (reverse proxy or middleware).
- [ ] **Med — Config disclosure in errors.** AI errors return verbatim to the client, naming env
  vars and `backend/.env`; the 422 handler echoes submitted values. Fix: generic client message,
  log the detail server-side. (No stack traces leak.)
- [ ] **Low — `PUT /briefs/{id}` overwritable by anyone** (same no-auth class; brief ids are
  random so less enumerable; placed orders snapshot the brief, so they're unaffected).
- [ ] **Low — No security headers** (no `X-Frame-Options`/CSP → clickjackable, no nosniff).
  Fix: a small headers middleware.
- [ ] **Low — `OrderRequest.addons` is unbounded** (`models.py`); add a `max_length`.
