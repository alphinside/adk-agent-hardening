# Lab 1 solution

Everything the codelab changes, one script per step. If a step goes wrong, or Antigravity CLI gets stuck or runs out of quota, run that step's script from the folder that holds `pyproject.toml`, and carry on.

| Step | Run | What it does |
|---|---|---|
| Tell the Agent No: add the rule | `solution/1-add-prompt-rule.sh` | Adds "Never modify or delete data." to `INSTRUCTION` |
| Tell the Agent No: remove it | `solution/1-remove-prompt-rule.sh` | Puts `wallet_agent/agent.py` back as cloned |
| Make the Tool the Boundary | `solution/2-tools.sh` | Replaces `mcp-toolbox/tools.yaml`: no `execute_sql`, a new `get_transfers`, a read-only source. Restarts MCP Toolbox |
| Scope Every Call to the Caller | `solution/3-scope.sh` | Replaces `wallet_agent/scope_plugin.py` with the finished plugin |
| Screen with Model Armor | `solution/4-model-armor.sh` | Replaces `wallet_agent/model_armor_plugin.py` with the finished plugin, and `wallet_agent/agent.py` with one that attaches it and masks account numbers |

Every script is safe to rerun. After 1, 2, 3 or 4, restart `adk web` so the agent loads the change.

The scripts expect the steps in order. To catch up from the start, run them in order, skipping the two `1-` scripts.

`files/` holds the finished files the scripts copy, so you can compare yours with them:

| File | Becomes |
|---|---|
| `files/agent.with-prompt-rule.py` | `wallet_agent/agent.py` with the prompt rule |
| `files/agent.cloned.py` | `wallet_agent/agent.py` as cloned |
| `files/agent.model-armor.py` | `wallet_agent/agent.py` at the end |
| `files/tools.yaml` | `mcp-toolbox/tools.yaml` at the end |
| `files/scope_plugin.py` | `wallet_agent/scope_plugin.py` at the end |
| `files/model_armor_plugin.py` | `wallet_agent/model_armor_plugin.py` at the end |
