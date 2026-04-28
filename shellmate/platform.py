"""
Top-level AgentPlatform: wires all layers together.
"""
import logging
import os
from shellmate.core.interfaces import ExecutionTool, WorkflowProvider, AuthProvider
from shellmate.core.registry import PluginRegistry
from shellmate.runtime.session_manager import SessionManager
from shellmate.runtime.state_machine import StateMachine
from shellmate.runtime.dispatcher import Dispatcher
from shellmate.runtime.approval_gate import ApprovalGate
from shellmate.auth import AllowlistAuthProvider
from shellmate.tools import ShellTool

log = logging.getLogger(__name__)


class AgentPlatform:
    def __init__(
        self,
        token: str,
        auth: AuthProvider,
        workdir: str = ".",
        webhook_url: str | None = None,
        port: int = 8080,
    ) -> None:
        self._token = token
        self._auth = auth
        self._workdir = workdir
        self._webhook_url = webhook_url
        self._port = port

        self._registry = PluginRegistry()
        self._sessions = SessionManager()
        self._sm = StateMachine()
        self._gate = ApprovalGate()
        self._dispatcher = Dispatcher(
            self._registry, self._sessions, self._sm, self._gate, workdir
        )

        # Register default shell tool
        self._registry.register_tool(ShellTool())

    @classmethod
    def from_env(cls) -> "AgentPlatform":
        return cls(
            token=os.environ["TELEGRAM_BOT_TOKEN"],
            auth=AllowlistAuthProvider.from_env("ALLOWED_USER_IDS"),
            workdir=os.environ.get("AGENT_WORKDIR", "."),
            webhook_url=os.environ.get("WEBHOOK_BASE_URL"),
            port=int(os.environ.get("WEBHOOK_PORT", "8080")),
        )

    def register_tool(self, tool: ExecutionTool) -> "AgentPlatform":
        self._registry.register_tool(tool)
        return self

    def register_workflow(self, workflow: WorkflowProvider) -> "AgentPlatform":
        self._registry.register_workflow(workflow)
        return self

    def run(self) -> None:
        from shellmate.interfaces.telegram.bot import build_app, run_webhook, run_polling

        logging.basicConfig(
            format="%(asctime)s %(levelname)s %(name)s: %(message)s",
            level=logging.INFO,
        )
        logging.getLogger("httpx").setLevel(logging.WARNING)

        app = build_app(
            token=self._token,
            dispatcher=self._dispatcher,
            sessions=self._sessions,
            gate=self._gate,
            auth=self._auth,
        )

        if self._webhook_url:
            run_webhook(app, self._webhook_url, self._port)
        else:
            run_polling(app)
