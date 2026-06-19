"""
Cache layer tests.

Strategy:
  - Unit-test CacheService methods with a real fakeredis instance so we
    don't need a live Redis server in CI.
  - Integration-test the Redis connection helper (mocked ping).
  - Test the LLMWrapper cache integration with a mocked cache_service.

Run:
    pytest tests/test_cache.py -v
"""

import asyncio
import json
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ── helpers ──────────────────────────────────────────────────────────────────

try:
    import fakeredis.aioredis as fakeredis_async  # type: ignore
    HAS_FAKEREDIS = True
except ImportError:
    HAS_FAKEREDIS = False


def _make_fake_redis():
    """Return an async fakeredis client that behaves like redis.asyncio.Redis."""
    return fakeredis_async.FakeRedis(decode_responses=True)


# ── fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def fake_redis():
    return _make_fake_redis() if HAS_FAKEREDIS else None


@pytest.fixture
def cache_svc(fake_redis):
    """CacheService with its Redis client monkey-patched to fakeredis."""
    from app.services.cache_service import CacheService
    svc = CacheService()

    async def _get_client():
        return fake_redis

    with patch("app.services.cache_service.get_redis_client", side_effect=_get_client):
        yield svc


# ── skip guard ───────────────────────────────────────────────────────────────

pytestmark = pytest.mark.skipif(
    not HAS_FAKEREDIS,
    reason="fakeredis not installed — run: pip install fakeredis",
)


# ═════════════════════════════════════════════════════════════════════════════
# Session
# ═════════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_session_set_get(cache_svc):
    data = {"user": "alice", "role": "patient"}
    await cache_svc.set_session("p001", data)
    result = await cache_svc.get_session("p001")
    assert result == data


@pytest.mark.asyncio
async def test_session_delete(cache_svc):
    await cache_svc.set_session("p002", {"x": 1})
    await cache_svc.delete_session("p002")
    assert await cache_svc.get_session("p002") is None


@pytest.mark.asyncio
async def test_session_missing_returns_none(cache_svc):
    assert await cache_svc.get_session("no-such-patient") is None


# ═════════════════════════════════════════════════════════════════════════════
# Patient Context
# ═════════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_patient_context_round_trip(cache_svc):
    ctx = {"name": "Bob", "dob": "1990-01-01", "conditions": ["hypertension"]}
    await cache_svc.set_patient_context("p003", ctx)
    assert await cache_svc.get_patient_context("p003") == ctx


@pytest.mark.asyncio
async def test_patient_context_invalidate(cache_svc):
    await cache_svc.set_patient_context("p004", {"a": 1})
    await cache_svc.invalidate_patient_context("p004")
    assert await cache_svc.get_patient_context("p004") is None


# ═════════════════════════════════════════════════════════════════════════════
# Graph state — update_graph_node must MERGE, not overwrite
# ═════════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_graph_state_set_get(cache_svc):
    state = {"nodes": ["intent", "billing"], "result": "ok"}
    await cache_svc.set_graph_state("req-001", state)
    assert await cache_svc.get_graph_state("req-001") == state


@pytest.mark.asyncio
async def test_update_graph_node_merges_not_overwrites(cache_svc):
    """Bug fix: update_graph_node must not destroy the full state."""
    full_state = {"nodes": ["intent", "billing"], "patient_id": "p999", "result": "ok"}
    await cache_svc.set_graph_state("req-002", full_state)

    await cache_svc.update_graph_node("req-002", "response", "running")

    updated = await cache_svc.get_graph_state("req-002")
    # Original fields must still be present
    assert updated["nodes"] == ["intent", "billing"]
    assert updated["patient_id"] == "p999"
    # New fields must be set
    assert updated["current_node"] == "response"
    assert updated["execution_status"] == "running"


# ═════════════════════════════════════════════════════════════════════════════
# Agent state — per-agent key isolation
# ═════════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_agent_state_per_agent_isolation(cache_svc):
    """Bug fix: two agents in the same request must not collide."""
    await cache_svc.set_agent_state("req-003", "billing_agent", "done", {"total": 100})
    await cache_svc.set_agent_state("req-003", "insurance_agent", "running", {})

    billing = await cache_svc.get_agent_state("req-003", "billing_agent")
    insurance = await cache_svc.get_agent_state("req-003", "insurance_agent")

    assert billing["agent"] == "billing_agent"
    assert billing["status"] == "done"
    assert insurance["agent"] == "insurance_agent"
    assert insurance["status"] == "running"


