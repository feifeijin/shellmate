from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class TaskState(Enum):
    RECEIVED = "received"
    PLANNING = "planning"
    AWAITING_APPROVAL = "awaiting_approval"
    EXECUTING = "executing"
    DONE = "done"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


@dataclass
class TaskContext:
    task_id: str
    raw_input: str
    user_id: str
    workflow_name: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskResult:
    success: bool
    output: str
    artifacts: dict[str, Any] = field(default_factory=dict)


@dataclass
class Session:
    session_id: str
    user_id: str
    state: TaskState
    context: TaskContext
    history: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime | None = None
    built_prompt: str = ""
    result: TaskResult | None = None

    def log(self, entry: str) -> None:
        self.history.append(f"{datetime.now(timezone.utc).isoformat()} {entry}")
