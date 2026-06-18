from app.agents.interfaces import ReflectionAgent
from app.graph.state import PatientState


class ReflectionAgentImpl(ReflectionAgent):
    async def run(self, state: PatientState) -> PatientState:
        state.setdefault("reflection", {})["needs_replan"] = False
        state.setdefault("reflection", {})["missing_intents"] = []
        return state
