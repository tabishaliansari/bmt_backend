# BMT · API contract

Base path: `/api/v1`. JSON in and out, except uploads (multipart). Errors return
`{"error": {"code": "string", "message": "human readable"}}` with a 4xx/5xx status.
Money: integers in the smallest unit is overkill for the demo; use numbers with 2 decimals,
and always say the currency (`_usd`, `_inr`).

The frontend calls these **only** through `frontend/js/api.js`, which converts the snake_case
JSON here into the shapes the screens use. `BMT_USE_MOCKS` (turned on by adding `?mocks=1` to
the URL, before the `#`) serves the same functions from mock data with canned Gemini results,
as the demo fallback.

Common errors: `401` not signed in, `404` unknown id **or someone else's record**, `409` action
not allowed in the order's current status, `413` file too large, `415` not a video, `422`
invalid input (or text blocked by Gemma screening), `429` hourly AI limit reached, `502
ai_error` Gemini failed, `503 ai_unavailable` AI not configured on the server, `504
ai_timeout` Gemini took longer than `AI_TIMEOUT_SEC`.

## Auth

Firebase Authentication with Google sign-in. Send the Firebase ID token on every private call:
`Authorization: Bearer <idToken>`. Public: `/healthz`, `/config`, `/editors`, `/editors/{id}`,
`/addons`, and signed media links. Everything else needs a token and only ever returns the
caller's own uploads, briefs and orders (anyone else's id is a `404`). With `AUTH=off` (local
development only) every request is one fixed local user. Gemini calls are limited per user
(`AI_RATE_LIMIT_PER_HOUR`, default 30).

### `GET /config`
What the browser needs to start sign-in (all public by design):
```json
{ "auth": "firebase", "firebase": { "apiKey": "...", "authDomain": "x.firebaseapp.com", "projectId": "x" },
  "authEmulator": "http://127.0.0.1:9099", "features": { "thumbnail": true, "screening": true } }
```

---

## Uploads

### `POST /uploads`
Multipart: `file` (video), `kind` = `raw` | `cut`.
```json
{ "id": "up_8f2c9a1b3c4d5e6f", "kind": "raw", "filename": "clip1.mp4", "mime": "video/mp4", "size": 12485123 }
```
Status `201`. Reject files over `MAX_UPLOAD_MB` (default 50; keep under 32 on Cloud Run) with
`413`, non-video files with `415`. Size is measured from the received bytes.

### `GET /uploads/{id}/url`
`{ "url": "/api/v1/uploads/{id}/content?exp=...&sig=..." }`: a short-lived signed link (1 hour)
for `<video>`/`<img>`, which can't send the auth header. Owner only.

### `GET /uploads/{id}/content?exp=&sig=`
Streams the file (supports `Range`, so the review player can seek). `403` without a valid link.

---

## Briefs (Brief Builder)

### `POST /briefs`
```json
{ "upload_ids": ["up_8f2c", "up_91aa"], "client_note": "Reel for my cafe launch, fun and fast, 30s" }
```
Response `201` (can take 10–60 s; frontend shows progress). 1–3 upload ids, all of kind `raw`:
```json
{
  "id": "br_3d10",
  "upload_ids": ["up_8f2c", "up_91aa"],
  "client_note": "Reel for my cafe launch, fun and fast, 30s",
  "created_at": "2026-11-20T10:40:00Z",
  "screened_by": "gemma-4-26b-a4b-it",
  "thumbnail_upload_id": null,
  "result": {
    "title": "Cafe launch reel",
    "format": "reel",
    "target_length_sec": 30,
    "hook_idea": "Open on the first pour in slow motion, cut on the beat",
    "best_moments": [
      { "upload_id": "up_8f2c", "start": "00:04", "end": "00:09", "why": "Latte art close-up, strong hook" }
    ],
    "style_notes": "Warm grade, quick cuts, bold captions",
    "must_include": ["Cafe name", "Opening date", "Location"],
    "questions_for_client": ["Do you have a logo file?"],
    "recommended_package": { "category": "reels", "package_title": "Instagram Reel", "reason": "Under 60s, captions, fast turnaround" }
  }
}
```
`format` is one of `reel | shorts | youtube | podcast_clips | ad | other`.
`recommended_package.category` is one of `reels | youtube | podcasts | ads | weddings | gaming`.
Before Gemini runs, **Gemma** (`GEMINI_SCREEN_MODEL`) screens `client_note`; blocked text is a
`422` with a reason the client can act on. `screened_by` names the Gemma model (null when
screening is off or Gemma was unavailable; screening fails open).

### `GET /briefs/{id}`
Returns the same object.

### `PUT /briefs/{id}`
`{ "result": { ...the full result... } }` → the updated brief. The client edits the brief
inline before ordering.

### `POST /briefs/{id}/thumbnail`
**Nano Banana** (`GEMINI_IMAGE_MODEL`) drafts a thumbnail concept from the brief's title, hook
and style (9:16 for reels/shorts, 16:9 otherwise). Stored as an upload of kind `thumb`; returns
the brief with `thumbnail_upload_id` set (get a link via `GET /uploads/{id}/url`). Counts
against the AI limit. Orders copy `thumbnail_upload_id` from the brief.

---

## Editors

### `GET /editors?category=reels&q=`
List of editors (same shape as `mock-ui/js/api.js`), each with `packages[]`.

### `GET /editors/{id}`
One editor with `packages[]`, `credit_list[]`, `reviews[]`.

