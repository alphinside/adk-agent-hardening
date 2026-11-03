#!/usr/bin/env bash
# Checks that the lab is ready to run and names anything that is missing.
#   scripts/check.sh              everything, including MCP Toolbox
#   scripts/check.sh --no-toolbox skip the MCP Toolbox check
set -uo pipefail
cd "$(dirname "$0")/.."

problems=()
if [[ ! -f .env ]]; then
  echo "NOT READY: no .env file in $(pwd)."
  exit 1
fi
set -a; source .env; set +a

enabled=$(gcloud services list --enabled --project="$GOOGLE_CLOUD_PROJECT" \
  --format='value(config.name)' 2>/dev/null)
for api in aiplatform bigquery iamcredentials modelarmor; do
  grep -qx "$api.googleapis.com" <<<"$enabled" ||
    problems+=("API $api.googleapis.com is not enabled. Run scripts/setup.sh.")
done

for table in wallet_support.transactions wallet_support.fraud_rules; do
  bq --project_id="$GOOGLE_CLOUD_PROJECT" show "$table" &>/dev/null ||
    problems+=("BigQuery table $table is missing. Run scripts/setup.sh.")
done

gcloud model-armor templates describe "$MODEL_ARMOR_TEMPLATE_ID" --location="$GOOGLE_CLOUD_LOCATION" \
  --project="$GOOGLE_CLOUD_PROJECT" &>/dev/null ||
  problems+=("Model Armor template $MODEL_ARMOR_TEMPLATE_ID is missing. Run scripts/setup.sh.")

[[ -d .venv ]] || problems+=("Python dependencies are not installed. Run scripts/setup.sh.")

if [[ "${1:-}" != "--no-toolbox" ]]; then
  # Calls one tool through MCP Toolbox, which proves the whole path to BigQuery.
  reply=$(curl -s -X POST "$TOOLBOX_URL/mcp" -H 'Content-Type: application/json' \
    -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"get_customer_profile","arguments":{"customer_id":"cust_0001"}}}')
  if [[ -z "$reply" ]]; then
    problems+=("MCP Toolbox is not answering at $TOOLBOX_URL. Run scripts/toolbox.sh start.")
  elif ! grep -q "Maya Torres" <<<"$reply"; then
    problems+=("MCP Toolbox answered, but could not read BigQuery: ${reply:0:300}")
  fi
fi

if (( ${#problems[@]} )); then
  echo "NOT READY:"
  printf '  - %s\n' "${problems[@]}"
  exit 1
fi
echo "READY"
