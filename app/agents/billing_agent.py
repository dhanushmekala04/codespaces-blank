from app.agents.interfaces import BillingAgent
from app.graph.state import PatientState


class BillingAgentImpl(BillingAgent):
    async def run(self, state: PatientState) -> PatientState:
        state.setdefault("execution", {})["agent_outputs"] = {}
        state["execution"]["agent_outputs"]["BillingAgent"] = {
            "status": "billing handled"
        }
        return state
