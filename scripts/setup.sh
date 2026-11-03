#!/usr/bin/env bash
# One-time setup for the lab: enables the APIs, loads the Cymbal Wallet data
# into BigQuery, creates the Model Armor template, installs the Python
# dependencies and starts MCP Toolbox. Safe to rerun; rerunning also resets
# the data.
set -euo pipefail
cd "$(dirname "$0")/.."

[[ -f .env ]] || { echo "No .env here. Create it first (see .env.example)." >&2; exit 1; }
set -a; source .env; set +a
: "${GOOGLE_CLOUD_PROJECT:?Set GOOGLE_CLOUD_PROJECT in .env}"
: "${GOOGLE_CLOUD_LOCATION:?Set GOOGLE_CLOUD_LOCATION in .env}"
: "${MODEL_ARMOR_TEMPLATE_ID:?Set MODEL_ARMOR_TEMPLATE_ID in .env}"

echo "Enabling APIs..."
gcloud services enable \
  aiplatform.googleapis.com \
  bigquery.googleapis.com \
  iamcredentials.googleapis.com \
  modelarmor.googleapis.com \
  --project="$GOOGLE_CLOUD_PROJECT"

echo "Loading data into BigQuery..."
bq --project_id="$GOOGLE_CLOUD_PROJECT" mk --force \
  --location="$GOOGLE_CLOUD_LOCATION" --dataset wallet_support >/dev/null
bq --project_id="$GOOGLE_CLOUD_PROJECT" --location="$GOOGLE_CLOUD_LOCATION" \
  query --nouse_legacy_sql --quiet < data/seed.sql >/dev/null

echo "Creating Model Armor template $MODEL_ARMOR_TEMPLATE_ID..."
# Prompt injection is set to high because lower levels flag plain questions
# such as "What bank accounts are linked to my wallet?". Sensitive Data
# Protection stays off: the agent masks account numbers itself.
gcloud model-armor templates describe "$MODEL_ARMOR_TEMPLATE_ID" \
  --location="$GOOGLE_CLOUD_LOCATION" --project="$GOOGLE_CLOUD_PROJECT" &>/dev/null ||
  gcloud model-armor templates create "$MODEL_ARMOR_TEMPLATE_ID" \
    --location="$GOOGLE_CLOUD_LOCATION" --project="$GOOGLE_CLOUD_PROJECT" \
    --pi-and-jailbreak-filter-settings-enforcement=enabled \
    --pi-and-jailbreak-filter-settings-confidence-level=high \
    --malicious-uri-filter-settings-enforcement=enabled \
    --rai-settings-filters=filterType=DANGEROUS,confidenceLevel=MEDIUM_AND_ABOVE \
    --rai-settings-filters=filterType=HARASSMENT,confidenceLevel=MEDIUM_AND_ABOVE \
    --quiet >/dev/null

echo "Installing Python dependencies..."
uv sync --quiet

scripts/toolbox.sh start
echo
scripts/check.sh
