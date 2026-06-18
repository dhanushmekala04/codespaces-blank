from app.agents.interfaces import AppointmentAgent
from app.graph.state import PatientState


class AppointmentAgentImpl(AppointmentAgent):
    async def run(self, state: PatientState) -> PatientState:
        state.setdefault("execution", {})["agent_outputs"] = {}
        state["execution"]["agent_outputs"]["AppointmentAgent"] = {
            "status": "appointment handled"
        }
        return state
