# BMT · instructions for Claude Code

You are helping build **BMT**, an AI-native marketplace for video editing, for the
Google Startup Buildathon India 2026 (Pune, 20–21 Nov). Hard deadline: submission
closes **09:00 IST, Saturday 21 Nov**. Scope discipline beats polish.

Read these before doing anything, and keep them up to date as you work:

@docs/MEMORY.md
@docs/RULES.md
@docs/PHASES.md

Reference these when the task touches them:

- `docs/PRD.md`: what we are building and why, MVP scope, out of scope
- `docs/ARCHITECTURE.md`: components, local vs Google Cloud mode, data model
- `docs/API.md`: the exact contract between `frontend/` and `backend/`
- `docs/DESIGN.md`: design tokens, UI rules, new screens to build
- `docs/NOTES.md`: event logistics, open questions, links
- `docs/DEMO.md`: the demo script the whole build serves

## Repo layout

```
bmt/
  mock-ui/     reference only. The original clickable prototype. Never edit.
  frontend/    the real web app. Starts as a copy of mock-ui, wired to the backend.
  backend/     FastAPI service. Also serves frontend/ as static files. Its own git repo.
    docs/      project docs (PRD, architecture, API, design, phases, rules, notes, demo)
```

Never run `git init`, `git commit` or `git push`. The team does all git operations.

## How to work

1. Check `PHASES.md` for the current phase. Work only on that phase.
2. Before writing code, state the plan in 3–6 bullets.
3. After finishing a phase: run it, confirm the "Done when" checks, tick the boxes in
   `PHASES.md`, and add anything future sessions must know to `MEMORY.md`.
4. If something is ambiguous, pick the simplest option that keeps the happy path working,
   and log the decision in `MEMORY.md` under Decisions.
