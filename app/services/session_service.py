"""
Session Service — conversation history via Redis (with in-memory fallback).

Each session stores:
  - The last N messages (role + content)
  - The last resolved intent (so follow-up questions stay in context)

Redis key schema:
  session:{session_id}:messages   →  JSON list  (TTL 2 h)
  session:{session_id}:intent     →  string     (TTL 2 h)

If Redis is unavailable the service falls back to a simple in-process
dict so the server keeps running without caching.
"""

import json
import logging
from typing import Any

from app.db.redis import get_redis_client

logger = logging.getLogger(__name__)

SESSION_TTL    = 60 * 60 * 2   # 2 hours
MAX_MESSAGES   = 20             # keep last 20 turns per session


class SessionService:

    # ── public API ────────────────────────────────────────────────────────

    async def get_history(self, session_id: str) -> list[dict[str, Any]]:
        """Return the conversation history for a session (newest last)."""
        if not session_id:
            return []
        try:
            client = await get_redis_client()
            if client is None:
                return self._mem_get(session_id)
            raw = await client.get(self._msg_key(session_id))
            return json.loads(raw) if raw else []
        except Exception as exc:
            logger.debug("session get_history failed: %s", exc)
            return self._mem_get(session_id)

    async def append_turn(
        self,
        session_id: str,
        user_message: str,
        assistant_reply: str,
        intent: str | None = None,
    ) -> None:
        """Append one user/assistant turn and optionally update the intent."""
        if not session_id:
            return
        try:
            client = await get_redis_client()
            history = await self.get_history(session_id)

            history.append({"role": "user",      "content": user_message})
            history.append({"role": "assistant",  "content": assistant_reply})

            # Trim to last MAX_MESSAGES
            if len(history) > MAX_MESSAGES:
                history = history[-MAX_MESSAGES:]

            if client is not None:
                await client.setex(
                    self._msg_key(session_id),
                    SESSION_TTL,
                    json.dumps(history),
                )
                if intent:
                    await client.setex(
                        self._intent_key(session_id),
                        SESSION_TTL,
                        intent,
                    )
            else:
                self._mem_set(session_id, history)

        except Exception as exc:
            logger.debug("session append_turn failed: %s", exc)

    async def get_last_intent(self, session_id: str) -> str | None:
        """Return the most recent intent for a session (for follow-up context)."""
        if not session_id:
            return None
        try:
            client = await get_redis_client()
            if client is None:
                return self._mem_intent.get(session_id)
            return await client.get(self._intent_key(session_id))
        except Exception as exc:
            logger.debug("session get_last_intent failed: %s", exc)
            return None

    async def clear(self, session_id: str) -> None:
        """Delete all session data."""
        if not session_id:
            return
        try:
            client = await get_redis_client()
            if client is not None:
                await client.delete(
                    self._msg_key(session_id),
                    self._intent_key(session_id),
                )
            self._mem_store.pop(session_id, None)
            self._mem_intent.pop(session_id, None)
        except Exception as exc:
            logger.debug("session clear failed: %s", exc)

    # ── helpers ───────────────────────────────────────────────────────────

    @staticmethod
    def _msg_key(session_id: str) -> str:
        return f"session:{session_id}:messages"

    @staticmethod
    def _intent_key(session_id: str) -> str:
        return f"session:{session_id}:intent"

    # ── in-memory fallback ────────────────────────────────────────────────
    _mem_store:  dict[str, list[dict]] = {}
    _mem_intent: dict[str, str]        = {}

    def _mem_get(self, session_id: str) -> list[dict]:
        return list(self._mem_store.get(session_id, []))

    def _mem_set(self, session_id: str, history: list[dict]) -> None:
        self._mem_store[session_id] = history


# Module-level singleton
session_service = SessionService()
