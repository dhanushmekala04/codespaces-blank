from app.agents.interfaces import AuditAgent
from app.graph.state import PatientState
from app.services.audit_service import AuditService


class AuditAgentImpl(AuditAgent):
    def __init__(self, audit_service: AuditService | None = None):
        self.audit_service = audit_service or AuditService()

    async def run(self, state: PatientState) -> PatientState:
        request_id = state.get("patient_context", {}).get("request_id", "unknown")
        patient_id = state.get("patient_context", {}).get("patient_id", "unknown")
        intent = state.get("request", {}).get("intent", "unknown")
        consent_valid = state.get("patient_context", {}).get("consent_valid", False)
        agent_outputs = state.get("execution", {}).get("agent_outputs", {})
        response_text = state.get("response", {}).get("response_text", "")

        # Determine outcome
        if not consent_valid:
            outcome = "access_denied"
        elif state.get("triage", {}).get("should_escalate"):
            outcome = "escalated"
        elif agent_outputs:
            failed_agents = [k for k, v in agent_outputs.items() if isinstance(v, dict) and v.get("status") == "failed"]
            outcome = "partial_failure" if failed_agents else "success"
        else:
            outcome = "success"

        trace_entry = {
            "event": "workflow_completed",
            "request_id": request_id,
            "intent": intent,
            "outcome": outcome,
            "agents_executed": list(agent_outputs.keys()),
        }

        state.setdefault("audit", {})["audit_trace"] = [trace_entry]

        # Persist to MongoDB
        try:
            await self.audit_service.log_workflow_complete(
                request_id=request_id,
                patient_id=patient_id,
                intent=intent,
                outcome=outcome,
                agent_outputs=agent_outputs,
            )
        except Exception:
            # Audit failure must never break the response pipeline
            pass

        return state
