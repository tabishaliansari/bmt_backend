# BMT · Rules

Rules for everyone writing code here, human or AI. When a rule and speed conflict,
the rule wins; these exist to protect the demo.

## Scope

1. Build only what the current phase in `PHASES.md` asks for. Ideas go in `NOTES.md`.
2. The happy path in `PRD.md` must keep working after every change. Check it before committing.
3. No new frameworks, languages or build steps. Frontend stays plain HTML, CSS and JS.
4. Simulated things are labelled as simulated in the UI (escrow, Ramp payout, FX rate).

## Code

5. Every Google service goes through its interface (`ai/`, `storage/`, `db/`). No direct
   SDK calls from routers.
6. Config comes from environment variables via `config.py`. No hard-coded keys, model IDs,
   bucket names, project IDs or regions.
7. Every Gemini call uses structured output with a Pydantic schema, is wrapped in a timeout,
   retries once on invalid JSON, and returns a clear error otherwise.
8. Prompts live in `backend/prompts/*.md`, not in Python strings.
9. Prices and state changes happen on the server only. The frontend never sends a price.
10. Frontend data access goes only through `frontend/js/api.js`, keeping its function names
    and return shapes (`API.md`).
11. Use design tokens and `BMT.ui` helpers. No hex colours in JS (`DESIGN.md`).
12. Keep functions small and files focused. Type hints in Python. No dead code, no commented-out blocks.

## Safety

13. Never commit `.env`, keys, service-account JSON, uploaded videos or the SQLite file.
14. Validate uploads: video MIME types only, size under `MAX_UPLOAD_MB`.
15. Don't log video bytes or full prompts with user content.
16. `mock-ui/` is read-only.

## Working with Claude Code

17. Plan first (3–6 bullets), then build. Show the diff summary after.
18. After each phase: run it, tick `PHASES.md`, log decisions and gotchas in `MEMORY.md`.
19. Small commits with clear messages: `feat(briefs): structured Brief Builder output`.
20. If stuck for more than 15 minutes on one bug, stop, write down what was tried in
    `NOTES.md`, and choose a simpler path.

## Testing

21. Test AI features with Mustafa's real clips, under 1 minute each.
22. Keep a `backend/scripts/smoke.sh` that walks the happy path with curl. Run it before every push.
