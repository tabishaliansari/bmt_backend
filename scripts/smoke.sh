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

check "brief: unknown upload"  404 '"error"'            -H 'Content-Type: application/json' -d '{"upload_ids":["up_nope"]}' "$BASE/briefs"
check "brief: no uploads"      422 '"error"'            -H 'Content-Type: application/json' -d '{"upload_ids":[]}' "$BASE/briefs"
check "unknown brief is 404"   404 '"error"'            "$BASE/briefs/br_nope"
check "recommended: no brief"  404 '"error"'            "$BASE/editors/recommended?brief_id=br_nope"
check "add-ons and rush fee"   200 '"rush_fee_usd"'     "$BASE/addons"

# ---- Orders and escrow (no Gemini needed). A client-sent price must be ignored.
JSON='Content-Type: application/json'
id_from_body() { grep -o "\"id\":\"$1[A-Za-z0-9_-]*\"" "$TMP/body" | head -1 | cut -d'"' -f4; }

check "order: server prices it" 201 '"total_usd":14.99' -H "$JSON" \
  -d '{"editor_id":"riya","package_id":"reel","addons":["captions"],"total_usd":0.01}' "$BASE/orders"
ORDER="$(id_from_body BMT-)"
check "order: starts funded"    200 '"status":"funded"'  "$BASE/orders/$ORDER"
check "order: can't approve yet" 409 '"error"'           -X POST "$BASE/orders/$ORDER/approve"
check "order: unknown add-on"   422 '"error"'            -H "$JSON" -d '{"editor_id":"riya","package_id":"reel","addons":["gold"]}' "$BASE/orders"
check "upload a cut"            201 '"kind":"cut"'       -F "file=@$TMP/clip.mp4" -F kind=cut "$BASE/uploads"
CUT="$(id_from_body up_)"
check "deliver the cut"         200 '"status":"review"'  -H "$JSON" -d "{\"cut_upload_id\":\"$CUT\"}" "$BASE/orders/$ORDER/deliver"
check "cut streams back"        206 ''                   -H 'Range: bytes=0-99' "$BASE/uploads/$CUT/content"
check "pin a note"              201 '"client_notes":\[{' -H "$JSON" -d '{"t":3,"text":"Cut this pause"}' "$BASE/orders/$ORDER/notes"
check "approve"                 200 '"amount_inr":1071.43' -X POST "$BASE/orders/$ORDER/approve"
check "approve twice is 409"    409 '"error"'            -X POST "$BASE/orders/$ORDER/approve"
check "orders list"             200 "\"id\":\"$ORDER\""  "$BASE/orders"

# ---- Real Gemini calls, only when a clip is given:  SMOKE_CLIP=path/to/clip.mp4 bash scripts/smoke.sh
if [[ -n "${SMOKE_CLIP:-}" ]]; then
  check "upload real clip"      201 '"id":"up_'      -F "file=@$SMOKE_CLIP" -F kind=raw "$BASE/uploads"
  UP_ID="$(id_from_body up_)"
  check "brief from real clip"  201 '"best_moments"' -H "$JSON" \
    -d "{\"upload_ids\":[\"$UP_ID\"],\"client_note\":\"Short reel, fun and fast, 30 seconds\"}" "$BASE/briefs"
  BR_ID="$(id_from_body br_)"
  check "get the brief"         200 '"result"'       "$BASE/briefs/$BR_ID"
  check "recommended editors"   200 '"id":'          "$BASE/editors/recommended?brief_id=$BR_ID"

  check "order with the brief"  201 '"brief_id"'     -H "$JSON" -d "{\"editor_id\":\"riya\",\"package_id\":\"reel\",\"brief_id\":\"$BR_ID\"}" "$BASE/orders"
  ORDER2="$(id_from_body BMT-)"
  check "upload real cut"       201 '"kind":"cut"'   -F "file=@$SMOKE_CLIP" -F kind=cut "$BASE/uploads"
  CUT2="$(id_from_body up_)"
  check "deliver real cut"      200 '"status":"review"' -H "$JSON" -d "{\"cut_upload_id\":\"$CUT2\"}" "$BASE/orders/$ORDER2/deliver"
  check "AI review"             200 '"overall_match"' -H "$JSON" -d '{}' "$BASE/orders/$ORDER2/review"
  check "feedback into notes"   200 '"source":"client"' -H "$JSON" -d '{"client_feedback":"make it more cinematic"}' "$BASE/orders/$ORDER2/review"
else
  echo "SKIP  Gemini checks (set SMOKE_CLIP=path/to/clip.mp4 and the Gemini values in .env)"
fi

exit "$FAILED"
