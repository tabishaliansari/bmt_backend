# BMT · API contract

Base path: `/api/v1`. JSON in and out, except uploads (multipart). Errors return
`{"error": {"code": "string", "message": "human readable"}}` with a 4xx/5xx status.
Money: integers in the smallest unit is overkill for the demo; use numbers with 2 decimals,
and always say the currency (`_usd`, `_inr`).

The frontend calls these **only** through `frontend/js/api.js`, which converts the snake_case
JSON here into the shapes the screens use. `BMT_USE_MOCKS` (turned on by adding `?mocks=1` to
the URL, before the `#`) serves the same functions from mock data with canned Gemini results,
as the demo fallback.

Common errors: `404` unknown id, `409` action not allowed in the order's current status,
`413` file too large, `415` not a video, `422` invalid input, `502 ai_error` Gemini failed or
is not configured, `504 ai_timeout` Gemini took longer than `AI_TIMEOUT_SEC`.

---

## Uploads

### `POST /uploads`
Multipart: `file` (video), `kind` = `raw` | `cut`.
```json
{ "id": "up_8f2c", "kind": "raw", "filename": "clip1.mp4", "mime": "video/mp4", "size": 12485123 }
```
Status `201`. Reject files over `MAX_UPLOAD_MB` (default 50) with `413`, non-video files with `415`.

### `GET /uploads/{id}/content`
Streams the video (supports `Range`, so the review player can seek).

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

### `GET /briefs/{id}`
Returns the same object.

### `PUT /briefs/{id}`
`{ "result": { ...the full result... } }` → the updated brief. The client edits the brief
inline before ordering.

---

## Editors

### `GET /editors?category=reels&q=`
List of editors (same shape as `mock-ui/js/api.js`), each with `packages[]`.

### `GET /editors/{id}`
One editor with `packages[]`, `credit_list[]`, `reviews[]`.

### `GET /editors/recommended?brief_id=br_3d10`
Editors whose categories match the brief's `recommended_package.category`, best rated first.
(Taste Match later replaces this ranking.)

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
  "id": "BMT-2481", "editor_id": "riya", "package_id": "reel", "brief_id": "br_3d10",
  "brief": { "...": "copy of the brief result at order time" },
  "title": "Instagram Reel", "g": 2, "addons": ["captions"], "rush": false, "note": "",
  "total_usd": 14.99, "total_inr": 1198, "status": "funded", "revisions_left": 2,
  "due_at": "2026-11-22T10:42:00Z", "cut_upload_id": null, "review": null,
  "client_notes": [], "payout": null, "created_at": "2026-11-20T10:42:00Z",
  "timeline": [{ "status": "funded", "at": "2026-11-20T10:42:00Z", "label": "Payment held safely" }]
}
```
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

### `POST /orders/{id}/approve`
```json
{
  "id": "BMT-2481", "status": "approved",
  "payout": { "amount_usd": 12.74, "fx_rate": 84.1, "amount_inr": 1071.43, "rail": "ramp", "status": "simulated" }
}
```
Returns the full order. Payout = total minus platform fee (`PLATFORM_FEE_PCT`, default 15). FX rate from env
`DEMO_FX_USD_INR` (fixed for the demo; say so in the UI).

---

## Health

### `GET /healthz`
`{ "ok": true, "mode": { "ai": "gemini-api|vertex", "storage": "local|gcs", "db": "sqlite|firestore" } }`
Handy on stage: shows judges it is really running on Google Cloud.
