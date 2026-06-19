from app.agents.interfaces import InsuranceAgent
from app.graph.state import PatientState
from app.llm.wrapper import get_default_model
from app.llm.prompts.insurance import INSURANCE_SYSTEM_PROMPT, get_insurance_prompt
from app.services.insurance_service import InsuranceService


class InsuranceAgentImpl(InsuranceAgent):
    """
    Insurance Agent handles insurance and claims queries.
    Uses GLM for claims analysis.
    """

    def __init__(self, insurance_service: InsuranceService | None = None):
        self.llm = get_default_model(temperature=0.1)
        self.insurance_service = insurance_service or InsuranceService()

    async def run(self, state: PatientState) -> PatientState:
        patient_id = state.get("patient_context", {}).get("patient_id")
        message = state.get("request", {}).get("message", "")
        
        if not patient_id:
            state.setdefault("execution", {}).setdefault("agent_outputs", {})["InsuranceAgent"] = {
                "status": "failed",
                "message": "Patient ID required",
            }
            return state
        
        try:
            # Get insurance info
            insurance = await self.insurance_service.get_patient_insurance(patient_id)
            insurance_data = None
            
            if insurance:
                insurance_data = {
                    "provider_name": getattr(insurance, "provider_name", "Unknown"),
                    "plan_name": getattr(insurance, "plan_name", "Unknown"),
                    "status": getattr(insurance, "status", "unknown"),
                }
            
            # Get claims
            claims_data = await self.insurance_service.get_patient_claims(patient_id)
            
            # Generate analysis
            prompt = get_insurance_prompt(message, insurance_data, claims_data)
            result = await self.llm.ainvoke_structured(
                prompt=prompt,
                system_prompt=INSURANCE_SYSTEM_PROMPT,
            )
            
            claim_status = result.get("claim_status", "No claims")
            denial_reason = result.get("denial_reason")
            response = result.get("response", "No insurance information available")
            
            state.setdefault("execution", {}).setdefault("agent_outputs", {})["InsuranceAgent"] = {
                "claim_status": claim_status,
                "denial_reason": denial_reason,
                "response": response,
            }
            
        except Exception as e:
            state.setdefault("execution", {}).setdefault("agent_outputs", {})["InsuranceAgent"] = {
                "status": "failed",
                "error": str(e),
                "message": "Unable to retrieve insurance information at this time.",
            }
            
        return state
