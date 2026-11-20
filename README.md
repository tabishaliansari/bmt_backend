# BMT

An AI-native marketplace for video editing. Clients order edits from editors with verified
work; Gemini writes the brief from raw footage and reviews each cut against it; Nano Banana
drafts the thumbnail; Gemma screens what people type; BMT holds the payment until the client
approves and pays the editor in their own currency.

Built for the Google Startup Buildathon India 2026 (Pune).

## Repo

| Folder | What |
|---|---|
| `frontend/` | Web app (plain HTML, CSS, JS). Phone, desktop, light and dark. Separate repo. |
| `backend/` | FastAPI service. Gemini, Gemma and Nano Banana (API or Vertex AI), Firestore, Cloud Storage, Firebase Auth, simulated payments. |
| `mock-ui/` | Original clickable prototype (reference only). |

Docs: `docs/HAPPY_PATH.md` (what we demo today), `docs/PRD.md` (what and why),
`docs/ARCHITECTURE.md` (how), `docs/API.md` (contract), `docs/DESIGN.md` (UI),
`docs/PHASES.md` (plan), `docs/RULES.md` (how we work), `docs/DEMO.md` (demo script).

## Run locally (WSL / Linux)

Clone `backend/` and `frontend/` side by side (the backend serves `../frontend` at `/`).
You need Python 3.11+, Node 20+ with `firebase-tools`, and Java 21+ for the Firebase emulators.

One time:
```bash
cd backend
python3 -m venv .venv && .venv/bin/python -m pip install -r requirements.txt
npm install -g firebase-tools
cp .env.example .env        # add GEMINI_API_KEY
```

Every time (starts the Firestore and Auth emulators, then the app):
```bash
cd backend && bash scripts/dev.sh
```

Open http://localhost:8080. Sign in with Google: locally this is the **Auth emulator**, which
shows a test account screen instead of a real Google login (pick "Add new account"). The
emulators' UI is at http://127.0.0.1:4000. Emulator data is not kept between runs.

- **Check it works:** `bash scripts/smoke.sh` walks every endpoint with curl, as two test users
  (and checks they can't see each other's data). Add `SMOKE_CLIP=path/to/clip.mp4` to also run
  the Gemini steps (costs API calls).
- **Reset the demo:** `.venv/bin/python scripts/reset_demo.py` removes all orders, briefs and
  uploads and re-seeds the editors.
- **Demo fallback:** http://localhost:8080/?mocks=1 runs the whole UI on mock data with canned
  AI results, no backend calls.
- **Without emulators:** set `DB=sqlite` and `AUTH=off` in `.env`, then
  `.venv/bin/python -m uvicorn app.main:app --port 8080`.

## Run on Google Cloud

`scripts/deploy.sh` builds one container (API + frontend, `deploy/Dockerfile`) and deploys it to
Cloud Run with `USE_VERTEX=true`, `STORAGE=gcs`, `DB=firestore`, `AUTH=firebase`. See the header
of that script for the variables and secrets it needs, and `docs/ARCHITECTURE.md` →
"Production on Google Cloud" for the project setup.

## Team

Tabish Ali Ansari (lead, AI and cloud) · Bilaal Shaikh (software engineer) ·
Mustafa Bhagat (video editor and creator, FilmPulse)