# ═════════════════════════════════════════════════════════════════════════════
# Timeline / Billing / Claim caches
# ═════════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_timeline_cache(cache_svc):
    timeline = [{"event": "appointment", "date": "2024-01-01"}]
    await cache_svc.set_timeline("p005", timeline)
    assert await cache_svc.get_timeline("p005") == timeline
    await cache_svc.invalidate_timeline("p005")
    assert await cache_svc.get_timeline("p005") is None


@pytest.mark.asyncio
async def test_billing_summary_cache(cache_svc):
    summary = {"total_due": 500.0, "total_paid": 200.0, "total_balance": 300.0}
    await cache_svc.set_billing_summary("p006", summary)
    assert await cache_svc.get_billing_summary("p006") == summary
    await cache_svc.invalidate_billing("p006")
    assert await cache_svc.get_billing_summary("p006") is None


@pytest.mark.asyncio
async def test_claim_cache(cache_svc):
    claim = {"status": "approved", "amount": 250.0}
    await cache_svc.set_claim("claim-42", claim)
    assert await cache_svc.get_claim("claim-42") == claim
    await cache_svc.invalidate_claim("claim-42")
    assert await cache_svc.get_claim("claim-42") is None


# ═════════════════════════════════════════════════════════════════════════════
# Response / Prompt cache
# ═════════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_response_cache_round_trip(cache_svc):
    query = "What are clinic hours?"
    response = "The clinic is open 9am–5pm Monday to Friday."
    await cache_svc.set_response(query, response)
    assert await cache_svc.get_response(query) == response


@pytest.mark.asyncio
async def test_response_cache_miss(cache_svc):
    assert await cache_svc.get_response("unknown query xyz") is None


@pytest.mark.asyncio
async def test_prompt_cache_round_trip(cache_svc):
    prompt_key = "billing_agent|patient_p007"
    prompt_text = "You are a billing agent. Patient balance is $300."
    await cache_svc.set_prompt(prompt_key, prompt_text)
    assert await cache_svc.get_prompt(prompt_key) == prompt_text


# ═════════════════════════════════════════════════════════════════════════════
# Rate limiting
# ═════════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_rate_limit_allows_within_limit(cache_svc):
    allowed, count = await cache_svc.check_rate_limit("login", "127.0.0.1")
    assert allowed is True
    assert count == 1


@pytest.mark.asyncio
async def test_rate_limit_blocks_over_limit(cache_svc):
    """Exceed the login limit (5 req/min)."""
    from app.services.cache_service import LIMIT_LOGIN
    identifier = "attacker-ip"
    for _ in range(LIMIT_LOGIN):
        await cache_svc.check_rate_limit("login", identifier)
    allowed, count = await cache_svc.check_rate_limit("login", identifier)
    assert allowed is False
    assert count == LIMIT_LOGIN + 1


@pytest.mark.asyncio
async def test_rate_limit_get_count(cache_svc):
    await cache_svc.check_rate_limit("chat", "user-99")
    await cache_svc.check_rate_limit("chat", "user-99")
    count = await cache_svc.get_rate_limit_count("chat", "user-99")
    assert count == 2


# ═════════════════════════════════════════════════════════════════════════════
# Distributed lock
# ═════════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_lock_acquire_and_release(cache_svc):
    acquired = await cache_svc.acquire_lock("claim-investigation-77")
    assert acquired is True

    # Second acquire must fail
    blocked = await cache_svc.acquire_lock("claim-investigation-77")
    assert blocked is False

    # After release, can acquire again
    await cache_svc.release_lock("claim-investigation-77")
    re_acquired = await cache_svc.acquire_lock("claim-investigation-77")
    assert re_acquired is True


# ═════════════════════════════════════════════════════════════════════════════
# Graceful degradation (Redis = None)
# ═════════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_cache_degrades_gracefully_when_redis_down():
    """All operations must return None / safe defaults when Redis is unavailable."""
    from app.services.cache_service import CacheService

    svc = CacheService()

    async def _no_redis():
        return None

    with patch("app.services.cache_service.get_redis_client", side_effect=_no_redis):
        assert await svc.get_session("p000") is None
        assert await svc.get_patient_context("p000") is None
        assert await svc.get_graph_state("req-000") is None
        assert await svc.get_timeline("p000") is None
        assert await svc.get_billing_summary("p000") is None
        assert await svc.get_response("any query") is None

        # Rate limit must fail-open (allow)
        allowed, count = await svc.check_rate_limit("chat", "any-user")
        assert allowed is True
        assert count == 0

        # Lock must fail-open (allow)
        acquired = await svc.acquire_lock("any-resource")
        assert acquired is True

        # Write operations must not raise
        await svc.set_session("p000", {"x": 1})
        await svc.set_patient_context("p000", {"x": 1})
        await svc.set_billing_summary("p000", {"x": 1})


