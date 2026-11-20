#!/usr/bin/env bash
# Deploy BMT to Cloud Run as one service (API + frontend).
#
# Needs: gcloud signed in, the project from docs/HAPPY_PATH.md set up, and frontend/ cloned
# next to backend/. Run from backend/:
#
#   GCP_PROJECT=my-project GCS_BUCKET=bmt-uploads-xyz bash scripts/deploy.sh
#
# Secrets come from Secret Manager (create them once):
#   gemini-api-key     AI Studio key: Gemma screening always uses it (Gemma on Vertex would
#                      need its own endpoint); Gemini uses it too when USE_VERTEX=false
#   media-signing-key  any long random string, e.g. `openssl rand -hex 32`
set -euo pipefail
cd "$(dirname "$0")/.."

: "${GCP_PROJECT:?set GCP_PROJECT}"
REGION="${REGION:-asia-south1}"
VERTEX_LOCATION="${VERTEX_LOCATION:-us-central1}"
SERVICE="${SERVICE:-bmt}"
SERVICE_ACCOUNT="${SERVICE_ACCOUNT:-bmt-run@${GCP_PROJECT}.iam.gserviceaccount.com}"
USE_VERTEX="${USE_VERTEX:-true}"
STORAGE="${STORAGE:-gcs}"
DB="${DB:-firestore}"
GCS_BUCKET="${GCS_BUCKET:-}"
FAST_MODEL="${GEMINI_FAST_MODEL:-gemini-3.8-flash}"
PRO_MODEL="${GEMINI_PRO_MODEL:-gemini-3.8-flash}"
SCREEN_MODEL="${GEMINI_SCREEN_MODEL:-gemma-4-26b-a4b-it}"
IMAGE_MODEL="${GEMINI_IMAGE_MODEL:-gemini-3.1-flash-image}"
FIREBASE_API_KEY="${FIREBASE_API_KEY:-}"

[ -d ../frontend ] || { echo "frontend/ must be cloned next to backend/"; exit 1; }
[ "$STORAGE" != "gcs" ] || [ -n "$GCS_BUCKET" ] || { echo "set GCS_BUCKET (or STORAGE=local)"; exit 1; }

STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT
mkdir -p "$STAGE/backend" "$STAGE/frontend"
tar --exclude=.git --exclude=.venv --exclude=data --exclude=.env --exclude=__pycache__ -cf - . | tar -xf - -C "$STAGE/backend"
(cd ../frontend && tar --exclude=.git -cf - .) | tar -xf - -C "$STAGE/frontend"
cp deploy/Dockerfile deploy/.dockerignore "$STAGE/"

ENV_VARS="USE_VERTEX=${USE_VERTEX},GCP_PROJECT=${GCP_PROJECT},VERTEX_LOCATION=${VERTEX_LOCATION}"
ENV_VARS+=",STORAGE=${STORAGE},GCS_BUCKET=${GCS_BUCKET},DB=${DB},AUTH=firebase,FIREBASE_API_KEY=${FIREBASE_API_KEY}"
ENV_VARS+=",GEMINI_FAST_MODEL=${FAST_MODEL},GEMINI_PRO_MODEL=${PRO_MODEL}"
ENV_VARS+=",GEMINI_SCREEN_MODEL=${SCREEN_MODEL},GEMINI_IMAGE_MODEL=${IMAGE_MODEL}"
ENV_VARS+=",AI_TIMEOUT_SEC=120,MAX_UPLOAD_MB=30"
SECRETS="MEDIA_SIGNING_KEY=media-signing-key:latest,GEMINI_API_KEY=gemini-api-key:latest"

gcloud run deploy "$SERVICE" \
  --project "$GCP_PROJECT" --region "$REGION" --source "$STAGE" \
  --service-account "$SERVICE_ACCOUNT" \
  --allow-unauthenticated \
  --min-instances 1 --max-instances 2 --memory 1Gi --timeout 300 \
  --set-env-vars "$ENV_VARS" --set-secrets "$SECRETS"
