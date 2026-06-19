from app.agents.interfaces import IntentAgent
from app.graph.state import PatientState
from app.llm.wrapper import get_default_model
from app.llm.prompts.intent import INTENT_SYSTEM_PROMPT, get_intent_classification_prompt


class IntentAgentImpl(IntentAgent):
    """
    Intent Agent classifies user requests and extracts entities.
    Uses the fast model for low-latency intent detection.
    """

    def __init__(self):
        self.llm = get_default_model(temperature=0.0)

    async def run(self, state: PatientState) -> PatientState:
        message = state.get("request", {}).get("message", "")
        
        try:
            # Use LLM for intent classification
            prompt = get_intent_classification_prompt(message)
            result = await self.llm.ainvoke_structured(
                prompt=prompt,
                system_prompt=INTENT_SYSTEM_PROMPT,
            )
            
            intent = result.get("intent", "general")
            entities = result.get("entities", {})
            confidence = result.get("confidence", 0.0)
            
            state.setdefault("request", {})["intent"] = intent
            state.setdefault("request", {})["metadata"] = {
                "entities": entities,
                "confidence": confidence,
            }
            
        except Exception as e:
            # Fallback to keyword-based classification
            lowered = message.lower()
            intent = "general"

            if any(w in lowered for w in ("appointment", "schedule", "reschedule", "cancel")):
                intent = "appointment"
            elif any(w in lowered for w in ("bill", "billing", "balance", "payment", "charge", "owe")):
                intent = "billing"
            elif any(w in lowered for w in ("insurance", "claim", "coverage", "denied", "denial")):
                intent = "insurance"
            elif any(w in lowered for w in ("refill", "prescription", "medication")):
                intent = "refill"
            elif any(w in lowered for w in ("case", "status", "update", "open case")):
                intent = "case"
            elif any(w in lowered for w in ("why", "what happened", "root cause", "investigate", "timeline", "history")):
                intent = "timeline"
                
            state.setdefault("request", {})["intent"] = intent
            state.setdefault("request", {})["metadata"] = {"fallback": True}
            
        return state
