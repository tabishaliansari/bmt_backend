#!/usr/bin/env bash
# Walks the happy path with curl. Run before every push:  bash scripts/smoke.sh [base_url]
# With AUTH=firebase it needs the Auth emulator (scripts/dev.sh starts it): it signs up two
# throwaway users there, runs the path as user A and checks user B can't see A's data.
# Gemini steps only run when SMOKE_CLIP=path/to/clip.mp4 is set (they cost API calls).
set -euo pipefail

BASE="${1:-http://localhost:8080}/api/v1"
AUTH_EMULATOR="${AUTH_EMULATOR:-http://127.0.0.1:9099}"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
FAILED=0
JSON='Content-Type: application/json'

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
field() { grep -o "\"$1\":\"[^\"]*\"" "$TMP/body" | head -1 | cut -d'"' -f4; }
id_from_body() { grep -o "\"id\":\"$1[A-Za-z0-9_-]*\"" "$TMP/body" | head -1 | cut -d'"' -f4; }

new_user() {  # anonymous user on the Auth emulator -> prints an ID token
  curl -s -H "$JSON" -d '{"returnSecureToken":true}' \
    "$AUTH_EMULATOR/identitytoolkit.googleapis.com/v1/accounts:signUp?key=demo-key" \
    | grep -o '"idToken":"[^"]*"' | cut -d'"' -f4
}

AUTH_MODE="$(curl -s "$BASE/config" | grep -o '"auth":"[a-z]*"' | cut -d'"' -f4)"
if [[ "$AUTH_MODE" == "firebase" ]]; then
  TOKEN_A="$(new_user)"; TOKEN_B="$(new_user)"
  [[ -n "$TOKEN_A" && -n "$TOKEN_B" ]] || { echo "FAIL  couldn't get test users from $AUTH_EMULATOR"; exit 1; }
else
  TOKEN_A="none"; TOKEN_B="none"
fi
A=(-H "Authorization: Bearer $TOKEN_A")
B=(-H "Authorization: Bearer $TOKEN_B")

head -c 20000 /dev/urandom > "$TMP/clip.mp4"
echo "not a video" > "$TMP/notes.txt"

# ---- Public
check "health"                 200 '"ok":true'          "$BASE/healthz"
check "security headers"       200 ''                   -D "$TMP/h" "$BASE/healthz"
grep -qi "x-frame-options: deny" "$TMP/h" && echo "PASS  x-frame-options" || { echo "FAIL  x-frame-options"; FAILED=1; }
check "list editors"           200 '"id":"mustafa"'     "$BASE/editors"
check "filter by category"     200 '"id":"arjun"'       "$BASE/editors?category=podcasts"
check "one editor"             200 '"price_usd"'        "$BASE/editors/riya"
check "unknown editor is 404"  404 '"error"'            "$BASE/editors/nobody"
check "add-ons and rush fee"   200 '"rush_fee_usd"'     "$BASE/addons"

# ---- Auth
if [[ "$AUTH_MODE" == "firebase" ]]; then
  check "orders need sign-in"   401 '"error"'          "$BASE/orders"
  check "bad token rejected"    401 '"error"'          -H 'Authorization: Bearer nope' "$BASE/orders"
fi

# ---- Uploads
check "upload a raw clip"      201 '"id":"up_'          "${A[@]}" -F "file=@$TMP/clip.mp4" -F kind=raw "$BASE/uploads"
check "reject non-video"       415 '"error"'            "${A[@]}" -F "file=@$TMP/notes.txt" -F kind=raw "$BASE/uploads"
check "brief: unknown upload"  404 '"error"'            "${A[@]}" -H "$JSON" -d '{"upload_ids":["up_nope"]}' "$BASE/briefs"
check "brief: no uploads"      422 '"error"'            "${A[@]}" -H "$JSON" -d '{"upload_ids":[]}' "$BASE/briefs"
check "unknown brief is 404"   404 '"error"'            "${A[@]}" "$BASE/briefs/br_nope"

# ---- Orders and escrow (no Gemini needed). A client-sent price must be ignored.
check "order: server prices it" 201 '"total_usd":14.99' "${A[@]}" -H "$JSON" \
  -d '{"editor_id":"mustafa","package_id":"reel","addons":["captions"],"total_usd":0.01}' "$BASE/orders"
