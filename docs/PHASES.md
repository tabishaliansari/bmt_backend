# BMT · Build phases

Work top to bottom. One phase at a time. Tick boxes when the "Done when" checks pass.
If a phase runs past its timebox, cut scope inside it rather than skipping ahead.

## Tonight (Thu 19 Nov): local happy path

### Phase 0 · Setup (20 min)
- [x] `frontend/` = copy of `mock-ui/` (mock-ui stays untouched)
- [x] `backend/` scaffold: FastAPI app, `config.py`, `requirements.txt`, `.env` from `.env.example`
- [x] `.gitignore` (`.env`, `backend/data/`, `__pycache__/`, `.venv/`)
- [ ] Gemini API key from AI Studio in `.env`; model IDs set (Tabish adds these by hand)
- **Done when:** `uvicorn app.main:app --reload` serves `GET /api/v1/healthz` and the frontend at `/`.

### Phase 1 · Data and editors (30 min)
- [x] Storage interface + `LocalStorage`; DB interface + SQLite
- [x] `seed.py` ports editors and packages from `mock-ui/js/api.js` (add `price_usd`)
- [x] `GET /editors`, `GET /editors/{id}`, `POST /uploads`
- **Done when:** frontend Discover and storefront load editors from the backend.

### Phase 2 · Brief Builder (60 min)
- [ ] `prompts/brief_builder.md` + `BriefResult` Pydantic schema
- [ ] `ai/client.py`, `ai/media.py`, `ai/brief_builder.py` with structured output
- [ ] `POST /briefs`, `GET /briefs/{id}`, `GET /editors/recommended`
- [ ] Tested on 2–3 of Mustafa's real clips; Mustafa says the brief is useful
- **Done when:** a real clip produces a sensible brief JSON in under ~60 s.

### Phase 3 · Orders and escrow (30 min)
- [ ] Order model, escrow state machine, server-side pricing
- [ ] `POST /orders`, `GET /orders`, `GET /orders/{id}`, `POST /orders/{id}/deliver`, `POST /orders/{id}/approve` (payout record)
- **Done when:** an order moves funded → review → approved with a payout record, via curl.

### Phase 4 · Review Copilot (60 min)
- [ ] `prompts/review_copilot.md`, `prompts/feedback_rewriter.md`, `ReviewResult` schema
- [ ] `POST /orders/{id}/review` with optional `client_feedback`
- **Done when:** a finished edit reviewed against its brief returns a score, checklist and
  timestamped notes that Mustafa agrees with.

### Phase 5 · Frontend wiring (90 min)
- [ ] `api.js` calls the backend (keep a `BMT_USE_MOCKS` fallback)
- [ ] New screens from `DESIGN.md`: Start with your footage, Brief result, AI review panel, payout receipt
- [ ] Order uses the brief; storefront shows "Matches your brief"
- **Done when:** the full happy path in `PRD.md` works in the browser, phone and desktop layouts.

### Phase 6 · Local end-to-end check (20 min)
- [ ] Run the happy path twice from a clean DB with different clips
- [ ] Commit and push. Tag `mvp-local`.
- **Done when:** a teammate can clone, follow `README.md`, and run it.

## Day 1 (Fri 20 Nov): Google Cloud

### Phase 7 · GCP setup (10:00–10:45)
- [ ] Redeem event credits on the billing account (valid 24 h, so not before 10:00)
- [ ] Enable Vertex AI, Cloud Run, Cloud Storage, Firestore, Cloud Build, Artifact Registry
- [ ] Bucket, Firestore (Native), service account and roles (see `ARCHITECTURE.md`)

### Phase 8 · Switch to Google services (10:45–13:30)
- [ ] `USE_VERTEX=true`: Brief Builder and Review Copilot work on Vertex AI
- [ ] `STORAGE=gcs`: uploads land in Cloud Storage; Gemini reads `gs://` URIs for large files
- [ ] `DB=firestore`: orders and briefs persist in Firestore
- **Mentor round 11:30:** show architecture + live brief on real footage.

### Phase 9 · Deploy (14:30–16:00)
- [ ] Dockerfile builds; `gcloud run deploy` succeeds; frontend served from the same URL
- [ ] `/healthz` shows `vertex / gcs / firestore`
- **Done when:** the happy path works on the public Cloud Run URL from a phone.

### Phase 10 · Stretch: Taste Match (16:00–20:00, only if Phase 9 is done)
- [ ] Vertex AI multimodal embeddings for editors' sample work and a reference reel
- [ ] Rank editors by cosine similarity; "Edits like this" on Discover

### Phase 11 · Ship (20:00–01:00)
- [ ] Demo video (2–3 min) following `DEMO.md`
- [ ] Deck updated with real screenshots and the live URL
- [ ] README final, repo public (or shared), submission done when it opens at 23:00, by 01:00 at the latest

## Day 2 (Sat 21 Nov)
- 09:00 submission closed. 10:00–13:00 mentor evaluation (live demo). 14:00–17:30 showcase.
- No new features on Day 2. Only fixes that protect the demo.
