from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from shellmate.core.interfaces import AuthProvider


def restricted(auth: AuthProvider, action: str = "telegram"):
    """Decorator that rejects unauthorized Telegram users."""
    def decorator(func):
        @wraps(func)
        async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            user = update.effective_user
            if not user:
                return
            if not await auth.is_authorized(str(user.id), action):
                await update.message.reply_text("Unauthorized.")
                return
            return await func(update, context, *args, **kwargs)
        return wrapped
    return decorator
