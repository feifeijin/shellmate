"""
Minimal example: Telegram bot with Claude Code + GitHub issue workflow.

1. Copy this file to your private project.
2. Create your own WorkflowProvider subclass with project-specific instructions.
3. Add secrets to .env (never commit it).
4. Run: python main.py
"""
from dotenv import load_dotenv
load_dotenv()

from shellmate import AgentPlatform
from shellmate.workflows import GitHubIssueWorkflow
from claude_tool import ClaudeCodeTool
import os


class MyProjectWorkflow(GitHubIssueWorkflow):
    """Override build_system_context() to inject your project conventions."""

    def build_system_context(self, context) -> str:
        return (
            "You are working on MyProject.\n"
            "Follow the project conventions in CLAUDE.md.\n"
            # Add project-specific instructions here — never put these in the public repo.
        )


platform = AgentPlatform.from_env()
platform.register_tool(ClaudeCodeTool())
platform.register_workflow(
    MyProjectWorkflow(
        repo=os.environ["GITHUB_REPO"],
        gh_token=os.environ["GITHUB_TOKEN"],
        tool_name="claude-code",
    )
)

platform.run()
