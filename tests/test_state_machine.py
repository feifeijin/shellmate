import pytest
from shellmate.runtime.state_machine import StateMachine
from shellmate.core.models import TaskState
from shellmate.core.exceptions import InvalidStateTransition


sm = StateMachine()


def test_valid_transitions():
    sm.validate(TaskState.RECEIVED, TaskState.PLANNING)
    sm.validate(TaskState.PLANNING, TaskState.EXECUTING)
    sm.validate(TaskState.EXECUTING, TaskState.DONE)
    sm.validate(TaskState.EXECUTING, TaskState.FAILED)
    sm.validate(TaskState.FAILED, TaskState.RETRYING)


def test_invalid_transition_raises():
    with pytest.raises(InvalidStateTransition):
        sm.validate(TaskState.DONE, TaskState.EXECUTING)


def test_terminal_states():
    assert sm.is_terminal(TaskState.DONE)
    assert sm.is_terminal(TaskState.CANCELLED)
    assert not sm.is_terminal(TaskState.EXECUTING)


def test_can_transition():
    assert sm.can_transition(TaskState.PLANNING, TaskState.AWAITING_APPROVAL)
    assert not sm.can_transition(TaskState.DONE, TaskState.PLANNING)
