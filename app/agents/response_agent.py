from app.agents.interfaces import ResponseAgent
from app.graph.state import PatientState


class ResponseAgentImpl(ResponseAgent):
    async def run(self, state: PatientState) -> PatientState:
        message = state.get("request", {}).get("message", "")
        state.setdefault("response", {})["response_text"] = f"Handled request: {message}"
        state.setdefault("response", {})["follow_up_actions"] = []
        return state
