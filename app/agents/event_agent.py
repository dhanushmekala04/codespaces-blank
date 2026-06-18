from app.agents.interfaces import EventInvestigationAgent
from app.graph.state import PatientState


class EventInvestigationAgentImpl(EventInvestigationAgent):
    async def run(self, state: PatientState) -> PatientState:
        state.setdefault("execution", {})["agent_outputs"] = {}
        state["execution"]["agent_outputs"]["EventInvestigationAgent"] = {
            "status": "timeline handled"
        }
        return state
