from app.agents.interfaces import ResponseAgent
from app.graph.state import PatientState
from app.llm.wrapper import get_default_model
from app.llm.prompts.response import (
    RESPONSE_SYSTEM_PROMPT,
    get_response_generation_prompt,
)


class ResponseAgentImpl(ResponseAgent):
    """
    Response Agent generates patient-friendly responses.
    Converts technical outputs into clear communication.
    """

    def __init__(self):
        self.llm = get_default_model(temperature=0.3)

    async def run(self, state: PatientState) -> PatientState:
        message = state.get("request", {}).get("message", "")
        intent = state.get("request", {}).get("intent", "general")
        consent_valid = state.get("patient_context", {}).get("consent_valid", False)
        denial_reason = state.get("patient_context", {}).get("denial_reason")
        should_escalate = state.get("triage", {}).get("should_escalate", False)
        agent_outputs = state.get("execution", {}).get("agent_outputs", {})
        root_cause = state.get("timeline", {}).get("root_cause")

        # Short-circuit: consent was denied — return a clear, safe message
        if not consent_valid:
            state.setdefault("response", {})["response_text"] = (
                "We're unable to process your request at this time. "
                "Please ensure your consent preferences are up to date or contact your care team."
            )
            state.setdefault("response", {})["follow_up_actions"] = [
                "Contact your care team to update consent preferences."
            ]
            return state

        # If any specialist agent already produced a direct response, use it
        # before spending an LLM call on reformatting
        direct_response = self._extract_direct_response(agent_outputs)

        try:
            # Generate response
            prompt = get_response_generation_prompt(
                message=message,
                intent=intent,
                agent_outputs=agent_outputs,
                root_cause=root_cause,
                escalation=should_escalate,
            )

            response_text = await self.llm.ainvoke(
                prompt=prompt,
                system_prompt=RESPONSE_SYSTEM_PROMPT,
            )

            # Clean up response
            response_text = response_text.strip()

            # Remove any JSON formatting if present
            if response_text.startswith("{") and response_text.endswith("}"):
                import json
                try:
                    parsed = json.loads(response_text)
                    response_text = parsed.get("response", response_text)
                except Exception:
                    pass

            # If the LLM returned a generic/empty response, fall back to the
            # direct response extracted from the specialist agent output
            if (not response_text or len(response_text) < 30) and direct_response:
                response_text = direct_response

            state.setdefault("response", {})["response_text"] = response_text

            # Add follow-up actions if applicable
            follow_ups = []
            if should_escalate:
                follow_ups.append("A healthcare professional will review your request")
            if intent == "appointment":
                follow_ups.append("You can schedule appointments through this platform")
            if intent == "billing":
                follow_ups.append("Contact billing support for payment assistance")

            state.setdefault("response", {})["follow_up_actions"] = follow_ups

        except Exception as e:
            # Use direct agent response if available, else generic fallback
            fallback = direct_response or self._generate_fallback(intent, should_escalate, str(e))
            state.setdefault("response", {})["response_text"] = fallback
            state.setdefault("response", {})["follow_up_actions"] = []

        return state

    def _extract_direct_response(self, agent_outputs: dict) -> str | None:
        """
        Pull the best available response string out of specialist agent outputs.
        Agents store their result under a 'response' key inside their output dict.
        """
        for agent_name, output in agent_outputs.items():
            if isinstance(output, dict):
                response = output.get("response") or output.get("summary") or output.get("message")
                if response and isinstance(response, str) and len(response) > 20:
                    return response
        return None

    def _generate_fallback(self, intent: str, escalation: bool, error: str) -> str:
        """Generate fallback response when LLM fails."""
        # Consent denied — surface a clear message
        denial_note = ""
        if not escalation and not intent:
            return (
                "We were unable to process your request. "
                "Please ensure your patient profile is active and consent has been granted, "
                "or contact your care team for assistance."
            )

        if escalation:
            return (
                "Thank you for your message. Your request requires review by a "
                "qualified healthcare professional. A member of our team will contact you shortly."
            )

        intent_messages = {
            "appointment": "I can help you with appointment scheduling. Please provide more details.",
            "billing": "I can help you with billing questions. Your current information is being retrieved.",
            "insurance": "I can help you with insurance and claims. Let me look that up for you.",
            "refill": "I can help you track prescription refills. What medication are you asking about?",
            "case": "I can provide your case status. Let me gather that information.",
            "timeline": "I can look into the history of your account. Please give me a moment.",
        }

        return intent_messages.get(
            intent,
            "I'm here to help. Could you please provide more details about your question?",
        )
