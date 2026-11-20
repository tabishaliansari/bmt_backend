#!/usr/bin/env bash
# Local dev in WSL: Firestore + Auth emulators, then the app on http://localhost:8080.
# Run from backend/:  bash scripts/dev.sh        (Ctrl+C stops everything; PORT=8090 to change)
# Emulator data is not kept between runs; the app re-seeds editors on start.
set -euo pipefail
cd "$(dirname "$0")/.."

# firebase-tools lives in nvm's Node 22; add the newest nvm Node to PATH directly
# (sourcing nvm.sh doesn't activate it reliably in non-interactive shells).
NVM_NODE_BIN="$(ls -d "$HOME"/.nvm/versions/node/v*/bin 2>/dev/null | sort -V | tail -1 || true)"
[ -n "$NVM_NODE_BIN" ] && export PATH="$NVM_NODE_BIN:$PATH"
command -v firebase >/dev/null || { echo "firebase CLI not found. Install it: npm install -g firebase-tools"; exit 1; }
# The Firebase emulators need Java 21+; use the user-space runtime if the system one is older.
if [ -x "$HOME/.local/jre21/bin/java" ]; then
  export JAVA_HOME="$HOME/.local/jre21"
  export PATH="$JAVA_HOME/bin:$PATH"
fi

firebase emulators:start --only firestore,auth --project demo-bmt > /tmp/bmt-emulators.log 2>&1 &
EMU_PID=$!
trap 'kill $EMU_PID 2>/dev/null; wait $EMU_PID 2>/dev/null' EXIT

echo "Starting emulators (log: /tmp/bmt-emulators.log)..."
for _ in $(seq 1 90); do
  if curl -s -o /dev/null http://127.0.0.1:8081 && curl -s -o /dev/null http://127.0.0.1:9099; then break; fi
  sleep 1
done
curl -s -o /dev/null http://127.0.0.1:9099 || { echo "Emulators didn't start; see /tmp/bmt-emulators.log"; exit 1; }
echo "Emulators up: Firestore :8081, Auth :9099, UI http://127.0.0.1:4000"

.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8080}"
