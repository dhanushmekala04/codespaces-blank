from app.agents.interfaces import AuthorizationAgent
from app.graph.state import PatientState
from app.services.patient_service import PatientService


class AuthorizationAgentImpl(AuthorizationAgent):
    """
    Authorization Agent — the gateway for every workflow run.

    Responsibilities:
    1. Validate the patient exists and is active.
    2. Verify consent has been granted (not just pending or revoked).
    3. Populate patient_context so all downstream agents have the IDs they need.

    Fail-safe: any exception → consent_valid = False. We never grant access
    on an error because the downstream agents assume verified identity.
    """

    def __init__(self, patient_service: PatientService | None = None):
        self.patient_service = patient_service or PatientService()

    async def run(self, state: PatientState) -> PatientState:
        request = state.get("request", {})
        patient_id = request.get("patient_id", "")
        tenant_id = request.get("tenant_id", "")
        request_id = state.get("patient_context", {}).get("request_id", "")

        # Always initialise patient_context so downstream agents can rely on it
        patient_context = state.setdefault("patient_context", {})
        patient_context["patient_id"] = patient_id
        patient_context["tenant_id"] = tenant_id
        if request_id:
            patient_context["request_id"] = request_id

        if not patient_id:
            patient_context["consent_valid"] = False
            patient_context["denial_reason"] = "patient_id missing from request"
            return state

        try:
            # Check patient exists, is active, and has granted consent
            patient = await self.patient_service.get_patient(patient_id)

            if patient is None:
                patient_context["consent_valid"] = False
                patient_context["denial_reason"] = "patient not found"
                return state

            has_consent = await self.patient_service.has_consent(patient_id)

            if not has_consent:
                patient_context["consent_valid"] = False
                patient_context["denial_reason"] = (
                    f"consent not granted (status: {patient.consent_status})"
                )
                return state

            # All checks passed
            patient_context["consent_valid"] = True
            patient_context["denial_reason"] = None
            # Carry over tenant from DB record in case it differs from request
            if patient.tenant_id:
                patient_context["tenant_id"] = patient.tenant_id

        except Exception as e:
            # Fail-safe: never grant access on an unexpected error
            patient_context["consent_valid"] = False
            patient_context["denial_reason"] = f"authorization check failed: {str(e)}"

        return state
