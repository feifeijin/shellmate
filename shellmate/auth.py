from shellmate.core.interfaces import AuthProvider


class AllowlistAuthProvider(AuthProvider):
    """Simple allowlist-based auth. Pass user IDs as a set of strings."""

    def __init__(self, allowed_user_ids: set[str]) -> None:
        self._allowed = allowed_user_ids

    async def is_authorized(self, user_id: str, action: str) -> bool:
        return user_id in self._allowed

    @classmethod
    def from_env(cls, env_var: str = "ALLOWED_USER_IDS") -> "AllowlistAuthProvider":
        import os
        raw = os.environ.get(env_var, "")
        ids = {x.strip() for x in raw.split(",") if x.strip()}
        return cls(ids)
