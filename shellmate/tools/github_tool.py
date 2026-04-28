import asyncio
import json
import logging
from shellmate.core.exceptions import ToolExecutionError

log = logging.getLogger(__name__)


class GitHubTool:
    """Thin wrapper around the `gh` CLI. Not an ExecutionTool — used by workflows."""

    def __init__(self, repo: str, token: str | None = None) -> None:
        self._repo = repo
        self._env = {"GH_TOKEN": token} if token else {}

    async def _run(self, *args: str) -> str:
        import os
        env = {**os.environ, **self._env}
        proc = await asyncio.create_subprocess_exec(
            "gh", *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise ToolExecutionError(f"gh {' '.join(args)} failed: {stderr.decode()}")
        return stdout.decode().strip()

    async def get_issue(self, number: int) -> dict:
        raw = await self._run(
            "issue", "view", str(number),
            "--repo", self._repo,
            "--json", "number,title,body",
        )
        return json.loads(raw)

    async def create_pr(self, title: str, body: str, head: str, base: str = "main") -> str:
        """Returns the PR URL."""
        return await self._run(
            "pr", "create",
            "--repo", self._repo,
            "--title", title,
            "--body", body,
            "--head", head,
            "--base", base,
        )

    async def list_issues(self, state: str = "open", limit: int = 10) -> list[dict]:
        raw = await self._run(
            "issue", "list",
            "--repo", self._repo,
            "--state", state,
            "--limit", str(limit),
            "--json", "number,title,state",
        )
        return json.loads(raw)

    async def list_runs(self, workflow: str | None = None, limit: int = 5) -> list[dict]:
        args = ["run", "list", "--repo", self._repo, "--limit", str(limit), "--json",
                "databaseId,name,status,conclusion,createdAt"]
        if workflow:
            args += ["--workflow", workflow]
        raw = await self._run(*args)
        return json.loads(raw)
