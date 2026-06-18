from app.agents.interfaces import VerificationAgent
from app.graph.state import PatientState


class VerificationAgentImpl(VerificationAgent):
    async def run(self, state: PatientState) -> PatientState:
        state.setdefault("verification", {})["is_verified"] = True
        state.setdefault("verification", {})["verification_notes"] = ["validated"]
        return state
