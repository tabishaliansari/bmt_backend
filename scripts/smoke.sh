#!/usr/bin/env bash
# Walks the happy path with curl. Run before every push:  bash scripts/smoke.sh [base_url]
# Extend this as each phase adds endpoints.
set -euo pipefail

BASE="${1:-http://localhost:8080}/api/v1"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
FAILED=0

check() {  # check <name> <expected status> <body must contain> <curl args...>
  local name="$1" want="$2" needle="$3"; shift 3
  local status
  status="$(curl -s -o "$TMP/body" -w '%{http_code}' "$@")"
  if [[ "$status" == "$want" ]] && grep -q -- "$needle" "$TMP/body"; then
    echo "PASS  $name"
  else
    echo "FAIL  $name (status $status, wanted $want containing '$needle')"
    head -c 300 "$TMP/body"; echo
    FAILED=1
  fi
}

head -c 20000 /dev/urandom > "$TMP/clip.mp4"
echo "not a video" > "$TMP/notes.txt"

check "health"                 200 '"ok":true'          "$BASE/healthz"
check "list editors"           200 '"id":"riya"'        "$BASE/editors"
check "filter by category"     200 '"id":"arjun"'       "$BASE/editors?category=podcasts"
check "one editor"             200 '"price_usd"'        "$BASE/editors/riya"
check "unknown editor is 404"  404 '"error"'            "$BASE/editors/nobody"
check "upload a raw clip"      201 '"id":"up_'          -F "file=@$TMP/clip.mp4" -F kind=raw "$BASE/uploads"
check "reject non-video"       415 '"error"'            -F "file=@$TMP/notes.txt" -F kind=raw "$BASE/uploads"

exit "$FAILED"
