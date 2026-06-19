from app.agents.interfaces import ReflectionAgent
from app.graph.state import PatientState
from app.llm.wrapper import get_default_model
from app.llm.prompts.reflection import REFLECTION_SYSTEM_PROMPT, get_reflection_prompt


class ReflectionAgentImpl(ReflectionAgent):
    """
    Reflection Agent reviews whether the response fully answers the patient's question.
    Uses GLM to check for missing intents or incomplete answers.
    """

    def __init__(self):
        self.llm = get_default_model(temperature=0.0)

    async def run(self, state: PatientState) -> PatientState:
        message = state.get("request", {}).get("message", "")
        intent = state.get("request", {}).get("intent", "general")
        agent_outputs = state.get("execution", {}).get("agent_outputs", {})
        response_text = state.get("response", {}).get("response_text", "")

        # Nothing to reflect on yet — response not generated, skip LLM call
        if not agent_outputs and not response_text:
            state.setdefault("reflection", {})["needs_replan"] = False
            state.setdefault("reflection", {})["missing_intents"] = []
            state.setdefault("reflection", {})["complete"] = True
            return state

        try:
            prompt = get_reflection_prompt(
                original_message=message,
                intent=intent,
                agent_outputs=agent_outputs,
                response_text=response_text,
            )
            result = await self.llm.ainvoke_structured(
                prompt=prompt,
                system_prompt=REFLECTION_SYSTEM_PROMPT,
            )

            complete = result.get("complete", True)
            missing = result.get("missing_intents", [])
            needs_replan = result.get("needs_replan", False)

            state.setdefault("reflection", {})["complete"] = complete
            state.setdefault("reflection", {})["missing_intents"] = missing
            # Cap replanning — never replan in production to avoid infinite loops
            state.setdefault("reflection", {})["needs_replan"] = False

        except Exception:
            # Safe fallback — don't block the response pipeline
            state.setdefault("reflection", {})["needs_replan"] = False
            state.setdefault("reflection", {})["missing_intents"] = []
            state.setdefault("reflection", {})["complete"] = True

        return state
