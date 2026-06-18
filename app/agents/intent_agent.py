from app.agents.interfaces import IntentAgent
from app.graph.state import PatientState


class IntentAgentImpl(IntentAgent):
    async def run(self, state: PatientState) -> PatientState:
        message = state.get("request", {}).get("message", "")
        lowered = message.lower()
        intent = "general"
        if "appointment" in lowered:
            intent = "appointment"
        elif "bill" in lowered or "billing" in lowered:
            intent = "billing"
        elif "insurance" in lowered:
            intent = "insurance"
        elif "refill" in lowered:
            intent = "refill"
        elif "case" in lowered:
            intent = "case"
        elif "timeline" in lowered or "why" in lowered:
            intent = "timeline"
        state.setdefault("request", {})["intent"] = intent
        return state
