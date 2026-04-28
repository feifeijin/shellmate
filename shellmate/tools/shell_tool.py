import asyncio
import logging
from shellmate.core.interfaces import ExecutionTool
from shellmate.core.models import TaskResult

log = logging.getLogger(__name__)


class ShellTool(ExecutionTool):
    """
    Runs a shell script given as the prompt.
    The prompt is treated as a bash script — NOT passed via shell=True with user input.
    """

    name = "shell"

    def __init__(self, timeout: int = 300) -> None:
        self._timeout = timeout

    async def execute(self, prompt: str, workdir: str) -> TaskResult:
        log.info("ShellTool executing in %s", workdir)
        try:
            proc = await asyncio.create_subprocess_exec(
                "/bin/bash", "-c", prompt,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                cwd=workdir,
            )
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=self._timeout)
            output = stdout.decode(errors="replace")
            success = proc.returncode == 0
            return TaskResult(success=success, output=output)
        except asyncio.TimeoutError:
            return TaskResult(success=False, output=f"Timed out after {self._timeout}s")
        except Exception as e:
            return TaskResult(success=False, output=str(e))
