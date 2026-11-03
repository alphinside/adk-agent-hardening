#!/usr/bin/env bash
# Scope Every Call to the Caller: fills in the plugin that checks each tool call
# against the session's user ID.
set -euo pipefail
cd "$(dirname "$0")/.."
cp solution/files/scope_plugin.py wallet_agent/scope_plugin.py
uv run python -W ignore -c "from wallet_agent.agent import app"
echo "Plugin in place. Restart adk web to load it."
