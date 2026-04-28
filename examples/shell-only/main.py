"""
Minimal example: shell-only bot, no AI, no GitHub.
Run a shell command via Telegram: /task echo hello
"""
from dotenv import load_dotenv
load_dotenv()

import re
from shellmate import AgentPlatform
from shellmate.core.interfaces import WorkflowProvider
from shellmate.core.models import TaskContext, TaskResult


class EchoWorkflow(WorkflowProvider):
    name = "echo"

    def matches(self, context: TaskContext) -> bool:
        return True  # catch-all

    async def build_prompt(self, context: TaskContext) -> str:
        # Sanitize: only allow alphanumeric + basic punctuation
        safe = re.sub(r"[^a-zA-Z0-9 .,!?_\-]", "", context.raw_input)
        return f"echo '{safe}'"

    async def on_success(self, context: TaskContext, result: TaskResult) -> str:
        return result.output.strip()


platform = AgentPlatform.from_env()
platform.register_workflow(EchoWorkflow())
platform.run()
