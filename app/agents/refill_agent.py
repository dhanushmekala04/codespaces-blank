from app.agents.interfaces import RefillAgent
from app.graph.state import PatientState
from app.llm.wrapper import get_default_model
from app.llm.prompts.refill import REFILL_SYSTEM_PROMPT, get_refill_prompt
from app.services.refill_service import RefillService


class RefillAgentImpl(RefillAgent):
    """
    Refill Agent handles prescription refill tracking.

    NOTE: Does NOT provide medication advice, dosage recommendations,
    or clinical guidance. Only tracks refill status and requests.
    All clinical decisions require a licensed healthcare provider.
    """

    def __init__(self, refill_service: RefillService | None = None):
        self.llm = get_default_model(temperature=0.1)
        self.refill_service = refill_service or RefillService()

    async def run(self, state: PatientState) -> PatientState:
        patient_id = state.get("patient_context", {}).get("patient_id")
        message = state.get("request", {}).get("message", "")

        if not patient_id:
            state.setdefault("execution", {}).setdefault("agent_outputs", {})["RefillAgent"] = {
                "status": "failed",
                "message": "Patient ID required",
            }
            return state

        try:
            # Get refill status and medication list
            refill_status = await self.refill_service.get_refill_status(patient_id)
            medications = await self.refill_service.get_active_medications(patient_id)
            refill_history = await self.refill_service.get_refill_history(patient_id)

            # Generate LLM-powered summary
            prompt = get_refill_prompt(
                message=message,
                refill_status=refill_status,
                medications=medications,
                history=refill_history,
            )
            result = await self.llm.ainvoke_structured(
                prompt=prompt,
                system_prompt=REFILL_SYSTEM_PROMPT,
            )

            summary = result.get("summary", refill_status.get("message", "No pending refills"))
            pending = result.get("pending_refills", refill_status.get("pending_refills", []))
            response = result.get("response", summary)

            state.setdefault("execution", {}).setdefault("agent_outputs", {})["RefillAgent"] = {
                "summary": summary,
                "pending_count": len(pending),
                "response": response,
                "safety_note": "For medication questions, please contact your healthcare provider.",
            }

        except Exception as e:
            # Fallback — always inform patient to contact provider
            state.setdefault("execution", {}).setdefault("agent_outputs", {})["RefillAgent"] = {
                "status": "failed",
                "error": str(e),
                "message": (
                    "Refill tracking is temporarily unavailable. "
                    "Please contact your healthcare provider for refill requests."
                ),
                "safety_note": "For medication questions, please contact your healthcare provider.",
            }

        return state
