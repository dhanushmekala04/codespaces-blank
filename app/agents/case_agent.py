from app.agents.interfaces import CaseAgent
from app.graph.state import PatientState


class CaseAgentImpl(CaseAgent):
    async def run(self, state: PatientState) -> PatientState:
        state.setdefault("execution", {})["agent_outputs"] = {}
        state["execution"]["agent_outputs"]["CaseAgent"] = {
            "status": "case handled"
        }
        return state
