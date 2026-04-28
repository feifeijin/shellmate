import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from shellmate.core.models import TaskContext, TaskResult
from shellmate.core.registry import PluginRegistry
from shellmate.core.interfaces import WorkflowProvider, ExecutionTool
from shellmate.runtime.session_manager import SessionManager
from shellmate.runtime.state_machine import StateMachine
from shellmate.runtime.dispatcher import Dispatcher
from shellmate.runtime.approval_gate import ApprovalGate


class _FakeWorkflow(WorkflowProvider):
    name = "fake"
    tool_name = "fake-tool"

    def matches(self, ctx): return True
    async def build_prompt(self, ctx): return "do the thing"
    async def on_success(self, ctx, result): return f"ok: {result.output}"


class _FakeTool(ExecutionTool):
    name = "fake-tool"
    async def execute(self, prompt, workdir): return TaskResult(success=True, output="done")


@pytest.fixture
def dispatcher():
    reg = PluginRegistry()
    reg.register_tool(_FakeTool())
    reg.register_workflow(_FakeWorkflow())
    return Dispatcher(reg, SessionManager(), StateMachine(), ApprovalGate(), workdir=".")


def test_dispatch_success(dispatcher):
    ctx = TaskContext(task_id="x", raw_input="do something", user_id="u1")
    result = asyncio.run(dispatcher.dispatch(ctx))
    assert "ok:" in result


def test_dispatch_no_workflow():
    reg = PluginRegistry()
    reg.register_tool(_FakeTool())
    d = Dispatcher(reg, SessionManager(), StateMachine(), ApprovalGate(), workdir=".")
    ctx = TaskContext(task_id="x", raw_input="anything", user_id="u1")
    result = asyncio.run(d.dispatch(ctx))
    assert "No workflow" in result
