from app.agents.interfaces import EventInvestigationAgent
from app.graph.state import PatientState
from app.llm.wrapper import get_default_model
from app.llm.prompts.event_investigation import (
    EVENT_INVESTIGATION_SYSTEM_PROMPT,
    get_event_investigation_prompt,
)
from app.services.event_service import EventService
from app.services.billing_service import BillingService
from app.services.insurance_service import InsuranceService


class EventInvestigationAgentImpl(EventInvestigationAgent):
    """
    Event Investigation Agent performs root cause analysis.
    Uses Nemotron model for deep reasoning over event timelines.
    """

    def __init__(
        self,
        event_service: EventService | None = None,
        billing_service: BillingService | None = None,
        insurance_service: InsuranceService | None = None,
    ):
        self.llm = get_default_model(temperature=0.1)
        self.event_service = event_service or EventService()
        self.billing_service = billing_service or BillingService()
        self.insurance_service = insurance_service or InsuranceService()

    async def run(self, state: PatientState) -> PatientState:
        patient_id = state.get("patient_context", {}).get("patient_id")
        message = state.get("request", {}).get("message", "")
        
        if not patient_id:
            state.setdefault("timeline", {})["root_cause"] = (
                "Unable to investigate: Patient ID not provided"
            )
            return state
        
        try:
            # Gather event data
            events = await self.event_service.get_patient_timeline(
                patient_id=patient_id,
                limit=50,
            )
            
            # Gather supporting data
            billing_data = None
            claims_data = None
            
            intent = state.get("request", {}).get("intent", "")
            if "billing" in intent or "bill" in message.lower():
                billing_data = await self.billing_service.get_billing_summary(patient_id)
            
            if "claim" in message.lower() or "insurance" in intent:
                claims_data = await self.insurance_service.get_patient_claims(patient_id)
            
            # Generate investigation prompt
            prompt = get_event_investigation_prompt(
                message=message,
                events=events,
                claims=claims_data,
                billing=billing_data,
            )
            
            # Use Nemotron for deep analysis
            result = await self.llm.ainvoke_structured(
                prompt=prompt,
                system_prompt=EVENT_INVESTIGATION_SYSTEM_PROMPT,
            )
            
            root_cause = result.get("root_cause", "Unable to determine root cause")
            evidence = result.get("evidence", [])
            confidence = result.get("confidence", 0.0)
            timeline_summary = result.get("timeline_summary", "")
            
            state.setdefault("timeline", {})["root_cause"] = root_cause
            state.setdefault("timeline", {})["evidence"] = evidence
            state.setdefault("timeline", {})["confidence"] = confidence
            state.setdefault("timeline", {})["timeline_summary"] = timeline_summary
            state.setdefault("timeline", {})["timeline_events"] = events[:10]  # Store recent events
            
            # Also set execution output
            state.setdefault("execution", {}).setdefault("agent_outputs", {})["EventInvestigationAgent"] = {
                "root_cause": root_cause,
                "confidence": confidence,
            }
            
        except Exception as e:
            state.setdefault("timeline", {})["root_cause"] = (
                f"Investigation failed: {str(e)}"
            )
            state.setdefault("timeline", {})["timeline_events"] = []
            state.setdefault("execution", {}).setdefault("agent_outputs", {})["EventInvestigationAgent"] = {
                "status": "failed",
                "error": str(e),
            }
            
        return state
