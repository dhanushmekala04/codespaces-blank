from app.agents.interfaces import AuthorizationAgent
from app.graph.state import PatientState
from app.services.patient_service import PatientService


class AuthorizationAgentImpl(AuthorizationAgent):
    def __init__(self, patient_service: PatientService | None = None):
        self.patient_service = patient_service or PatientService()

    async def run(self, state: PatientState) -> PatientState:
        patient_id = state.get("request", {}).get("patient_id")

        if patient_id:
            try:
                patient = await self.patient_service.get_patient(patient_id)
                consent_valid = patient is not None
            except Exception:
                consent_valid = True
            state.setdefault("patient_context", {})["consent_valid"] = consent_valid
        else:
            state.setdefault("patient_context", {})["consent_valid"] = False

        return state
