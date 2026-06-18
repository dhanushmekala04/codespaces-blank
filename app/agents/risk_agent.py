from app.agents.interfaces import RiskAgent
from app.graph.state import PatientState


class RiskAgentImpl(RiskAgent):
    async def run(self, state: PatientState) -> PatientState:
        message = state.get("request", {}).get("message", "")
        emergency_keywords = ["chest pain", "breathing", "suicide", "self harm"]
        is_emergency = any(keyword in message.lower() for keyword in emergency_keywords)
        state.setdefault("triage", {})["is_emergency"] = is_emergency
        state.setdefault("triage", {})["should_escalate"] = is_emergency
        return state
