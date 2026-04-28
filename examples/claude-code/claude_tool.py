"""
Example: ExecutionTool adapter for Claude Code CLI.

Copy this file into your private project and register it:
    platform.register_tool(ClaudeCodeTool())
"""
import asyncio
import logging
from shellmate.core.interfaces import ExecutionTool
from shellmate.core.models import TaskResult

log = logging.getLogger(__name__)


class ClaudeCodeTool(ExecutionTool):
    """Runs `claude --dangerously-skip-permissions -p <prompt>` in a subprocess."""

    name = "claude-code"

    def __init__(self, timeout: int = 900) -> None:
        self._timeout = timeout

    async def execute(self, prompt: str, workdir: str) -> TaskResult:
        log.info("ClaudeCodeTool executing in %s (timeout=%ds)", workdir, self._timeout)
        try:
            proc = await asyncio.create_subprocess_exec(
                "claude", "--dangerously-skip-permissions", "-p", prompt,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                cwd=workdir,
            )
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=self._timeout)
            output = stdout.decode(errors="replace")
            return TaskResult(success=proc.returncode == 0, output=output)
        except asyncio.TimeoutError:
            return TaskResult(success=False, output=f"Claude timed out after {self._timeout}s")
        except FileNotFoundError:
            return TaskResult(success=False, output="claude CLI not found. Is it installed?")
