"""
Cache Service — implements all Redis caching use cases from REDIS_STRATEGY.md.

Key schema (matches strategy doc exactly):
  session:{patient_id}              — active user session (TTL 30 min)
  context:{patient_id}              — assembled patient context (TTL 10 min)
  graph:{request_id}                — LangGraph execution state (TTL 24 h)
  agent:{request_id}                — per-agent checkpoint (TTL 24 h)
  timeline:{patient_id}             — patient 360 timeline (TTL 5 min)
  billing_summary:{patient_id}      — billing summary (TTL 2 min)
  claim:{claim_id}                  — single claim lookup (TTL 2 min)
  response:{query_hash}             — common response cache (TTL 1 h)
  prompt:{hash}                     — prompt cache (TTL 24 h)
  rate_limit:chat:{user_id}         — chat rate limit counter (TTL 60 s)
  rate_limit:login:{ip}             — login rate limit counter (TTL 60 s)
  rate_limit:admin:{user_id}        — admin rate limit counter (TTL 60 s)
  lock:{resource_id}                — distributed lock (TTL 60 s)

All methods degrade gracefully when Redis is unavailable.
"""

import hashlib
import json
import logging
from typing import Any

from app.db.redis import get_redis_client

logger = logging.getLogger(__name__)

# ── TTLs (seconds) ────────────────────────────────────────────────────────────
TTL_SESSION    = 60 * 30        # 30 min
TTL_CONTEXT    = 60 * 10        # 10 min
TTL_TIMELINE   = 60 * 5         # 5 min
TTL_BILLING    = 60 * 2         # 2 min
TTL_CLAIM      = 60 * 2         # 2 min
TTL_RESPONSE   = 60 * 60        # 1 h
TTL_PROMPT     = 60 * 60 * 24   # 24 h
TTL_GRAPH      = 60 * 60 * 24   # 24 h
TTL_AGENT      = 60 * 60 * 24   # 24 h
TTL_RATE_CHAT  = 60             # 1 min window
TTL_RATE_LOGIN = 60             # 1 min window
TTL_RATE_ADMIN = 60             # 1 min window
TTL_LOCK       = 60             # 60 s

# ── Rate limits ───────────────────────────────────────────────────────────────
LIMIT_CHAT  = 60   # requests/min
LIMIT_LOGIN = 5    # requests/min
LIMIT_ADMIN = 20   # requests/min


