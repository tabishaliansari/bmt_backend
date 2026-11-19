# BMT

An AI-native marketplace for video editing. Clients order edits from editors with verified
work; Gemini writes the brief from raw footage and reviews each cut against it; BMT holds
the payment until the client approves and pays the editor in their own currency.

Built for the Google Startup Buildathon India 2026 (Pune).

## Repo

| Folder | What |
|---|---|
| `frontend/` | Web app (plain HTML, CSS, JS). Phone, desktop, light and dark. |
| `backend/` | FastAPI service. Gemini (API or Vertex AI), storage, database, simulated payments. |
| `mock-ui/` | Original clickable prototype (reference only). |

Docs: `docs/PRD.md` (what and why), `docs/ARCHITECTURE.md` (how), `docs/API.md` (contract),
`docs/DESIGN.md` (UI), `docs/PHASES.md` (plan), `docs/RULES.md` (how we work), `docs/DEMO.md` (demo script).

## Run locally

Clone `backend/` and `frontend/` side by side (the backend serves `../frontend` at `/`).

macOS / Linux:
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # add GEMINI_API_KEY and the model IDs
uvicorn app.main:app --reload --port 8080
```

Windows (PowerShell):
```powershell
cd backend
python -m venv .venv; .venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env      # add GEMINI_API_KEY and the model IDs
uvicorn app.main:app --reload --port 8080
```

Open http://localhost:8080. The API is under `/api/v1`, health at `/api/v1/healthz`.
After editing `.env`, restart uvicorn (settings are read once).

- **Check it works:** `bash scripts/smoke.sh` walks every endpoint with curl. Add
  `SMOKE_CLIP=path/to/clip.mp4` to also run the Gemini steps (brief, review, feedback).
- **Demo fallback:** http://localhost:8080/?mocks=1 runs the whole UI on mock data with
  canned Gemini results, no backend calls.
- **Clean demo data:** stop uvicorn, delete `data/bmt.db` and `data/uploads/`, start again.
  In the browser, You → Reset demo data clears local favourites and the active brief.

## Run on Google Cloud

Set `USE_VERTEX=true`, `STORAGE=gcs`, `DB=firestore` and the project settings in the
environment, then deploy one Cloud Run service from the repo root. Full steps in
`docs/ARCHITECTURE.md` → "Production on Google Cloud".

## Team

Tabish Ali Ansari (lead, AI and cloud) · Bilaal Shaikh (software engineer) ·
Mustafa Bhagat (video editor and creator, FilmPulse)
