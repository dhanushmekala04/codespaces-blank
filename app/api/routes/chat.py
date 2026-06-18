from fastapi import APIRouter
from pydantic import BaseModel

from app.graph.state import PatientState
from app.graph.workflow import build_workflow

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    patient_id: str | None = None


class ChatResponse(BaseModel):
    reply: str
    intent: str | None = None


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    workflow = build_workflow()

    state: PatientState = {
        "request": {
            "message": request.message,
            "patient_id": request.patient_id,
        },
        "patient_context": {
            "patient_id": request.patient_id,
            "request_id": f"req-{request.patient_id or 'anon'}",
        },
    }

    final_state = await workflow.ainvoke(state)
    request_intent = final_state.get("request", {}).get("intent", "general")
    response_text = final_state.get("response", {}).get(
        "response_text",
        f"Request received for intent '{request_intent}'.",
    )

    return ChatResponse(
        reply=response_text,
        intent=request_intent,
    )


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    return {
        "message": request.message,
        "patient_id": request.patient_id,
        "status": "streaming not implemented",
    }