ORDER="$(id_from_body BMT-)"
[[ "$ORDER" =~ ^BMT-[A-Z2-9]{8}$ ]] && echo "PASS  order id is random ($ORDER)" || { echo "FAIL  order id format: $ORDER"; FAILED=1; }
check "order: starts funded"    200 '"status":"funded"'  "${A[@]}" "$BASE/orders/$ORDER"
check "order: payment recorded" 200 '"reference":"PAY-SIM-' "${A[@]}" "$BASE/orders/$ORDER"
check "order: can't approve yet" 409 '"error"'           "${A[@]}" -X POST "$BASE/orders/$ORDER/approve"
check "order: unknown add-on"   422 '"error"'            "${A[@]}" -H "$JSON" -d '{"editor_id":"riya","package_id":"reel","addons":["gold"]}' "$BASE/orders"
check "upload a cut"            201 '"kind":"cut"'       "${A[@]}" -F "file=@$TMP/clip.mp4" -F kind=cut "$BASE/uploads"
CUT="$(id_from_body up_)"
check "deliver the cut"         200 '"status":"review"'  "${A[@]}" -H "$JSON" -d "{\"cut_upload_id\":\"$CUT\"}" "$BASE/orders/$ORDER/deliver"
check "media link for owner"    200 '"url":"/api/v1/uploads/' "${A[@]}" "$BASE/uploads/$CUT/url"
MEDIA="$(field url)"
check "cut streams via link"    206 ''                   -H 'Range: bytes=0-99' "${BASE%/api/v1}$MEDIA"
check "unsigned media refused"  403 '"error"'            "$BASE/uploads/$CUT/content"
check "pin a note"              201 '"client_notes":\[{'  "${A[@]}" -H "$JSON" -d '{"t":3,"text":"Cut this pause"}' "$BASE/orders/$ORDER/notes"
check "approve"                 200 '"amount_inr":1071.43' "${A[@]}" -X POST "$BASE/orders/$ORDER/approve"
grep -q '"fee_usd":2.25' "$TMP/body" && grep -q '"transfer_id":"RAMP-SIM-' "$TMP/body" \
  && echo "PASS  payout breakdown (fee, Ramp transfer id)" || { echo "FAIL  payout breakdown"; FAILED=1; }
check "approve twice is 409"    409 '"error"'            "${A[@]}" -X POST "$BASE/orders/$ORDER/approve"
check "orders list"             200 "\"id\":\"$ORDER\""  "${A[@]}" "$BASE/orders"

# ---- Isolation: user B sees none of user A's data
if [[ "$AUTH_MODE" == "firebase" ]]; then
  check "B can't read A's order"  404 '"error"'          "${B[@]}" "$BASE/orders/$ORDER"
  check "B's order list is empty" 200 '^\[\]$'           "${B[@]}" "$BASE/orders"
  check "B can't get A's media"   404 '"error"'          "${B[@]}" "$BASE/uploads/$CUT/url"
  check "B can't approve A's order" 404 '"error"'        "${B[@]}" -X POST "$BASE/orders/$ORDER/approve"
fi

# ---- Real Gemini calls, only when a clip is given
if [[ -n "${SMOKE_CLIP:-}" ]]; then
  check "upload real clip"      201 '"id":"up_'      "${A[@]}" -F "file=@$SMOKE_CLIP" -F kind=raw "$BASE/uploads"
  UP_ID="$(id_from_body up_)"
  check "brief from real clip"  201 '"best_moments"' "${A[@]}" -H "$JSON" \
    -d "{\"upload_ids\":[\"$UP_ID\"],\"client_note\":\"Short reel, fun and fast, 30 seconds\"}" "$BASE/briefs"
  BR_ID="$(id_from_body br_)"
  check "get the brief"         200 '"result"'       "${A[@]}" "$BASE/briefs/$BR_ID"
  check "recommended editors"   200 '"id":"mustafa"' "${A[@]}" "$BASE/editors/recommended?brief_id=$BR_ID"
  check "order with the brief"  201 '"brief_id"'     "${A[@]}" -H "$JSON" -d "{\"editor_id\":\"mustafa\",\"package_id\":\"reel\",\"brief_id\":\"$BR_ID\"}" "$BASE/orders"
  ORDER2="$(id_from_body BMT-)"
  check "upload real cut"       201 '"kind":"cut"'   "${A[@]}" -F "file=@$SMOKE_CLIP" -F kind=cut "$BASE/uploads"
  CUT2="$(id_from_body up_)"
  check "deliver real cut"      200 '"status":"review"' "${A[@]}" -H "$JSON" -d "{\"cut_upload_id\":\"$CUT2\"}" "$BASE/orders/$ORDER2/deliver"
  check "AI review"             200 '"overall_match"' "${A[@]}" -H "$JSON" -d '{}' "$BASE/orders/$ORDER2/review"
  check "feedback into notes"   200 '"source":"client"' "${A[@]}" -H "$JSON" -d '{"client_feedback":"make it more cinematic"}' "$BASE/orders/$ORDER2/review"
else
  echo "SKIP  Gemini checks (set SMOKE_CLIP=path/to/clip.mp4)"
fi

exit "$FAILED"
