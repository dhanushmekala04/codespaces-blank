from app.agents.interfaces import PlannerAgent
from app.graph.state import PatientState


class PlannerAgentImpl(PlannerAgent):
    async def run(self, state: PatientState) -> PatientState:
        intent = state.get("request", {}).get("intent", "")
        mapping = {
            "appointment": ["AppointmentAgent"],
            "billing": ["BillingAgent"],
            "insurance": ["InsuranceAgent"],
            "refill": ["RefillAgent"],
            "case": ["CaseAgent"],
            "timeline": ["EventInvestigationAgent"],
        }
        agents = mapping.get(intent, ["ResponseAgent"])
        state.setdefault("planning", {})["required_agents"] = agents
        return state
