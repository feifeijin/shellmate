import uuid
import logging
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes
from shellmate.core.models import TaskContext
from shellmate.core.interfaces import AuthProvider
from shellmate.runtime.dispatcher import Dispatcher
from shellmate.runtime.session_manager import SessionManager
from shellmate.runtime.approval_gate import ApprovalGate
from .middleware import restricted

log = logging.getLogger(__name__)


class TelegramHandlers:
    def __init__(
        self,
        dispatcher: Dispatcher,
        sessions: SessionManager,
        gate: ApprovalGate,
        auth: AuthProvider,
    ) -> None:
        self._dispatcher = dispatcher
        self._sessions = sessions
        self._gate = gate
        self._auth = auth

    def _guard(self, action: str = "telegram"):
        return restricted(self._auth, action)

    async def handle_task(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        raw = " ".join(context.args or []).strip()
        if not raw:
            await update.message.reply_text("Usage: /task <description>")
            return

        user_id = str(update.effective_user.id)
        task_context = TaskContext(
            task_id=str(uuid.uuid4())[:8],
            raw_input=raw,
            user_id=user_id,
            metadata={"chat_id": update.effective_chat.id},
        )

        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id, action=ChatAction.TYPING
        )

        result_msg = await self._dispatcher.dispatch(task_context)
        await update.message.reply_text(result_msg)

    async def handle_approve(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = str(update.effective_user.id)
        session = self._sessions.get_by_user(user_id)
        if not session or not self._gate.is_pending(session.session_id):
            await update.message.reply_text("No pending task awaiting your approval.")
            return
        self._gate.approve(session.session_id)
        await update.message.reply_text("Approved. Executing...")

    async def handle_cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = str(update.effective_user.id)
        session = self._sessions.get_by_user(user_id)
        if not session:
            await update.message.reply_text("No active task to cancel.")
            return
        if self._gate.is_pending(session.session_id):
            self._gate.reject(session.session_id)
        await update.message.reply_text("Task cancelled.")

    async def handle_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = str(update.effective_user.id)
        session = self._sessions.get_by_user(user_id)
        if not session:
            await update.message.reply_text("No active task.")
            return
        await update.message.reply_text(
            f"Task `{session.context.task_id}` — state: *{session.state.value}*",
            parse_mode="Markdown",
        )

    async def handle_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        text = (
            "*ShellMate Commands*\n\n"
            "/task <description> — submit a new task\n"
            "/approve — approve a pending task plan\n"
            "/cancel — cancel the current task\n"
            "/status — check current task state\n"
            "/help — this message"
        )
        await update.message.reply_text(text, parse_mode="Markdown")
