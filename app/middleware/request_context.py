"""
Request context middleware — injects a unique request_id per request
and opens a Langfuse trace for the full HTTP request lifecycle.

ContextVars
───────────
  request_id_context   — UUID4 stamped on every request
  trace_context        — Langfuse StatefulTraceClient | None

The Langfuse trace is ended (and the output recorded) after the response
is sent, so it captures the full round-trip latency.  When Langfuse is
not configured the trace helpers are no-ops — the middleware still works.
"""

import uuid
from contextvars import ContextVar
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.observability.logging import start_trace, end_trace

# ── ContextVars ───────────────────────────────────────────────────────────────

request_id_context: ContextVar[str] = ContextVar("request_id", default="unknown")
trace_context: ContextVar[Any]      = ContextVar("langfuse_trace", default=None)


def get_request_id() -> str:
    """Return the request_id for the current async context."""
    return request_id_context.get()


def get_current_trace():
    """Return the Langfuse trace for the current async context, or None."""
    return trace_context.get()


class RequestContextMiddleware(BaseHTTPMiddleware):
    """
    Starlette middleware that:
      1. Stamps every request with a unique X-Request-ID.
      2. Opens a Langfuse trace for the request (no-op if keys missing).
      3. Closes the trace after the response is sent.
      4. Echoes X-Request-ID and X-Trace-ID back in response headers.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # ── Request ID ────────────────────────────────────────────────────
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        id_token = request_id_context.set(request_id)

        # ── Langfuse trace — opened before the handler runs ───────────────
        patient_id = _extract_patient_id(request)
        trace = start_trace(
            "http_request",
            trace_id=request_id,
            user_id=patient_id,
            metadata={
                "method": request.method,
                "path":   request.url.path,
            },
            tags=[request.method, request.url.path.split("/")[1] or "root"],
            input={"path": request.url.path, "method": request.method},
        )
        trace_token = trace_context.set(trace)

        try:
            response: Response = await call_next(request)

            # ── Close trace with status code ─────────────────────────────
            end_trace(
                trace,
                output={"status_code": response.status_code},
                metadata={"status_code": response.status_code},
            )

            # Echo identifiers back to the client
            response.headers["X-Request-ID"] = request_id
            if trace is not None:
                response.headers["X-Trace-ID"] = request_id

            return response

        except Exception as exc:
            end_trace(
                trace,
                output={"error": str(exc)},
                metadata={"error": type(exc).__name__},
            )
            raise

        finally:
            request_id_context.reset(id_token)
            trace_context.reset(trace_token)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _extract_patient_id(request: Request) -> str | None:
    """
    Best-effort patient_id extraction for Langfuse user_id.
    Checks query params then path params (e.g. /patients/{patient_id}).
    Returns None when not present — Langfuse accepts None fine.
    """
    pid = request.query_params.get("patient_id")
    if pid:
        return pid
    # path like /patients/P123 → segment index 2
    parts = request.url.path.strip("/").split("/")
    if len(parts) >= 2 and parts[0] in ("patients", "chat"):
        candidate = parts[1]
        if candidate and candidate not in ("stream", "history"):
            return candidate
    return None
