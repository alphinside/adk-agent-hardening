#!/usr/bin/env bash
# Make the Tool the Boundary: removes execute_sql, adds get_transfers, and makes
# the BigQuery source read-only.
set -euo pipefail
cd "$(dirname "$0")/.."
cp solution/files/tools.yaml mcp-toolbox/tools.yaml
scripts/toolbox.sh restart
grep "tools:" toolbox.log | tail -n 1
echo "Restart adk web so the agent loads the new tool list."
