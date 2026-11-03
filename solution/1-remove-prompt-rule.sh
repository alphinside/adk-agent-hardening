#!/usr/bin/env bash
# Tell the Agent No: puts the instruction back as it was, without the prompt rule.
set -euo pipefail
cd "$(dirname "$0")/.."
cp solution/files/agent.cloned.py wallet_agent/agent.py
echo "Prompt rule removed from wallet_agent/agent.py. Restart adk web to load it."
