#!/usr/bin/env bash
# Tell the Agent No: adds "Never modify or delete data." to the instruction.
set -euo pipefail
cd "$(dirname "$0")/.."
cp solution/files/agent.with-prompt-rule.py wallet_agent/agent.py
echo "Prompt rule added to wallet_agent/agent.py. Restart adk web to load it."
