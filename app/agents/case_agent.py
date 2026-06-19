from app.agents.interfaces import CaseAgent
from app.graph.state import PatientState
from app.llm.wrapper import get_default_model
from app.llm.prompts.case import CASE_SYSTEM_PROMPT, get_case_analysis_prompt
from app.services.appointment_service import AppointmentService
from app.services.insurance_service import InsuranceService
from app.services.billing_service import BillingService
from app.services.event_service import EventService


class CaseAgentImpl(CaseAgent):
    """
    Case Agent builds Patient 360 operational summaries.
    Uses Nemotron for comprehensive analysis across multiple data sources.
    """

    def __init__(
        self,
        appointment_service: AppointmentService | None = None,
        insurance_service: InsuranceService | None = None,
        billing_service: BillingService | None = None,
        event_service: EventService | None = None,
    ):
        self.llm = get_default_model(temperature=0.1)
        self.appointment_service = appointment_service or AppointmentService()
        self.insurance_service = insurance_service or InsuranceService()
        self.billing_service = billing_service or BillingService()
        self.event_service = event_service or EventService()

    async def run(self, state: PatientState) -> PatientState:
        patient_id = state.get("patient_context", {}).get("patient_id")
        message = state.get("request", {}).get("message", "")
        
        if not patient_id:
            state.setdefault("case", {})["case_summary"] = "Patient ID required"
            return state
        
        try:
            # Gather comprehensive data
            appointments = await self.appointment_service.get_patient_appointments(patient_id)
            claims = await self.insurance_service.get_patient_claims(patient_id)
            billing = await self.billing_service.get_billing_summary(patient_id)
            events = await self.event_service.get_patient_timeline(patient_id, limit=20)
            
            # Convert appointments to dicts
            appointments_data = [
                {
                    "scheduled_at": apt.scheduled_at.isoformat() if apt.scheduled_at else "",
                    "status": apt.status,
                    "reason": apt.reason or "",
                }
                for apt in appointments
            ] if appointments else None
            
            # Generate comprehensive analysis with Nemotron
            prompt = get_case_analysis_prompt(
                message=message,
                appointments=appointments_data,
                claims=claims,
                billing=billing,
                events=events,
            )
            
            result = await self.llm.ainvoke_structured(
                prompt=prompt,
                system_prompt=CASE_SYSTEM_PROMPT,
            )
            
            case_summary = result.get("case_summary", "No case information available")
            active_items = result.get("active_items", [])
            pending_items = result.get("pending_items", [])
            response = result.get("response", case_summary)
            
            state.setdefault("case", {})["case_summary"] = case_summary
            state.setdefault("case", {})["status"] = "analyzed"
            state.setdefault("case", {})["active_items"] = active_items
            state.setdefault("case", {})["pending_items"] = pending_items
            
            state.setdefault("execution", {}).setdefault("agent_outputs", {})["CaseAgent"] = {
                "summary": case_summary,
                "active_count": len(active_items),
                "response": response,
            }
            
        except Exception as e:
            state.setdefault("case", {})["case_summary"] = f"Analysis failed: {str(e)}"
            state.setdefault("execution", {}).setdefault("agent_outputs", {})["CaseAgent"] = {
                "status": "failed",
                "error": str(e),
            }
            
        return state
