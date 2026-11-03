#!/usr/bin/env bash
# Screen with Model Armor: finishes the Model Armor plugin and attaches it,
# and fills in the hook that masks account numbers.
set -euo pipefail
cd "$(dirname "$0")/.."
cp solution/files/model_armor_plugin.py wallet_agent/model_armor_plugin.py
cp solution/files/agent.model-armor.py wallet_agent/agent.py
set -a; source .env; set +a
uv run python -W ignore -c "from wallet_agent.agent import app"
echo "Model Armor plugin attached. Restart adk web to load it."
