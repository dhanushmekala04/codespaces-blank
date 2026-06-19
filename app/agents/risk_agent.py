from app.agents.interfaces import RiskAgent
from app.graph.state import PatientState
from app.llm.wrapper import get_glm_model
from app.llm.prompts.risk import RISK_SYSTEM_PROMPT, get_risk_assessment_prompt


class RiskAgentImpl(RiskAgent):
    """
    Risk Agent evaluates patient messages for safety concerns.
    Escalates emergency symptoms, self-harm, medical advice requests.
    """

    def __init__(self):
        self.llm = get_glm_model(temperature=0.0)

    async def run(self, state: PatientState) -> PatientState:
        message = state.get("request", {}).get("message", "")
        
        try:
            # Use LLM for risk assessment
            prompt = get_risk_assessment_prompt(message)
            result = await self.llm.ainvoke_structured(
                prompt=prompt,
                system_prompt=RISK_SYSTEM_PROMPT,
            )
            
            decision = result.get("decision", "SAFE")
            is_emergency = decision == "ESCALATE"
            priority = result.get("priority")
            
            state.setdefault("triage", {})["is_emergency"] = is_emergency
            state.setdefault("triage", {})["should_escalate"] = is_emergency
            state.setdefault("triage", {})["risk_flags"] = [result.get("reason", "")]
            state.setdefault("triage", {})["priority"] = priority
            
        except Exception as e:
            # Fallback to keyword-based detection
            emergency_keywords = [
                "chest pain", "breathing", "suicide", "self harm",
                "kill myself", "emergency", "bleeding", "stroke"
            ]
            is_emergency = any(keyword in message.lower() for keyword in emergency_keywords)
            state.setdefault("triage", {})["is_emergency"] = is_emergency
            state.setdefault("triage", {})["should_escalate"] = is_emergency
            state.setdefault("triage", {})["risk_flags"] = ["Fallback keyword detection"]
            
        return state
