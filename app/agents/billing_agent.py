from app.agents.interfaces import BillingAgent
from app.graph.state import PatientState
from app.llm.wrapper import get_default_model
from app.llm.prompts.billing import BILLING_SYSTEM_PROMPT, get_billing_prompt
from app.services.billing_service import BillingService


class BillingAgentImpl(BillingAgent):
    """
    Billing Agent analyzes patient billing information.
    Uses GLM for billing explanations.
    """

    def __init__(self, billing_service: BillingService | None = None):
        self.llm = get_default_model(temperature=0.1)
        self.billing_service = billing_service or BillingService()

    async def run(self, state: PatientState) -> PatientState:
        patient_id = state.get("patient_context", {}).get("patient_id")
        message = state.get("request", {}).get("message", "")
        
        if not patient_id:
            state.setdefault("execution", {}).setdefault("agent_outputs", {})["BillingAgent"] = {
                "status": "failed",
                "message": "Patient ID required",
            }
            return state
        
        try:
            # Get billing data
            billing_data = await self.billing_service.get_billing_summary(patient_id)
            
            # Generate analysis
            prompt = get_billing_prompt(message, billing_data)
            result = await self.llm.ainvoke_structured(
                prompt=prompt,
                system_prompt=BILLING_SYSTEM_PROMPT,
            )
            
            balance = result.get("balance", 0.0)
            charges_summary = result.get("charges_summary", "No charges")
            response = result.get("response", charges_summary)
            
            state.setdefault("execution", {}).setdefault("agent_outputs", {})["BillingAgent"] = {
                "balance": balance,
                "summary": charges_summary,
                "response": response,
            }
            
        except Exception as e:
            state.setdefault("execution", {}).setdefault("agent_outputs", {})["BillingAgent"] = {
                "status": "failed",
                "error": str(e),
                "message": "Unable to retrieve billing information at this time.",
            }
            
        return state
