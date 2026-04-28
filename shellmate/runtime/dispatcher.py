import logging
from shellmate.core.models import TaskContext, TaskState
from shellmate.core.registry import PluginRegistry
from shellmate.core.exceptions import WorkflowNotFound
from .session_manager import SessionManager
from .state_machine import StateMachine
from .approval_gate import ApprovalGate

log = logging.getLogger(__name__)


class Dispatcher:
    """Orchestrates the full task lifecycle from received → done/failed."""

    def __init__(
        self,
        registry: PluginRegistry,
        sessions: SessionManager,
        state_machine: StateMachine,
        approval_gate: ApprovalGate,
        workdir: str = ".",
    ) -> None:
        self._registry = registry
        self._sessions = sessions
        self._sm = state_machine
        self._gate = approval_gate
        self._workdir = workdir

    async def dispatch(self, context: TaskContext) -> str:
        """
        Full task lifecycle. Returns the final human-readable outcome message.
        """
        session = self._sessions.create(context)

        # PLANNING
        self._sm.validate(session.state, TaskState.PLANNING)
        self._sessions.transition(session, TaskState.PLANNING)

        try:
            workflow = self._registry.resolve_workflow(context)
            context.workflow_name = workflow.name
            prompt = await workflow.build_prompt(context)
            session.built_prompt = prompt
        except WorkflowNotFound as e:
            self._sessions.transition(session, TaskState.CANCELLED)
            return str(e)

        # AWAITING_APPROVAL (if workflow requires it)
        if workflow.requires_approval:
            self._sm.validate(session.state, TaskState.AWAITING_APPROVAL)
            self._sessions.transition(session, TaskState.AWAITING_APPROVAL)

            plan_summary = f"Plan for task `{context.task_id}`:\n{prompt[:500]}..."
            future = self._gate.register(session)
            log.info("Session %s awaiting approval", session.session_id)
            approved = await future

            if not approved:
                self._sessions.transition(session, TaskState.CANCELLED)
                return "Task cancelled by user."

        # EXECUTING
        self._sm.validate(session.state, TaskState.EXECUTING)
        self._sessions.transition(session, TaskState.EXECUTING)

        try:
            tool = self._registry.get_tool(workflow.tool_name)
            result = await tool.execute(prompt, self._workdir)
            session.result = result
        except Exception as e:
            self._sessions.transition(session, TaskState.FAILED)
            msg = await workflow.on_failure(context, str(e))
            log.error("Task %s failed: %s", context.task_id, e)
            return msg

        if not result.success:
            self._sessions.transition(session, TaskState.FAILED)
            msg = await workflow.on_failure(context, result.output)
            return msg

        self._sessions.transition(session, TaskState.DONE)
        return await workflow.on_success(context, result)
