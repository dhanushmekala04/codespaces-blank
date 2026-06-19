"""
LLM Wrapper for multi-model support.
Uses LangChain as the LLM wrapper with NVIDIA NIM as the backend.
Includes automatic retry with exponential back-off for 429 rate-limit errors.
LLM responses are cached in Redis (key: response:{hash}) to avoid redundant API calls.
"""

import asyncio
import hashlib
import json
import logging
from typing import Any, Literal

from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.messages import HumanMessage, SystemMessage

from config.settings import settings
from app.services.cache_service import cache_service  # noqa: E402 — needed for response caching
from app.observability.logging import start_generation, end_generation  # Langfuse tracing
from app.middleware.request_context import get_request_id

logger = logging.getLogger(__name__)


ModelType = Literal["fast", "balanced", "powerful", "nano"]

# All models confirmed available on NVIDIA NIM free tier
MODEL_MAP: dict[ModelType, str] = {
    "fast":     "meta/llama-3.1-8b-instruct",          # fast, low latency — intent, planner
    "balanced": "meta/llama-3.1-70b-instruct",          # solid all-rounder — most agents
    "powerful": "nvidia/llama-3.3-nemotron-super-49b-v1",  # strongest reasoning — case, event
    "nano":     "nvidia/llama-3.1-nemotron-nano-8b-v1", # lightest — fallbacks
}

# Best free-tier embedding model (1024-dim, matches Pinecone index)
EMBEDDING_MODEL = "nvidia/nv-embedqa-e5-v5"


class LLMWrapper:
    """
    Unified wrapper using LangChain + NVIDIA NIM backend.

    Usage:
        llm = LLMWrapper(model_type="balanced")
        response = await llm.ainvoke("What is the patient's status?")
    """

    def __init__(self, model_type: ModelType = "balanced", temperature: float = 0.1):
        self.model_type = model_type
        self.temperature = temperature
        self._client: ChatNVIDIA | None = None

    def _get_client(self) -> ChatNVIDIA:
        if self._client is None:
            self._client = ChatNVIDIA(
                model=MODEL_MAP[self.model_type],
                api_key=settings.nvidia_api_key,
                temperature=self.temperature,
            )
        return self._client

    async def ainvoke(
        self,
        prompt: str,
        system_prompt: str | None = None,
        use_cache: bool = True,
        **kwargs: Any,
    ) -> str:
        """
        Async invoke the LLM with automatic retry on 429 rate-limit errors.
        Retries up to 3 times with exponential back-off (5s, 10s, 20s).

        Responses are cached in Redis by default (use_cache=False to skip,
        e.g. for write-oriented or unique requests).
        """
        # ── Cache read ────────────────────────────────────────────────────
        cache_key = _llm_cache_key(self.model_type, system_prompt or "", prompt)
        if use_cache:
            cached = await cache_service.get_response(cache_key)
            if cached is not None:
                logger.debug("LLM cache hit for key %s", cache_key[:12])
                return cached

        # ── Langfuse generation span ───────────────────────────────────────
        model_name = MODEL_MAP[self.model_type]
        gen = start_generation(
            name=f"llm.{self.model_type}",
            trace_id=get_request_id(),
            model=model_name,
            input={"system": system_prompt, "prompt": prompt},
            model_parameters={"temperature": self.temperature},
        )

        # ── LLM call ──────────────────────────────────────────────────────
        client = self._get_client()
        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=prompt))

        last_exc: Exception | None = None
        for attempt in range(3):
            try:
                response = await client.ainvoke(messages, **kwargs)
                result: str = response.content

                # ── Cache write ───────────────────────────────────────────
                if use_cache:
                    await cache_service.set_response(cache_key, result)

                end_generation(gen, output=result)
                return result
            except Exception as exc:
                last_exc = exc
                err_str = str(exc).lower()
                # Retry on rate-limit (429) or transient errors
                if "429" in err_str or "rate" in err_str or "too many" in err_str:
                    wait = 5 * (2 ** attempt)   # 5s, 10s, 20s
                    logger.warning(
                        "NVIDIA NIM rate-limited (attempt %d/3). Retrying in %ds...",
                        attempt + 1, wait,
                    )
                    await asyncio.sleep(wait)
                else:
                    end_generation(gen, output=None, level="ERROR", status_message=str(exc))
                    raise  # Non-429 errors fail immediately

        end_generation(gen, output=None, level="ERROR", status_message=str(last_exc))
        raise last_exc  # All retries exhausted

    async def ainvoke_structured(
        self,
        prompt: str,
        system_prompt: str | None = None,
        response_format: dict[str, Any] | None = None,
        use_cache: bool = True,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Async invoke with structured JSON output.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            response_format: Optional JSON schema hint
            use_cache: Whether to use Redis response cache (default True)
            **kwargs: Additional parameters

        Returns:
            Parsed JSON response
        """
        json_instruction = "\n\nRespond ONLY with valid JSON. No additional text."
        raw = await self.ainvoke(prompt + json_instruction, system_prompt, use_cache=use_cache, **kwargs)
        return _parse_json(raw)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _llm_cache_key(model_type: str, system_prompt: str, prompt: str) -> str:
    """Stable hash key for an LLM request — used as the response cache key."""
    combined = f"{model_type}|{system_prompt}|{prompt}"
    return hashlib.sha256(combined.encode()).hexdigest()[:16]

def _parse_json(content: str) -> dict[str, Any]:
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        return json.loads(content.strip())


# ---------------------------------------------------------------------------
# Convenience factories
# ---------------------------------------------------------------------------

def get_glm_model(temperature: float = 0.1) -> LLMWrapper:
    """Balanced model — used by most agents (appointment, billing, insurance, etc.)."""
    return LLMWrapper(model_type="balanced", temperature=temperature)


def get_nemotron_model(temperature: float = 0.1) -> LLMWrapper:
    """Most powerful model — used for complex reasoning (case, event investigation)."""
    return LLMWrapper(model_type="powerful", temperature=temperature)


def get_default_model(temperature: float = 0.1) -> LLMWrapper:
    """Fast lightweight model — used for intent classification and planning."""
    return LLMWrapper(model_type="fast", temperature=temperature)


def get_embeddings():
    """Return NVIDIA NIM embeddings client (1024-dim, for Pinecone)."""
    from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
    return NVIDIAEmbeddings(
        model=EMBEDDING_MODEL,
        api_key=settings.nvidia_api_key,
        truncate="END",
    )