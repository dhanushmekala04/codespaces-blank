from app.agents.interfaces import InsuranceAgent
from app.graph.state import PatientState


class InsuranceAgentImpl(InsuranceAgent):
    async def run(self, state: PatientState) -> PatientState:
        state.setdefault("execution", {})["agent_outputs"] = {}
        state["execution"]["agent_outputs"]["InsuranceAgent"] = {
            "status": "insurance handled"
        }
        return state
