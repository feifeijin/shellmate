import asyncio
import logging
from shellmate.core.exceptions import ToolExecutionError

log = logging.getLogger(__name__)


class GitTool:
    """Helper for common git operations. Not an ExecutionTool — used by workflows."""

    def __init__(self, workdir: str) -> None:
        self._workdir = workdir

    async def run(self, *args: str) -> str:
        cmd = ["git", *args]
        log.debug("git %s", " ".join(args))
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self._workdir,
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise ToolExecutionError(f"git {' '.join(args)} failed: {stderr.decode()}")
        return stdout.decode().strip()

    async def checkout_branch(self, branch: str) -> None:
        await self.run("checkout", "-b", branch)

    async def add_all(self) -> None:
        await self.run("add", "-A")

    async def commit(self, message: str) -> None:
        await self.run("commit", "-m", message)

    async def push(self, remote: str, branch: str) -> None:
        await self.run("push", remote, branch)

    async def current_branch(self) -> str:
        return await self.run("rev-parse", "--abbrev-ref", "HEAD")
