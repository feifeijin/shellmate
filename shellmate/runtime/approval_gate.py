import asyncio
from shellmate.core.models import Session


class ApprovalGate:
    """Holds sessions waiting for human approval before execution."""

    def __init__(self) -> None:
        self._pending: dict[str, asyncio.Future] = {}

    def register(self, session: Session) -> asyncio.Future:
        """Register a session and return a Future that resolves on approve/reject."""
        future: asyncio.Future = asyncio.get_running_loop().create_future()
        self._pending[session.session_id] = future
        return future

    def approve(self, session_id: str) -> bool:
        future = self._pending.pop(session_id, None)
        if future and not future.done():
            future.set_result(True)
            return True
        return False

    def reject(self, session_id: str) -> bool:
        future = self._pending.pop(session_id, None)
        if future and not future.done():
            future.set_result(False)
            return True
        return False

    def is_pending(self, session_id: str) -> bool:
        return session_id in self._pending
