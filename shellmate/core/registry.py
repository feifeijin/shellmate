from .interfaces import ExecutionTool, WorkflowProvider
from .exceptions import WorkflowNotFound


class PluginRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ExecutionTool] = {}
        self._workflows: list[WorkflowProvider] = []

    def register_tool(self, tool: ExecutionTool) -> None:
        self._tools[tool.name] = tool

    def register_workflow(self, workflow: WorkflowProvider) -> None:
        self._workflows.append(workflow)

    def get_tool(self, name: str) -> ExecutionTool:
        tool = self._tools.get(name)
        if tool is None:
            raise KeyError(f"No tool registered with name '{name}'. "
                           f"Available: {list(self._tools)}")
        return tool

    def resolve_workflow(self, context) -> WorkflowProvider:
        for workflow in self._workflows:
            if workflow.matches(context):
                return workflow
        raise WorkflowNotFound(
            f"No workflow matched input: {context.raw_input!r}"
        )

    @property
    def tools(self) -> list[ExecutionTool]:
        return list(self._tools.values())

    @property
    def workflows(self) -> list[WorkflowProvider]:
        return list(self._workflows)