### `GET /editors/recommended?brief_id=br_3d10`
Editors whose categories match the brief's `recommended_package.category`: `featured` first
(the demo founder profile), then best rated. Needs sign-in (the brief is private). (Taste Match
later replaces this ranking.)

### `GET /addons`
Add-ons and the rush fee, priced in both currencies, so the UI shows what the server charges.
```json
{ "addons": [{ "id": "captions", "icon": "cc", "title": "Animated captions", "sub": "Word-by-word, on-brand", "price_inr": 199, "price_usd": 2.0 }],
  "rush_fee_inr": 300, "rush_fee_usd": 3.59 }
```

---

## Orders

### `POST /orders`
```json
{ "editor_id": "riya", "package_id": "reel", "brief_id": "br_3d10", "addons": ["captions"], "rush": false, "note": "" }
```
`brief_id` and `note` are optional. Response `201`, the full order:
```json
{
  "id": "BMT-7KQ2XDMA", "editor_id": "mustafa", "package_id": "reel", "brief_id": "br_3d10",
  "brief": { "...": "copy of the brief result at order time" }, "thumbnail_upload_id": null,
  "title": "Instagram Reel", "g": 2, "addons": ["captions"], "rush": false, "note": "",
  "total_usd": 14.99, "total_inr": 1198, "status": "funded", "revisions_left": 2,
  "due_at": "2026-11-22T10:42:00Z", "cut_upload_id": null, "review": null,
  "client_notes": [], "payout": null, "created_at": "2026-11-20T10:42:00Z",
  "timeline": [{ "status": "funded", "at": "2026-11-20T10:42:00Z", "label": "Payment held safely" }]
}
```
Order ids are random (`BMT-` + 8 characters), so they can't be guessed or walked.
The server computes both totals. Never trust a price from the client (any price field sent is ignored).
Status moves `funded → review → approved`, with `review → in_progress → review` for changes.

### `GET /orders` and `GET /orders/{id}`
Order objects, newest first. Include the brief result and review if present.

### `POST /orders/{id}/deliver`
`{ "cut_upload_id": "up_c001" }` (an upload of kind `cut`) → order with `status: "review"`.
Allowed from `funded` or `in_progress`. Clears any previous review and pinned notes.

### `POST /orders/{id}/notes`
`{ "t": 12, "text": "Cut this pause" }` → order (status `201`). A note the client pins at a
second in the cut; listed in `client_notes`, sorted by `t`.

### `POST /orders/{id}/revisions`
Client asks for changes: `review → in_progress`, `revisions_left` minus one (`409` at zero).

### `POST /orders/{id}/review` (Review Copilot)
```json
{ "client_feedback": "make it more cinematic" }
```
`client_feedback` is optional. Response:
```json
{
  "overall_match": 82,
  "summary": "Hook and pacing match the brief; captions missing in the middle section.",
  "checklist": [
    { "item": "Under 30 seconds", "met": true },
    { "item": "Cafe name on screen", "met": false }
  ],
  "notes": [
    { "timestamp_sec": 12, "issue": "Captions disappear", "suggestion": "Keep captions through 0:12–0:18", "severity": "high", "source": "ai" },
    { "timestamp_sec": 3,  "issue": "Client: make it more cinematic", "suggestion": "Add a slow push-in and a warmer grade on the opening pour", "severity": "medium", "source": "client" }
  ]
}
```
`severity` is `low | medium | high`. `source` is `ai | client`. Saved on the order.
Only allowed while the order is in `review` with a delivered cut (`409` otherwise).
Without feedback it (re)runs the review on `GEMINI_PRO_MODEL`, keeping `client` notes. With
feedback it adds `client` notes via `GEMINI_FAST_MODEL`, running the review first if there is none.
Feedback is screened by Gemma first (blocked text is a `422`). Counts against the AI limit.

### `POST /orders/{id}/approve`
```json
{
  "id": "BMT-7KQ2XDMA", "status": "approved",
  "payout": { "gross_usd": 14.99, "fee_pct": 15, "fee_usd": 2.25, "amount_usd": 12.74, "fx_rate": 84.1,
              "amount_inr": 1071.43, "transfer_id": "RAMP-SIM-3F9A1C2B", "eta": "About 1 business day",
              "rail": "ramp", "status": "simulated", "at": "..." }
}
```
Returns the full order. Payout = total minus platform fee (`PLATFORM_FEE_PCT`, default 15). FX rate from env
`DEMO_FX_USD_INR` (fixed for the demo; say so in the UI). The transfer id is simulated; no money moves.

### Demo payment on `POST /orders`
`payment_method` is `demo_card` (default) or `demo_upi`. The order gets a simulated payment record:
`"payment": { "method": "Test card ending 4242", "amount_usd": 14.99, "amount_inr": 1198, "reference": "PAY-SIM-…", "status": "held", "simulated": true }`.
No card or bank details are ever sent or stored; the checkout only offers these demo methods.

---

## Health

### `GET /healthz`
```json
{ "ok": true,
  "mode": { "ai": "gemini-api|vertex", "storage": "local|gcs", "db": "sqlite|firestore", "auth": "firebase|off" },
  "models": { "brief": "...", "review": "...", "feedback": "...", "screening": "gemma-...", "thumbnail": "gemini-...-image" } }
```
Handy on stage: shows judges it is really running on Google Cloud, and which model does which job.
