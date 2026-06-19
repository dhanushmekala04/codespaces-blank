from app.agents.interfaces import PlannerAgent
from app.graph.state import PatientState
from app.llm.wrapper import get_default_model
from app.llm.prompts.planner import PLANNER_SYSTEM_PROMPT, get_planner_prompt


class PlannerAgentImpl(PlannerAgent):
    """
    Planner Agent determines which specialist agents should execute.
    Routes based on intent and message complexity.
    """

    def __init__(self):
        self.llm = get_default_model(temperature=0.0)

    async def run(self, state: PatientState) -> PatientState:
        intent = state.get("request", {}).get("intent", "general")
        message = state.get("request", {}).get("message", "")
        entities = state.get("request", {}).get("metadata", {}).get("entities", {})
        
        try:
            # Use LLM for planning
            prompt = get_planner_prompt(intent, message, entities)
            result = await self.llm.ainvoke_structured(
                prompt=prompt,
                system_prompt=PLANNER_SYSTEM_PROMPT,
            )
            
            agents = result.get("agents", [])
            execution_mode = result.get("execution_mode", "parallel")
            reasoning = result.get("reasoning", "")
            
            state.setdefault("planning", {})["required_agents"] = agents
            state.setdefault("planning", {})["execution_mode"] = execution_mode
            state.setdefault("planning", {})["plan_summary"] = reasoning
            
        except Exception as e:
            # Fallback to rule-based routing
            mapping = {
                "appointment": ["AppointmentAgent"],
                "billing": ["BillingAgent"],
                "insurance": ["InsuranceAgent"],
                "refill": ["RefillAgent"],
                "case": ["CaseAgent"],
                "timeline": ["EventInvestigationAgent"],
            }
            agents = mapping.get(intent, ["ResponseAgent"])

            # For "why" / root-cause questions also add EventInvestigationAgent
            if "why" in message.lower() and "EventInvestigationAgent" not in agents:
                agents.append("EventInvestigationAgent")

            state.setdefault("planning", {})["required_agents"] = agents
            state.setdefault("planning", {})["execution_mode"] = "sequential"
            state.setdefault("planning", {})["plan_summary"] = f"Fallback routing for {intent}"
            
        return state
