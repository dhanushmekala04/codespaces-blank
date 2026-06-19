from app.agents.interfaces import AppointmentAgent
from app.graph.state import PatientState
from app.llm.wrapper import get_default_model
from app.llm.prompts.appointment import APPOINTMENT_SYSTEM_PROMPT, get_appointment_prompt
from app.services.appointment_service import AppointmentService


class AppointmentAgentImpl(AppointmentAgent):
    """
    Appointment Agent handles appointment-related queries.
    Uses GLM for fast appointment information retrieval.
    """

    def __init__(self, appointment_service: AppointmentService | None = None):
        self.llm = get_default_model(temperature=0.1)
        self.appointment_service = appointment_service or AppointmentService()

    async def run(self, state: PatientState) -> PatientState:
        patient_id = state.get("patient_context", {}).get("patient_id")
        message = state.get("request", {}).get("message", "")
        
        if not patient_id:
            state.setdefault("execution", {}).setdefault("agent_outputs", {})["AppointmentAgent"] = {
                "status": "failed",
                "message": "Patient ID required",
            }
            return state
        
        try:
            # Get appointments
            appointments = await self.appointment_service.get_patient_appointments(patient_id)
            
            # Convert to dict for LLM
            appointments_data = [
                {
                    "_id": str(apt.id),
                    "appointment_id": getattr(apt, "appointment_id", str(apt.id)),
                    "scheduled_at": apt.scheduled_at.isoformat() if apt.scheduled_at else "unknown",
                    "status": apt.status,
                    "reason": apt.reason or "",
                    "provider_id": apt.provider_id or "",
                    "notes": apt.notes or "",
                }
                for apt in appointments
            ]
            
            # Generate analysis
            prompt = get_appointment_prompt(message, appointments_data)
            result = await self.llm.ainvoke_structured(
                prompt=prompt,
                system_prompt=APPOINTMENT_SYSTEM_PROMPT,
            )
            
            summary = result.get("summary", "No appointments found")
            upcoming = result.get("upcoming_appointments", [])
            response = result.get("response", summary)
            
            state.setdefault("execution", {}).setdefault("agent_outputs", {})["AppointmentAgent"] = {
                "summary": summary,
                "upcoming_count": len(upcoming),
                "response": response,
            }
            
        except Exception as e:
            state.setdefault("execution", {}).setdefault("agent_outputs", {})["AppointmentAgent"] = {
                "status": "failed",
                "error": str(e),
                "message": "Unable to retrieve appointments at this time.",
            }
            
        return state
