from app.agents.interfaces import AuditAgent
from app.graph.state import PatientState


class AuditAgentImpl(AuditAgent):
    async def run(self, state: PatientState) -> PatientState:
        state.setdefault("audit", {})["audit_trace"] = []
        state["audit"]["audit_trace"].append(
            {
                "event": "workflow_completed",
                "request_id": state.get("patient_context", {}).get("request_id", "unknown"),
            }
        )
        return state
