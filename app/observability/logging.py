"""
Observability module — structured logging + Langfuse tracing.

Langfuse is initialised lazily from settings.  If the keys are absent or
the host is unreachable the module degrades gracefully: all trace/span
helpers become no-ops so the application keeps running without telemetry.

Public API
──────────
  setup_logging()           — call once at app startup (configures JSON logs)
  get_langfuse()            — returns the Langfuse client or None
  flush_langfuse()          — flush pending events (call at shutdown)

  start_trace(...)          — open a Langfuse trace; returns StatefulTraceClient | None
  end_trace(trace, ...)     — close a trace

  start_generation(...)     — open a Langfuse generation span; returns StatefulClient | None
  end_generation(gen, ...)  — close a generation span

  log_event(action, **kw)   — structured log line (unchanged from original API)
"""

import logging
import time
from typing import Any

from config.settings import settings

# ── JSON-structured logging ───────────────────────────────────────────────────

class _JsonFormatter(logging.Formatter):
    """Single-line JSON log records — works well with CloudWatch / Datadog."""

    def format(self, record: logging.LogRecord) -> str:
        import json as _json
        payload: dict[str, Any] = {
            "ts":      self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level":   record.levelname,
            "logger":  record.name,
            "msg":     record.getMessage(),
        }
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        # merge any extra= kwargs passed to logger.info(…, extra={…})
        for k, v in record.__dict__.items():
            if k not in logging.LogRecord.__dict__ and not k.startswith("_"):
                payload[k] = v
        return _json.dumps(payload, default=str)


def setup_logging(level: int = logging.INFO) -> None:
    """Configure root logger with JSON output.  Call once in app lifespan."""
    handler = logging.StreamHandler()
    handler.setFormatter(_JsonFormatter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


# ── Langfuse client singleton ─────────────────────────────────────────────────

_langfuse = None          # Langfuse | None
_langfuse_enabled = None  # bool, None = not yet determined
logger = logging.getLogger("patientcare.observability")


def get_langfuse():
    """
    Return the Langfuse client.  Returns None if keys are missing or the
    initial connection failed.  Initialises on first call.
    """
    global _langfuse, _langfuse_enabled

    if _langfuse_enabled is False:
        return None
    if _langfuse is not None:
        return _langfuse

    # Only initialise when both keys are present
    if not settings.langfuse_public_key or not settings.langfuse_secret_key:
        _langfuse_enabled = False
        logger.info("Langfuse keys not configured — tracing disabled.")
        return None

    try:
        from langfuse import Langfuse  # type: ignore
        _langfuse = Langfuse(
            public_key=settings.langfuse_public_key,
            secret_key=settings.langfuse_secret_key,
            host=settings.langfuse_host,
        )
        _langfuse_enabled = True
        logger.info("Langfuse connected to %s", settings.langfuse_host)
    except Exception as exc:
        _langfuse_enabled = False
        logger.warning("Langfuse init failed (%s) — tracing disabled.", exc)

    return _langfuse


def flush_langfuse() -> None:
    """Flush all pending Langfuse events.  Call during app shutdown."""
    lf = get_langfuse()
    if lf:
        try:
            lf.flush()
            logger.debug("Langfuse flushed.")
        except Exception as exc:
            logger.warning("Langfuse flush failed: %s", exc)


# ── Trace helpers ─────────────────────────────────────────────────────────────

def start_trace(
    name: str,
    *,
    trace_id: str | None = None,
    user_id: str | None = None,
    session_id: str | None = None,
    metadata: dict | None = None,
    tags: list[str] | None = None,
    input: Any = None,
):
    """
    Open a Langfuse trace.  Returns the StatefulTraceClient or None.

    Usage:
        trace = start_trace("chat", trace_id=request_id, user_id=patient_id)
        # … workflow runs …
        end_trace(trace, output="assistant reply")
    """
    lf = get_langfuse()
    if lf is None:
        return None
    try:
        kwargs: dict[str, Any] = {"name": name}
        if trace_id:
            kwargs["trace_id"] = trace_id
        if user_id:
            kwargs["user_id"] = user_id
        if session_id:
            kwargs["session_id"] = session_id
        if metadata:
            kwargs["metadata"] = metadata
        if tags:
            kwargs["tags"] = tags
        if input is not None:
            kwargs["input"] = input
        return lf.trace(**kwargs)
    except Exception as exc:
        logger.debug("start_trace failed: %s", exc)
        return None


def end_trace(trace, *, output: Any = None, metadata: dict | None = None) -> None:
    """Close a trace and optionally record final output."""
    if trace is None:
        return
    try:
        kwargs: dict[str, Any] = {}
        if output is not None:
            kwargs["output"] = output
        if metadata:
            kwargs["metadata"] = metadata
        trace.update(**kwargs)
    except Exception as exc:
        logger.debug("end_trace failed: %s", exc)


# ── Generation (LLM span) helpers ─────────────────────────────────────────────

def start_generation(
    *,
    name: str,
    trace_id: str | None = None,
    model: str,
    input: Any,
    model_parameters: dict | None = None,
    metadata: dict | None = None,
):
    """
    Open a Langfuse generation span for one LLM call.
    Returns the generation object or None.

    Usage:
        gen = start_generation(name="intent_agent", model="llama-3.1-8b",
                               input=prompt, trace_id=request_id)
        result = await llm.ainvoke(prompt)
        end_generation(gen, output=result, usage={"total_tokens": 123})
    """
    lf = get_langfuse()
    if lf is None:
        return None
    try:
        kwargs: dict[str, Any] = {
            "name":  name,
            "model": model,
            "input": input,
            "start_time": _now(),
        }
        if trace_id:
            kwargs["trace_id"] = trace_id
        if model_parameters:
            kwargs["model_parameters"] = model_parameters
        if metadata:
            kwargs["metadata"] = metadata
        return lf.generation(**kwargs)
    except Exception as exc:
        logger.debug("start_generation failed: %s", exc)
        return None


def end_generation(
    gen,
    *,
    output: Any = None,
    usage: dict | None = None,
    level: str = "DEFAULT",
    status_message: str | None = None,
) -> None:
    """Close a generation span with output and optional token usage."""
    if gen is None:
        return
    try:
        kwargs: dict[str, Any] = {
            "end_time": _now(),
            "level": level,
        }
        if output is not None:
            kwargs["output"] = output
        if usage:
            kwargs["usage"] = usage
        if status_message:
            kwargs["status_message"] = status_message
        gen.end(**kwargs)
    except Exception as exc:
        logger.debug("end_generation failed: %s", exc)


# ── Convenience log helper (backward-compatible) ──────────────────────────────

def log_event(action: str, **metadata: Any) -> None:
    """Structured log line.  Preserved from original API."""
    logging.getLogger("patientcare").info(action, extra=metadata)


# ── Internal helpers ──────────────────────────────────────────────────────────

def _now():
    """Return current UTC datetime (used for generation timestamps)."""
    from datetime import datetime, timezone
    return datetime.now(timezone.utc)
