# BMT · Project memory

Long-lived facts and decisions. Claude Code: read this every session, and append new
decisions under **Decisions** with a date. Keep it short; move detail to other docs.

## Snapshot

- **Product:** BMT, an AI-native marketplace for video editing. Two-sided guarantee:
  work for clients (pay on approval), payment for editors (local currency via Ramp).
- **Event:** Google Startup Buildathon India 2026, Pune. Day 1 Fri 20 Nov, Day 2 Sat 21 Nov.
- **Hard deadline:** submission closes 09:00 IST, Sat 21 Nov. Target: submit by 01:00.
- **Team:** Tabish (lead; AI, cloud), Bilaal (software engineer; backend, frontend wiring),
  Mustafa (video editor and creator, FilmPulse; footage, quality judge, demo, pitch).
- **Current phase:** see `PHASES.md`.

## Stack (fixed, do not change)

- Frontend: plain HTML, CSS, JS. No framework, no build step. All data via `js/api.js`.
- Backend: Python 3.11+, FastAPI, Pydantic v2, `google-genai` SDK, uvicorn.
- Local: Gemini API key, local disk, SQLite.
- Cloud: Vertex AI, Cloud Storage, Firestore, Cloud Run (one service serves API + frontend).

## Decisions

- 2026-11-19: MVP = Brief Builder + Review Copilot + simulated escrow and Ramp payout.
  Taste Match is a stretch goal. Proof Engine, Gemini Live, Nano Banana, Lyria are roadmap only.
- 2026-11-19: Every Google service sits behind an env switch (`USE_VERTEX`, `STORAGE`, `DB`).
- 2026-11-19: Video goes to Gemini inline (`Part.from_bytes`) for clips under ~15 MB.
  Larger files: Files API locally, `gs://` URI on Vertex.
- 2026-11-19: Model IDs come from env (`GEMINI_FAST_MODEL`, `GEMINI_PRO_MODEL`), never hard-coded.
- 2026-11-19: Prices live on the server. Store USD and INR; payout uses a fixed demo FX rate.
- 2026-11-19: `mock-ui/` is a frozen reference. All UI work happens in `frontend/`.
- 2026-11-20: Docs live in `backend/docs/`. `backend/` and `frontend/` are separate git repos,
  each with its own `.gitignore`. `bmt/` itself is not a repo.
- 2026-11-20: Claude never runs `git init`, `git commit` or `git push`. The team does all git.
- 2026-11-20: The frontend is mounted at `/` in every mode (local too), from `FRONTEND_DIR`
  (default `../frontend`). Mounted after the API router so `/api/v1/*` wins.
- 2026-11-20: All errors, including 404s from unknown paths, use
  `{"error": {"code", "message"}}` (handler on Starlette's `HTTPException`).
- 2026-11-20: Local dev runs on Python 3.14 in `backend/.venv`.
- 2026-11-20: The DB interface is a JSON document store (`put/get/list` by collection + id).
  SQLite keeps it in one `docs` table, which lines up with Firestore for Phase 8.
- 2026-11-20: Seed is written on every startup (upsert), so edits to `seed.py` apply after a
  restart. USD prices are hand-set (about INR / 84, ending .99); Reel = $12.99.
- 2026-11-20: The backend speaks snake_case (`packages`, `credit_list`, `rating_count`).
  `api.js` converts it with `toEditor()` into the shape the screens already use
  (`menu`, `creditList`, `price` = INR), so screen code stays unchanged.
- 2026-11-20: `BMT_USE_MOCKS` in `api.js` is `false`; add `?mocks=1` to the URL (before the `#`)
  to serve mock data instead. This is the demo fallback.
- 2026-11-20: Uploads accept a video MIME from the request, or one guessed from the file
  extension (curl sends `application/octet-stream`). Too large → 413, not a video → 415.
- 2026-11-20: Still mocked in `api.js` until their phase: categories, quick packages,
  add-ons and rush fee (Phase 3 pricing), orders, quotes.

## Glossary

- **Brief:** structured description of the video to make, written by Gemini from raw clips.
- **Cut:** a video the editor delivers for review.
- **Escrow / held safely:** client's money held by BMT until approval (simulated).
- **Payout:** money released to the editor after approval (simulated Ramp transfer).
- **Taste test:** cheapest package; a short sample edit so clients can try an editor.

## Gotchas found while building

_(Append here: SDK quirks, model limits, things that broke and how we fixed them.)_

- Windows: `uvicorn --reload` sometimes detects a change but never finishes reloading, so the
  old code keeps serving. If a change doesn't show up, stop and restart uvicorn.
- An exception handler registered for FastAPI's `HTTPException` misses 404s raised by the
  `StaticFiles` mount. Register it for `starlette.exceptions.HTTPException` instead.
- Starlette reads the whole multipart body before the handler runs, so the upload size
  limit is checked on `UploadFile.size` after receipt, not while streaming.
- Phase 2: declare `GET /editors/recommended` before `GET /editors/{editor_id}` in
  `routers/editors.py`, or "recommended" is matched as an editor id.
