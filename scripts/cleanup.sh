#!/usr/bin/env bash
# Deletes what this lab created in your project. No other lab depends on it.
set -uo pipefail
cd "$(dirname "$0")/.."
set -a; source .env; set +a

scripts/toolbox.sh stop
gcloud model-armor templates delete "${MODEL_ARMOR_TEMPLATE_ID:-wallet-agent-armor}" \
  --location="$GOOGLE_CLOUD_LOCATION" --project="$GOOGLE_CLOUD_PROJECT" --quiet
bq --project_id="$GOOGLE_CLOUD_PROJECT" rm -r -f -d wallet_support
