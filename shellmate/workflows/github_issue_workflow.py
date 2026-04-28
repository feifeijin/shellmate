import re
from shellmate.core.interfaces import WorkflowProvider
from shellmate.core.models import TaskContext, TaskResult
from shellmate.tools.github_tool import GitHubTool


class GitHubIssueWorkflow(WorkflowProvider):
    """
    Generic workflow: fetch a GitHub issue and ask the execution tool to implement it.

    Matches inputs like: "issue 42", "#42", "implement issue 42".
    Subclass and override `build_system_context()` to inject project-specific instructions.
    """

    name = "github-issue"

    _PATTERN = re.compile(r"(?:issue\s*#?|#)(\d+)", re.IGNORECASE)

    def __init__(self, repo: str, gh_token: str | None = None, tool_name: str = "shell") -> None:
        self._repo = repo
        self._gh = GitHubTool(repo, gh_token)
        self._tool_name = tool_name

    @property
    def tool_name(self) -> str:
        return self._tool_name

    def matches(self, context: TaskContext) -> bool:
        return bool(self._PATTERN.search(context.raw_input))

    async def build_prompt(self, context: TaskContext) -> str:
        m = self._PATTERN.search(context.raw_input)
        issue_number = int(m.group(1))
        issue = await self._gh.get_issue(issue_number)
        context.metadata["issue_number"] = issue_number
        context.metadata["issue_title"] = issue["title"]

        system_ctx = self.build_system_context(context)
        branch = self._branch_name(issue_number, issue["title"])
        context.metadata["branch"] = branch

        return (
            f"{system_ctx}\n\n"
            f"GitHub Issue #{issue_number}: {issue['title']}\n\n"
            f"{issue.get('body') or '(no description)'}\n\n"
            f"Tasks:\n"
            f"1. Read relevant source files to understand the context.\n"
            f"2. Create branch: git checkout -b {branch}\n"
            f"3. Implement the change.\n"
            f"4. Commit: git add -A && git commit -m 'feat: {issue['title']} (#{issue_number})'\n"
            f"5. Push: git push origin {branch}\n"
            f"6. Create PR: gh pr create --title '{issue['title']}' "
            f"--body 'Closes #{issue_number}' --head {branch}\n"
            f"7. Print ONLY the PR URL as the last line of output."
        )

    def build_system_context(self, context: TaskContext) -> str:
        """Override in subclass to add project-specific instructions."""
        return "You are an AI coding assistant. Implement the following GitHub issue."

    async def on_success(self, context: TaskContext, result: TaskResult) -> str:
        pr_url = self._extract_pr_url(result.output)
        issue_num = context.metadata.get("issue_number", "?")
        title = context.metadata.get("issue_title", "")
        if pr_url:
            return f"Done issue #{issue_num}: {title}\nPR: {pr_url}"
        return f"Done issue #{issue_num}: {title}\n(PR URL not found in output)"

    async def on_failure(self, context: TaskContext, error: str) -> str:
        issue_num = context.metadata.get("issue_number", "?")
        return f"Failed on issue #{issue_num}: {error[:300]}"

    @staticmethod
    def _branch_name(number: int, title: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:40].rstrip("-")
        return f"feature/issue-{number}-{slug}"

    @staticmethod
    def _extract_pr_url(output: str) -> str:
        match = re.search(r"https://github\.com/[^\s]+/pull/\d+", output)
        return match.group(0) if match else ""
