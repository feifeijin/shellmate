# ShellMate

A modular, open-source AI Task Agent Platform controlled via Telegram.

Send a task from Telegram → a workflow builds a prompt → an execution tool runs it → you get a notification.

## Features

- Pluggable **WorkflowProvider** — define what a task means and how to prompt the AI
- Pluggable **ExecutionTool** — run Claude Code, a shell script, or any custom tool
- Pluggable **AuthProvider** — allowlist, OAuth, or anything else
- Optional **human approval gate** — pause before executing and ask for confirmation
- Full **session state machine** — received → planning → executing → done/failed
- Telegram webhook or polling mode
- CLI runner for local testing

## Quickstart

```bash
pip install shellmate
cp .env.example .env  # fill in TELEGRAM_BOT_TOKEN and ALLOWED_USER_IDS
```

```python
# main.py
from dotenv import load_dotenv; load_dotenv()
from shellmate import AgentPlatform
from shellmate.tools import ShellTool
from shellmate.workflows import GitHubIssueWorkflow
import os

platform = AgentPlatform.from_env()
platform.register_workflow(
    GitHubIssueWorkflow(repo=os.environ["GITHUB_REPO"])
)
platform.run()
```

Then in Telegram: `/task issue 42`

## Writing your own tool

See [docs/PLUGINS.md](docs/PLUGINS.md).

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Deployment

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

## License

MIT
