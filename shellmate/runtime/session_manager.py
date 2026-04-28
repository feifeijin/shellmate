import uuid
from datetime import datetime, timedelta, timezone
from shellmate.core.models import Session, TaskState, TaskContext


class SessionManager:
    def __init__(self, ttl_seconds: int = 3600) -> None:
        self._sessions: dict[str, Session] = {}
        self._ttl = timedelta(seconds=ttl_seconds)

    def create(self, context: TaskContext) -> Session:
        session = Session(
            session_id=str(uuid.uuid4()),
            user_id=context.user_id,
            state=TaskState.RECEIVED,
            context=context,
            expires_at=datetime.now(timezone.utc) + self._ttl,
        )
        self._sessions[session.session_id] = session
        session.log(f"session created for user={context.user_id}")
        return session

    def get(self, session_id: str) -> Session | None:
        return self._sessions.get(session_id)

    def get_by_user(self, user_id: str) -> Session | None:
        """Returns the most recent active session for a user."""
        active = [
            s for s in self._sessions.values()
            if s.user_id == user_id and s.state not in (
                TaskState.DONE, TaskState.FAILED, TaskState.CANCELLED
            )
        ]
        return max(active, key=lambda s: s.created_at, default=None)

    def transition(self, session: Session, new_state: TaskState) -> None:
        session.log(f"state {session.state.value} → {new_state.value}")
        session.state = new_state

    def purge_expired(self) -> int:
        now = datetime.now(timezone.utc)
        expired = [
            sid for sid, s in self._sessions.items()
            if s.expires_at and s.expires_at < now
        ]
        for sid in expired:
            del self._sessions[sid]
        return len(expired)