class CacheService:

    # ════════════════════════════════════════════════════════════════════════
    # Session  (session:{patient_id})
    # ════════════════════════════════════════════════════════════════════════

    async def set_session(self, patient_id: str, data: dict) -> None:
        await self._setex(f"session:{patient_id}", TTL_SESSION, data)

    async def get_session(self, patient_id: str) -> dict | None:
        return await self._getjson(f"session:{patient_id}")

    async def delete_session(self, patient_id: str) -> None:
        await self._delete(f"session:{patient_id}")

    # ════════════════════════════════════════════════════════════════════════
    # Patient Context  (context:{patient_id})
    # Caches assembled patient context so agents don't hit MongoDB every request
    # ════════════════════════════════════════════════════════════════════════

    async def set_patient_context(self, patient_id: str, context: dict) -> None:
        await self._setex(f"context:{patient_id}", TTL_CONTEXT, context)

    async def get_patient_context(self, patient_id: str) -> dict | None:
        return await self._getjson(f"context:{patient_id}")

    async def invalidate_patient_context(self, patient_id: str) -> None:
        """Call after any write that changes patient data."""
        await self._delete(f"context:{patient_id}")

    # ════════════════════════════════════════════════════════════════════════
    # LangGraph State  (graph:{request_id})
    # ════════════════════════════════════════════════════════════════════════

    async def set_graph_state(self, request_id: str, state: dict) -> None:
        await self._setex(f"graph:{request_id}", TTL_GRAPH, state)

    async def get_graph_state(self, request_id: str) -> dict | None:
        return await self._getjson(f"graph:{request_id}")

    async def update_graph_node(self, request_id: str, current_node: str, execution_status: str) -> None:
        """Checkpoint the current graph node for observability.
        Merges into the existing state instead of overwriting it.
        """
        existing = await self.get_graph_state(request_id) or {}
        existing.update({
            "current_node": current_node,
            "execution_status": execution_status,
        })
        await self._setex(f"graph:{request_id}", TTL_GRAPH, existing)

    # ════════════════════════════════════════════════════════════════════════
    # Agent State  (agent:{request_id})
    # ════════════════════════════════════════════════════════════════════════

    async def set_agent_state(self, request_id: str, agent: str, status: str, output: dict | None = None) -> None:
        """Store per-agent state. Key includes agent name to prevent collision."""
        await self._setex(f"agent:{request_id}:{agent}", TTL_AGENT, {
            "request_id": request_id,
            "agent": agent,
            "status": status,
            "output": output or {},
        })

    async def get_agent_state(self, request_id: str, agent: str) -> dict | None:
        return await self._getjson(f"agent:{request_id}:{agent}")

    # ════════════════════════════════════════════════════════════════════════
    # Timeline Cache  (timeline:{patient_id})
    # Patient 360 timelines are expensive — cache 5 min
    # ════════════════════════════════════════════════════════════════════════

    async def set_timeline(self, patient_id: str, timeline: list) -> None:
        await self._setex(f"timeline:{patient_id}", TTL_TIMELINE, timeline)

    async def get_timeline(self, patient_id: str) -> list | None:
        return await self._getjson(f"timeline:{patient_id}")

    async def invalidate_timeline(self, patient_id: str) -> None:
        await self._delete(f"timeline:{patient_id}")

    # ════════════════════════════════════════════════════════════════════════
    # Billing Summary Cache  (billing_summary:{patient_id})
    # Read-only — never cache write operations
    # ════════════════════════════════════════════════════════════════════════

    async def set_billing_summary(self, patient_id: str, summary: dict) -> None:
        await self._setex(f"billing_summary:{patient_id}", TTL_BILLING, summary)

    async def get_billing_summary(self, patient_id: str) -> dict | None:
        return await self._getjson(f"billing_summary:{patient_id}")

    async def invalidate_billing(self, patient_id: str) -> None:
        await self._delete(f"billing_summary:{patient_id}")

    # ════════════════════════════════════════════════════════════════════════
    # Claim Cache  (claim:{claim_id})
    # ════════════════════════════════════════════════════════════════════════

    async def set_claim(self, claim_id: str, claim: dict) -> None:
        await self._setex(f"claim:{claim_id}", TTL_CLAIM, claim)

    async def get_claim(self, claim_id: str) -> dict | None:
        return await self._getjson(f"claim:{claim_id}")

    async def invalidate_claim(self, claim_id: str) -> None:
        await self._delete(f"claim:{claim_id}")

    # ════════════════════════════════════════════════════════════════════════
    # Response Cache  (response:{query_hash})
    # Cache common/static responses — e.g. clinic hours, HIPAA info
    # ════════════════════════════════════════════════════════════════════════

    async def set_response(self, query: str, response: str, ttl: int = TTL_RESPONSE) -> None:
        key = f"response:{self._hash(query)}"
        try:
            client = await get_redis_client()
            if client:
                await client.setex(key, ttl, response)
        except Exception as exc:
            logger.debug("cache set_response failed: %s", exc)

    async def get_response(self, query: str) -> str | None:
        key = f"response:{self._hash(query)}"
        try:
            client = await get_redis_client()
            if client:
                return await client.get(key)
        except Exception as exc:
            logger.debug("cache get_response failed: %s", exc)
        return None

    # ════════════════════════════════════════════════════════════════════════
    # Prompt Cache  (prompt:{hash})
    # Cache generated prompts to avoid reconstruction
    # ════════════════════════════════════════════════════════════════════════

    async def set_prompt(self, prompt_key: str, prompt: str) -> None:
        await self._setexstr(f"prompt:{self._hash(prompt_key)}", TTL_PROMPT, prompt)

    async def get_prompt(self, prompt_key: str) -> str | None:
        try:
            client = await get_redis_client()
            if client:
                return await client.get(f"prompt:{self._hash(prompt_key)}")
        except Exception as exc:
            logger.debug("cache get_prompt failed: %s", exc)
        return None

    # ════════════════════════════════════════════════════════════════════════
    # Rate Limiting
    # Uses Redis INCR + EXPIRE for sliding window counters
    # ════════════════════════════════════════════════════════════════════════

    async def check_rate_limit(
        self,
        key_type: str,   # "chat" | "login" | "admin"
        identifier: str, # user_id or IP
    ) -> tuple[bool, int]:
        """
        Returns (allowed, current_count).
        allowed=False means the limit has been exceeded.
        """
        limits = {"chat": LIMIT_CHAT, "login": LIMIT_LOGIN, "admin": LIMIT_ADMIN}
        ttls   = {"chat": TTL_RATE_CHAT, "login": TTL_RATE_LOGIN, "admin": TTL_RATE_ADMIN}
        limit  = limits.get(key_type, LIMIT_CHAT)
        ttl    = ttls.get(key_type, TTL_RATE_CHAT)
        key    = f"rate_limit:{key_type}:{identifier}"

        try:
            client = await get_redis_client()
            if client is None:
                return True, 0   # No Redis → allow all

            count = await client.incr(key)
            if count == 1:
                await client.expire(key, ttl)   # Set TTL on first hit
            return count <= limit, count
        except Exception as exc:
            logger.debug("rate_limit check failed: %s", exc)
            return True, 0   # Fail open

    async def get_rate_limit_count(self, key_type: str, identifier: str) -> int:
        key = f"rate_limit:{key_type}:{identifier}"
        try:
            client = await get_redis_client()
            if client:
                val = await client.get(key)
                return int(val) if val else 0
        except Exception:
            pass
        return 0

    # ════════════════════════════════════════════════════════════════════════
    # Distributed Lock  (lock:{resource_id})
    # Prevents duplicate processing (e.g. two concurrent claim investigations)
    # ════════════════════════════════════════════════════════════════════════

    async def acquire_lock(self, resource_id: str, ttl: int = TTL_LOCK) -> bool:
        """
        Try to acquire a lock. Returns True if acquired, False if already locked.
        Uses SET NX (set-if-not-exists) for atomic lock acquisition.
        """
        key = f"lock:{resource_id}"
        try:
            client = await get_redis_client()
            if client is None:
                return True   # No Redis → always allow
            result = await client.set(key, "1", nx=True, ex=ttl)
            return result is not None
        except Exception as exc:
            logger.debug("acquire_lock failed: %s", exc)
            return True   # Fail open

    async def release_lock(self, resource_id: str) -> None:
        await self._delete(f"lock:{resource_id}")

    # ════════════════════════════════════════════════════════════════════════
    # Internal helpers
    # ════════════════════════════════════════════════════════════════════════

    async def _setex(self, key: str, ttl: int, value: Any) -> None:
        try:
            client = await get_redis_client()
            if client:
                await client.setex(key, ttl, json.dumps(value, default=str))
        except Exception as exc:
            logger.debug("cache _setex %s failed: %s", key, exc)

    async def _setexstr(self, key: str, ttl: int, value: str) -> None:
        try:
            client = await get_redis_client()
            if client:
                await client.setex(key, ttl, value)
        except Exception as exc:
            logger.debug("cache _setexstr %s failed: %s", key, exc)

    async def _getjson(self, key: str) -> Any | None:
        try:
            client = await get_redis_client()
            if client:
                raw = await client.get(key)
                return json.loads(raw) if raw else None
        except Exception as exc:
            logger.debug("cache _getjson %s failed: %s", key, exc)
        return None

    async def _delete(self, *keys: str) -> None:
        try:
            client = await get_redis_client()
            if client and keys:
                await client.delete(*keys)
        except Exception as exc:
            logger.debug("cache _delete failed: %s", exc)

    @staticmethod
    def _hash(value: str) -> str:
        return hashlib.sha256(value.encode()).hexdigest()[:16]


# Module-level singleton
cache_service = CacheService()
