# Writing Plugins

## Custom ExecutionTool

Implement the `ExecutionTool` ABC:

```python
from shellmate.core.interfaces import ExecutionTool
from shellmate.core.models import TaskResult

class MyTool(ExecutionTool):
    name = "my-tool"

    async def execute(self, prompt: str, workdir: str) -> TaskResult:
        # prompt is the fully-built string from WorkflowProvider.build_prompt()
        # workdir is the directory to operate in
        ...
        return TaskResult(success=True, output="done")
```

Register it: `platform.register_tool(MyTool())`

## Custom WorkflowProvider

```python
from shellmate.core.interfaces import WorkflowProvider
from shellmate.core.models import TaskContext, TaskResult

class MyWorkflow(WorkflowProvider):
    name = "my-workflow"
    tool_name = "my-tool"          # which ExecutionTool to use
    requires_approval = True       # pause for human approval before executing

    def matches(self, context: TaskContext) -> bool:
        return "deploy" in context.raw_input.lower()

    async def build_prompt(self, context: TaskContext) -> str:
        return f"Deploy the application. Input was: {context.raw_input}"

    async def on_success(self, context: TaskContext, result: TaskResult) -> str:
        return f"Deployed successfully.\n{result.output[:200]}"
```

Register it: `platform.register_workflow(MyWorkflow())`

## Extending GitHubIssueWorkflow

The most common pattern — override only `build_system_context()`:

```python
from shellmate.workflows import GitHubIssueWorkflow

class MyProjectWorkflow(GitHubIssueWorkflow):
    def build_system_context(self, context) -> str:
        return """
        You are working on MyProject (.NET 10, PostgreSQL).
        Follow Clean Architecture: Core → Infrastructure → UI.
        Run tests with: dotnet test MyProject.sln
        """
```

Keep this class in your **private** repo — it contains project-specific knowledge.
