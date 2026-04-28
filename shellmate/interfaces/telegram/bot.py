import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from shellmate.core.interfaces import AuthProvider
from shellmate.runtime.dispatcher import Dispatcher
from shellmate.runtime.session_manager import SessionManager
from shellmate.runtime.approval_gate import ApprovalGate
from .handlers import TelegramHandlers
from .middleware import restricted

log = logging.getLogger(__name__)


def build_app(
    token: str,
    dispatcher: Dispatcher,
    sessions: SessionManager,
    gate: ApprovalGate,
    auth: AuthProvider,
    webhook_url: str | None = None,
    port: int = 8080,
) -> Application:
    app = Application.builder().token(token).build()
    h = TelegramHandlers(dispatcher, sessions, gate, auth)

    guard = h._guard()

    app.add_handler(CommandHandler("task",    _wrap(guard, h.handle_task)))
    app.add_handler(CommandHandler("approve", _wrap(guard, h.handle_approve)))
    app.add_handler(CommandHandler("cancel",  _wrap(guard, h.handle_cancel)))
    app.add_handler(CommandHandler("status",  _wrap(guard, h.handle_status)))
    app.add_handler(CommandHandler("help",    h.handle_help))

    return app


def run_polling(app: Application) -> None:
    log.info("Starting bot in polling mode")
    app.run_polling()


def run_webhook(app: Application, webhook_url: str, port: int = 8080) -> None:
    log.info("Starting bot with webhook at %s", webhook_url)
    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path="webhook",
        webhook_url=f"{webhook_url}/webhook",
    )


def _wrap(guard, handler):
    """Apply auth guard to a handler."""
    return guard(handler)
