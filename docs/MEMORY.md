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
- 2026-11-20: Every Gemini call goes through `ai/structured.py::generate_json()`: JSON mode +
  Pydantic `response_schema`, one retry on unreadable JSON, `AIError` → 502 `ai_error`,
  `AITimeout` → 504 `ai_timeout`. Timeout is `AI_TIMEOUT_SEC` (default 90) on the client.
- 2026-11-20: Video to Gemini: inline up to `INLINE_VIDEO_MAX_MB` (15), Files API above that in
  local mode. Vertex + large clip raises a clear error until Phase 8 adds `gs://`.
- 2026-11-20: `recommended_package.category` is limited to the editors' 6 categories, so
  `/editors/recommended` always has something to match. Clips are labelled
  `Clip <upload_id> (<filename>)` so best moments point at the right clip.
- 2026-11-20: `POST /briefs` waits for Gemini and returns the finished brief (no background
  job). Only `raw` uploads are accepted; a `cut` returns 422.
- 2026-11-20: Still mock in both modes (not in MVP scope): categories, quick packages,
  courses, posts, mentors, the editor studio, credits lookup, chat.
- 2026-11-20: Add-ons and the rush fee live in `seed.py::CATALOG` (INR + USD) and are served by
  `GET /addons`. Captions = $2.00, so Reel + captions = $14.99 as in `API.md`.
- 2026-11-20: Order ids are `BMT-<2481 + count>`. `due_at` = now + package `eta_hours`
  (24 h if rush). Revisions: 2, or 3 with the "revision" add-on.
- 2026-11-20: Order statuses map to the UI as funded/in_progress → "editing", review, approved.
  Only `payments/escrow.py::transition()` changes status; bad transitions return 409.
- 2026-11-20: Orders keep a copy of the brief result (`order.brief`), so later brief edits
  don't change an order already placed. The brief is optional on an order.
- 2026-11-20: Review notes: `source` is set by the server (`ai` from Review Copilot, `client`
  from the feedback rewriter), never by Gemini. Re-running the review keeps `client` notes.
  Pinned notes from the review player are separate: `order.client_notes` (`t`, `text`).
- 2026-11-20: The demo "Upload the editor's cut" button on the order screen uploads a `cut`
  and calls `/deliver`; it stands in for the editor app. The review player plays the real cut
  from `GET /uploads/{id}/content`.
- 2026-11-20: The active brief (the one being ordered for) is kept in localStorage `bmt:brief`
  and cleared once an order is placed with it. The storefront picks the matching package by
  word overlap with `package_title`, falling back to the "best" package in that category.
- 2026-11-20: All text from users or Gemini goes through `BMT.ui.esc()` before `innerHTML`.
- 2026-11-20 (Day 1): The happy path is `docs/HAPPY_PATH.md` v2. Dev runs in **WSL**; git on Windows.
- 2026-11-20: **DB is Firestore** (`DB=firestore`), locally on the Firestore emulator
  (`FIRESTORE_EMULATOR_HOST`, project `demo-bmt`). SQLite stays as a fallback. Firestore has no
  insertion order, so routers sort what they show (editors in seed order, orders by date).
- 2026-11-20: **Auth is Firebase Authentication with Google sign-in** (`AUTH=firebase`), locally on
  the Auth emulator. Backend verifies the ID token (`app/auth.py`, `UserId` dependency). Uploads,
  briefs and orders carry `owner`; someone else's id is a 404. `AUTH=off` = one local user (dev only).
  Frontend: Firebase compat SDK 10.14.1 from gstatic (no build step), config from `GET /config`;
  private routes (start, brief, orders, order, review) show a sign-in screen first.
- 2026-11-20: Order ids are random (`BMT-` + 8 chars). Media is served only through signed,
  expiring links (`GET /uploads/{id}/url`), since `<video>`/`<img>` can't send the auth header.
  `MEDIA_SIGNING_KEY` must be set on Cloud Run (Secret Manager), or links break across instances.
- 2026-11-20: Gemini calls are limited per user (`AI_RATE_LIMIT_PER_HOUR`, in-memory per instance).
  AI config errors return a generic 503; details go to the server log only.
- 2026-11-20: **Gemma** (`GEMINI_SCREEN_MODEL=gemma-4-26b-a4b-it`) screens the client note and review
  feedback before Gemini. Gemma on the Gemini API has no JSON mode, so it answers one line
  (`ALLOW` / `BLOCK: reason`), the one exception to "structured output on every call". Fails open.
- 2026-11-20: **Nano Banana** (`GEMINI_IMAGE_MODEL=gemini-3.1-flash-image`) drafts a thumbnail via
  `POST /briefs/{id}/thumbnail`, stored as an upload of kind `thumb`. It needs a billed project:
  the free API key returns 429 for every image model, so it only works once credits arrive.
- 2026-11-20: Mustafa is the first seeded editor (`featured`, listed first, recommended first).
  His credits are empty until he sends real FilmPulse ones; never invent them.
- 2026-11-20: Deploy = `scripts/deploy.sh` (stages backend + frontend with `deploy/Dockerfile`,
  then `gcloud run deploy --source`). Cloud Run caps requests at 32 MB, so `MAX_UPLOAD_MB=30` there.
  `STORAGE=gcs` caches files in `/tmp` and serves them with Range support; Vertex reads large clips
  by `gs://` URI.

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
- `GET /editors/recommended` must stay declared before `GET /editors/{editor_id}`, or
  "recommended" is matched as an editor id.
- `google-genai` 3.x uses `httpx2` (a fork of httpx), not `httpx`, so `import httpx` fails.
  `structured.py` catches the timeout error of whichever one is installed.
- Settings and the Gemini client are cached: after editing `.env`, restart uvicorn.
- Keep Python 3.11 syntax (`TypeVar`, not `def f[T]`); the Dockerfile may use 3.11/3.12.
- Browser-recorded WebM (MediaRecorder) reports `duration = Infinity`, and in the app's
  built-in browser even 0 after the usual seek-to-end trick. The review player then keeps its
  0:58 placeholder. Real MP4/MOV files are fine. Use real MP4s for the demo.
- Testing without a Gemini key: run the UI with `?mocks=1`, or write a brief/review straight
  into the DB from a throwaway script. Never add a fake-AI mode to the product code.
- Scripted `el.focus()`/`blur()` does nothing while the page isn't focused (e.g. a hidden
  browser pane), so inline-edit saves look broken in automated tests. Dispatch the event instead.
- firebase-tools 15 needs **Java 21+** for the emulators. WSL has Java 17 and no passwordless
  sudo, so a Temurin JRE 21 lives in `~/.local/jre21`; `scripts/dev.sh` puts it on PATH.
  firebase-tools also needs Node 20+: Node 22 is installed with nvm (WSL's system Node is 18).
- The venue/home link is slow (~40-60 kB/s to PyPI and Adoptium); Gemini calls took up to 190 s.
  `AI_TIMEOUT_SEC=300` locally for now.
- `gemini-2.5-pro` and `gemini-3.1-pro-preview` aren't available to the free key, so both
  `GEMINI_FAST_MODEL` and `GEMINI_PRO_MODEL` are `gemini-3.8-flash` until Vertex is set up.
- From Git Bash, run WSL scripts with `MSYS_NO_PATHCONV=1 wsl.exe -- bash <script>`; inline
  `bash -lc "..."` quoting breaks on `$vars` and redirects.
