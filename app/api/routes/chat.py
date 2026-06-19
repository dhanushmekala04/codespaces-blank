"""Chat route — main entry point for the patient AI workflow."""

import uuid
from functools import lru_cache

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.graph.state import PatientState
from app.graph.workflow import build_workflow
from app.services.session_service import session_service
from app.services.cache_service import cache_service

router = APIRouter(prefix="/chat", tags=["chat"])


# ---------------------------------------------------------------------------
# Compile workflow once at import time, not on every request
# ---------------------------------------------------------------------------
@lru_cache(maxsize=1)
def _get_compiled_workflow():
    """Build and compile the LangGraph workflow exactly once."""
    return build_workflow()


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    patient_id: str | None = None
    tenant_id: str | None = None
    session_id: str | None = None


class ChatResponse(BaseModel):
    reply: str
    intent: str | None = None
    request_id: str
    session_id: str
    follow_up_actions: list[str] = []


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Process a patient message through the full AI workflow.

    Session history is loaded from Redis before the workflow runs and
    saved back to Redis after the response is generated.

    Rate limit: 60 requests/min per patient_id (REDIS_STRATEGY.md).
    """
    request_id = str(uuid.uuid4())
    session_id = request.session_id or str(uuid.uuid4())
    patient_id = request.patient_id or "anonymous"

    # ── Rate limiting (rate_limit:chat:{patient_id}) ──────────────────────
    allowed, count = await cache_service.check_rate_limit("chat", patient_id)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded: {count}/60 requests per minute.",
        )
    workflow   = _get_compiled_workflow()

    # ── Load session context from Redis ───────────────────────────────────
    history = await session_service.get_history(session_id)

    # If intent agent may be confused by a follow-up question, hint the last intent
    last_intent = await session_service.get_last_intent(session_id)

    initial_state: PatientState = {
        "request": {
            "message":     request.message,
            "patient_id":  request.patient_id or "",
            "tenant_id":   request.tenant_id  or "",
            # Carry last intent so planner has context for follow-ups
            "intent":      last_intent or "",
            "metadata":    {"conversation_history": history[-6:]},  # last 3 turns
        },
        "patient_context": {
            "patient_id": request.patient_id or "",
            "tenant_id":  request.tenant_id  or "",
            "request_id": request_id,
        },
    }

    try:
        final_state = await workflow.ainvoke(initial_state)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred processing your request. Please try again.",
        ) from exc

    intent       = final_state.get("request", {}).get("intent", "general")
    response_text = final_state.get("response", {}).get(
        "response_text",
        "I'm here to help. Could you please provide more details?",
    )
    follow_ups = final_state.get("response", {}).get("follow_up_actions", [])

    # Persist this turn to Redis
    await session_service.append_turn(
        session_id=session_id,
        user_message=request.message,
        assistant_reply=response_text,
        intent=intent,
    )

    return ChatResponse(
        reply=response_text,
        intent=intent,
        request_id=request_id,
        session_id=session_id,
        follow_up_actions=follow_ups,
    )


@router.post("/stream", status_code=status.HTTP_200_OK)
async def chat_stream(request: ChatRequest):
    """
    Streaming chat endpoint — same workflow as /chat with session history.
    Rate limit: 60 requests/min per patient_id.
    """
    request_id = str(uuid.uuid4())
    session_id = request.session_id or str(uuid.uuid4())
    patient_id = request.patient_id or "anonymous"

    allowed, count = await cache_service.check_rate_limit("chat", patient_id)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded: {count}/60 requests per minute.",
        )
    workflow   = _get_compiled_workflow()

    history     = await session_service.get_history(session_id)
    last_intent = await session_service.get_last_intent(session_id)

    initial_state: PatientState = {
        "request": {
            "message":    request.message,
            "patient_id": request.patient_id or "",
            "tenant_id":  request.tenant_id  or "",
            "intent":     last_intent or "",
            "metadata":   {"conversation_history": history[-6:]},
        },
        "patient_context": {
            "patient_id": request.patient_id or "",
            "tenant_id":  request.tenant_id  or "",
            "request_id": request_id,
        },
    }

    try:
        final_state = await workflow.ainvoke(initial_state)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred processing your request.",
        ) from exc

    intent        = final_state.get("request", {}).get("intent", "general")
    response_text = final_state.get("response", {}).get(
        "response_text",
        "I'm here to help. Could you please provide more details?",
    )

    await session_service.append_turn(
        session_id=session_id,
        user_message=request.message,
        assistant_reply=response_text,
        intent=intent,
    )

    async def token_generator():
        yield response_text

    return StreamingResponse(token_generator(), media_type="text/plain")


@router.get("/history/{session_id}", status_code=status.HTTP_200_OK)
async def get_history(session_id: str):
    """Return the conversation history for a session."""
    history = await session_service.get_history(session_id)
    last_intent = await session_service.get_last_intent(session_id)
    return {
        "session_id":   session_id,
        "message_count": len(history),
        "last_intent":  last_intent,
        "messages":     history,
    }


@router.delete("/history/{session_id}", status_code=status.HTTP_200_OK)
async def clear_history(session_id: str):
    """Clear conversation history for a session."""
    await session_service.clear(session_id)
    return {"session_id": session_id, "cleared": True}
