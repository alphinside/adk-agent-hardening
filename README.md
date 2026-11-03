# [Codelab Starter] Untrusted by Default: Securing ADK Agents with MCP Toolbox and Model Armor

The starter project for the Untrusted by Default codelab. You harden a customer support agent for Cymbal Wallet, a fictional digital wallet app. The agent is built with the Agent Development Kit (ADK) and reads BigQuery through MCP Toolbox.

The agent here works, and it is deliberately open:

- MCP Toolbox runs BigQuery queries as you, so the agent can read any table you can.
- `execute_sql` accepts any GoogleSQL statement, including `DELETE`.
- Nothing checks whose account a tool call asks for.
- Nothing screens what goes into the model or what comes out of it.

The codelab will guide you on how to address those issues

## Requirements

- A Google Cloud project with billing enabled

## Run it

From Cloud Shell, in this folder:

```bash
cp .env.example .env
sed -i "s/your-project-id/$(gcloud config get-value project)/" .env # Setup the .env with your project id
scripts/setup.sh            # APIs, data, Model Armor template, dependencies, MCP Toolbox
uv run adk web              # dev UI on port 8000, open it with Web Preview
```

MCP Toolbox will running in the background on 127.0.0.1:5000; Run `scripts/toolbox.sh status` to check it.

Open `/dev-ui/?app=wallet_agent&userId=cust_0001` to chat as a customer. Change `userId` to `support_0001` to chat as support staff.

## Files

| Path | What it is |
|---|---|
| `wallet_agent/agent.py` | The agent, its instruction, the reply hook and the plugin registration |
| `wallet_agent/scope_plugin.py` | Caller-scope plugin. Its callback is a `TODO` until module 3 |
| `wallet_agent/model_armor_plugin.py` | Model Armor plugin, not attached yet. One `TODO` until module 4 |
| `mcp-toolbox/tools.yaml` | The BigQuery source and the tools the agent can call |
| `data/seed.sql` | The synthetic Cymbal Wallet data `setup.sh` loads into BigQuery |
| `scripts/setup.sh` | One-time setup. Rerunning it also resets the data |
| `scripts/toolbox.sh` | `start`, `restart`, `stop`, or `status` for MCP Toolbox |
| `scripts/check.sh` | Prints `READY` or names what is missing |
| `scripts/cleanup.sh` | Deletes what the lab created |
| `solution/` | Finished files and one catch-up script per step. See its README |

The finished version of every file is in [solution/](solution/), with one script per codelab step. If a step goes wrong, run its script and carry on: `solution/2-tools.sh`, for example.

## The data

Everything in `data/seed.sql` is mock data intended for the codelab tutorial

## Clean up

When you finish, run `scripts/cleanup.sh`, or delete the project.
