from shellmate.core.models import TaskState
from shellmate.core.exceptions import InvalidStateTransition

# Valid transitions: from_state → set of allowed to_states
_TRANSITIONS: dict[TaskState, set[TaskState]] = {
    TaskState.RECEIVED:          {TaskState.PLANNING, TaskState.CANCELLED},
    TaskState.PLANNING:          {TaskState.AWAITING_APPROVAL, TaskState.EXECUTING, TaskState.CANCELLED},
    TaskState.AWAITING_APPROVAL: {TaskState.EXECUTING, TaskState.CANCELLED},
    TaskState.EXECUTING:         {TaskState.DONE, TaskState.FAILED},
    TaskState.FAILED:            {TaskState.RETRYING, TaskState.CANCELLED},
    TaskState.RETRYING:          {TaskState.EXECUTING, TaskState.CANCELLED},
    TaskState.DONE:              set(),
    TaskState.CANCELLED:         set(),
}


class StateMachine:
    def validate(self, current: TaskState, target: TaskState) -> None:
        allowed = _TRANSITIONS.get(current, set())
        if target not in allowed:
            raise InvalidStateTransition(
                f"Cannot transition from {current.value!r} to {target.value!r}. "
                f"Allowed: {[s.value for s in allowed]}"
            )

    def can_transition(self, current: TaskState, target: TaskState) -> bool:
        return target in _TRANSITIONS.get(current, set())

    def is_terminal(self, state: TaskState) -> bool:
        return not _TRANSITIONS.get(state)
