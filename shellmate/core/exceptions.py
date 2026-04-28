class AgentError(Exception):
    """Base exception for all ShellMate errors."""


class WorkflowNotFound(AgentError):
    """No registered workflow matched the incoming task."""


class Unauthorized(AgentError):
    """User is not authorized to perform this action."""


class ToolExecutionError(AgentError):
    """An execution tool failed."""


class InvalidStateTransition(AgentError):
    """Attempted an illegal state machine transition."""