# ═════════════════════════════════════════════════════════════════════════════
# Redis connection helper — retry backoff
# ═════════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_redis_connection_backoff_prevents_hammering():
    """
    After a failed init, get_redis_client() must NOT call init_redis again
    within the cooldown window.
    """
    import app.db.redis as redis_mod

    # Reset module state
    redis_mod._client = None
    redis_mod._failed_at = None

    init_call_count = 0
    original_init = redis_mod.init_redis

    async def counting_init():
        nonlocal init_call_count
        init_call_count += 1
        # Mark as failed so cooldown kicks in
        redis_mod._failed_at = time.monotonic()
        # Leave _client as None (simulates connection failure)

    redis_mod.init_redis = counting_init
    try:
        await redis_mod.get_redis_client()   # call 1 — triggers init, sets _failed_at
        await redis_mod.get_redis_client()   # call 2 — inside cooldown, must NOT reinit
        await redis_mod.get_redis_client()   # call 3 — inside cooldown, must NOT reinit
    finally:
        redis_mod.init_redis = original_init
        redis_mod._client = None
        redis_mod._failed_at = None

    assert init_call_count == 1, (
        f"Expected init_redis called once (backoff), but was called {init_call_count} times"
    )


# ═════════════════════════════════════════════════════════════════════════════
# LLMWrapper cache integration
# ═════════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_llm_wrapper_uses_response_cache_on_hit():
    """LLMWrapper must return cached response without calling NVIDIA NIM."""
    from app.llm.wrapper import LLMWrapper

    mock_cache = AsyncMock()
    mock_cache.get_response = AsyncMock(return_value="cached answer")
    mock_cache.set_response = AsyncMock()

    wrapper = LLMWrapper(model_type="fast")

    with patch("app.llm.wrapper.cache_service", mock_cache):
        result = await wrapper.ainvoke("What is my balance?", use_cache=True)

    assert result == "cached answer"
    mock_cache.get_response.assert_called_once()
    # NIM client should never have been created
    assert wrapper._client is None


@pytest.mark.asyncio
async def test_llm_wrapper_stores_response_on_miss():
    """On a cache miss, LLMWrapper must call NIM and then store the result."""
    from app.llm.wrapper import LLMWrapper

    mock_cache = AsyncMock()
    mock_cache.get_response = AsyncMock(return_value=None)   # miss
    mock_cache.set_response = AsyncMock()

    nim_response = MagicMock()
    nim_response.content = "Your balance is $300."

    mock_nim_client = AsyncMock()
    mock_nim_client.ainvoke = AsyncMock(return_value=nim_response)

    wrapper = LLMWrapper(model_type="fast")
    wrapper._client = mock_nim_client   # inject fake NIM client

    with patch("app.llm.wrapper.cache_service", mock_cache):
        result = await wrapper.ainvoke("What is my balance?", use_cache=True)

    assert result == "Your balance is $300."
    mock_cache.set_response.assert_called_once()


@pytest.mark.asyncio
async def test_llm_wrapper_skips_cache_when_disabled():
    """use_cache=False must bypass both get and set."""
    from app.llm.wrapper import LLMWrapper

    mock_cache = AsyncMock()
    mock_cache.get_response = AsyncMock()
    mock_cache.set_response = AsyncMock()

    nim_response = MagicMock()
    nim_response.content = "Direct answer."

    mock_nim_client = AsyncMock()
    mock_nim_client.ainvoke = AsyncMock(return_value=nim_response)

    wrapper = LLMWrapper(model_type="fast")
    wrapper._client = mock_nim_client

    with patch("app.llm.wrapper.cache_service", mock_cache):
        result = await wrapper.ainvoke("tell me something", use_cache=False)

    assert result == "Direct answer."
    mock_cache.get_response.assert_not_called()
    mock_cache.set_response.assert_not_called()
