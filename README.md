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

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # add GEMINI_API_KEY and the model IDs
uvicorn app.main:app --reload --port 8080
```

Open http://localhost:8080. The API is under `/api/v1`, health at `/api/v1/healthz`.

## Run on Google Cloud

Set `USE_VERTEX=true`, `STORAGE=gcs`, `DB=firestore` and the project settings in the
environment, then deploy one Cloud Run service from the repo root. Full steps in
`docs/ARCHITECTURE.md` → "Production on Google Cloud".

## Team

Tabish Ali Ansari (lead, AI and cloud) · Bilaal Shaikh (software engineer) ·
Mustafa Bhagat (video editor and creator, FilmPulse)
