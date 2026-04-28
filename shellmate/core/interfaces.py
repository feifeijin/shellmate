from abc import ABC, abstractmethod
from .models import TaskContext, TaskResult


class ExecutionTool(ABC):
    """Runs the actual agent or shell command for a task."""

    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    async def execute(self, prompt: str, workdir: str) -> TaskResult: ...


class WorkflowProvider(ABC):
    """Decides whether it handles a task and builds its execution prompt."""

    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def matches(self, context: TaskContext) -> bool: ...

    @abstractmethod
    async def build_prompt(self, context: TaskContext) -> str: ...

    @abstractmethod
    async def on_success(self, context: TaskContext, result: TaskResult) -> str:
        """Returns a human-readable summary sent back to the user."""
        ...

    async def on_failure(self, context: TaskContext, error: str) -> str:
        return f"Task failed: {error}"

    @property
    def requires_approval(self) -> bool:
        """Override to True to pause and ask user before executing."""
        return False

    @property
    def tool_name(self) -> str:
        """Name of the ExecutionTool this workflow uses. Override to specify."""
        return "shell"


class AuthProvider(ABC):
    """Decides whether a user is allowed to perform an action."""

    @abstractmethod
    async def is_authorized(self, user_id: str, action: str) -> bool: ...


class NotificationChannel(ABC):
    """Sends messages back to the user."""

    @abstractmethod
    async def send(self, user_id: str, message: str) -> None: ...
