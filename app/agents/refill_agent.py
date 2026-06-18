from app.agents.interfaces import RefillAgent
from app.graph.state import PatientState


class RefillAgentImpl(RefillAgent):
    async def run(self, state: PatientState) -> PatientState:
        state.setdefault("execution", {})["agent_outputs"] = {}
        state["execution"]["agent_outputs"]["RefillAgent"] = {
            "status": "refill handled"
        }
        return state
