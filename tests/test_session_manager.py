import pytest
from shellmate.runtime.session_manager import SessionManager
from shellmate.core.models import TaskContext, TaskState


def _ctx(raw="test task"):
    return TaskContext(task_id="t1", raw_input=raw, user_id="u1")


def test_create_and_get():
    sm = SessionManager()
    s = sm.create(_ctx())
    assert sm.get(s.session_id) is s
    assert s.state == TaskState.RECEIVED


def test_get_by_user_returns_active():
    sm = SessionManager()
    s = sm.create(_ctx())
    assert sm.get_by_user("u1") is s


def test_get_by_user_ignores_terminal():
    sm = SessionManager()
    s = sm.create(_ctx())
    sm.transition(s, TaskState.DONE)
    assert sm.get_by_user("u1") is None


def test_transition_logs():
    sm = SessionManager()
    s = sm.create(_ctx())
    sm.transition(s, TaskState.PLANNING)
    assert s.state == TaskState.PLANNING
    assert any("planning" in entry for entry in s.history)
