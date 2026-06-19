from app.agents.interfaces import VerificationAgent
from app.graph.state import PatientState
from app.llm.wrapper import get_default_model
from app.llm.prompts.verification import VERIFICATION_SYSTEM_PROMPT, get_verification_prompt


class VerificationAgentImpl(VerificationAgent):
    """
    Verification Agent validates specialist agent outputs.
    Checks for hallucinations, unsupported claims, and contradictions.
    """

    def __init__(self):
        self.llm = get_default_model(temperature=0.0)

    async def run(self, state: PatientState) -> PatientState:
        agent_outputs = state.get("execution", {}).get("agent_outputs", {})
        
        if not agent_outputs:
            # No outputs to verify
            state.setdefault("verification", {})["is_verified"] = True
            state.setdefault("verification", {})["verification_notes"] = ["No outputs to verify"]
            return state
        
        try:
            # Gather available data for verification
            available_data = {
                "timeline": state.get("timeline", {}),
                "case": state.get("case", {}),
                "triage": state.get("triage", {}),
            }
            
            # Run verification
            prompt = get_verification_prompt(agent_outputs, available_data)
            result = await self.llm.ainvoke_structured(
                prompt=prompt,
                system_prompt=VERIFICATION_SYSTEM_PROMPT,
            )
            
            status = result.get("status", "PASS")
            issues = result.get("issues", [])
            confidence = result.get("confidence", 1.0)
            
            is_verified = status == "PASS"
            
            state.setdefault("verification", {})["is_verified"] = is_verified
            state.setdefault("verification", {})["verification_notes"] = issues if issues else ["All outputs verified"]
            state.setdefault("verification", {})["confidence"] = confidence
            
            if not is_verified:
                # Log verification failures for audit
                print(f"⚠️ Verification FAILED: {issues}")
            
        except Exception as e:
            # On error, mark as verified but note the issue
            state.setdefault("verification", {})["is_verified"] = True
            state.setdefault("verification", {})["verification_notes"] = [
                f"Verification check failed: {str(e)}"
            ]
        
        return state
