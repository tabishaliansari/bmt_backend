# BMT · API contract

Base path: `/api/v1`. JSON in and out, except uploads (multipart). Errors return
`{"error": {"code": "string", "message": "human readable"}}` with a 4xx/5xx status.
Money: integers in the smallest unit is overkill for the demo; use numbers with 2 decimals,
and always say the currency (`_usd`, `_inr`).

The frontend calls these **only** through `frontend/js/api.js`. Keep that file's function
names; replace mock bodies with `fetch()`. A flag `BMT_USE_MOCKS` in `api.js` keeps the
old mock behaviour available as a fallback for the demo.

---

## Uploads

### `POST /uploads`
Multipart: `file` (video), `kind` = `raw` | `cut`.
```json
{ "id": "up_8f2c", "kind": "raw", "filename": "clip1.mp4", "mime": "video/mp4", "size": 12485123 }
```
Reject files over `MAX_UPLOAD_MB` (default 50) with `413`.

---

## Briefs (Brief Builder)

### `POST /briefs`
```json
{ "upload_ids": ["up_8f2c", "up_91aa"], "client_note": "Reel for my cafe launch, fun and fast, 30s" }
```
Response (can take 10–60 s; frontend shows progress):
```json
{
  "id": "br_3d10",
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

### `GET /briefs/{id}`
Returns the same object.

---

## Editors

### `GET /editors?category=reels&q=`
List of editors (same shape as `mock-ui/js/api.js`), each with `packages[]`.

### `GET /editors/{id}`
One editor with `packages[]`, `credit_list[]`, `reviews[]`.

### `GET /editors/recommended?brief_id=br_3d10`
Editors whose categories match the brief's `recommended_package.category`, best rated first.
(Taste Match later replaces this ranking.)

---

## Orders

### `POST /orders`
```json
{ "editor_id": "riya", "package_id": "reel", "brief_id": "br_3d10", "addons": ["captions"], "rush": false }
```
```json
{
  "id": "BMT-2481", "editor_id": "riya", "package_id": "reel", "brief_id": "br_3d10",
  "total_usd": 14.99, "status": "funded",
  "timeline": [{ "status": "funded", "at": "2026-11-20T10:42:00Z", "label": "Payment held safely" }]
}
```
The server computes `total_usd`. Never trust a price from the client.

### `GET /orders` and `GET /orders/{id}`
Order objects, newest first. Include the brief result and review if present.

### `POST /orders/{id}/deliver`
`{ "cut_upload_id": "up_c001" }` → order with `status: "review"`.

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

### `POST /orders/{id}/approve`
```json
{
  "id": "BMT-2481", "status": "approved",
  "payout": { "amount_usd": 12.74, "fx_rate": 84.1, "amount_inr": 1071.43, "rail": "ramp", "status": "simulated" }
}
```
Payout = total minus platform fee (`PLATFORM_FEE_PCT`, default 15). FX rate from env
`DEMO_FX_USD_INR` (fixed for the demo; say so in the UI).

---

## Health

### `GET /healthz`
`{ "ok": true, "mode": { "ai": "gemini-api|vertex", "storage": "local|gcs", "db": "sqlite|firestore" } }`
Handy on stage: shows judges it is really running on Google Cloud.
