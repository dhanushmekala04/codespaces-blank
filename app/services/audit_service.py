"""AuditService — persists audit log entries to MongoDB."""

from datetime import datetime, timezone

from app.repositories.audit_repository import AuditRepository
from app.schemas.audit import AuditLogDocument


class AuditService:
    def __init__(self, audit_repository: AuditRepository | None = None):
        self.audit_repository = audit_repository or AuditRepository()

    async def log_event(
        self,
        request_id: str,
        action: str,
        outcome: str,
        actor_id: str | None = None,
        metadata: dict | None = None,
        latency_ms: int | None = None,
    ) -> AuditLogDocument:
        """Persist an audit log entry."""
        log = AuditLogDocument(
            request_id=request_id,
            actor_id=actor_id,
            action=action,
            outcome=outcome,
            metadata=metadata or {},
            latency_ms=latency_ms,
        )
        return await self.audit_repository.create(log)

    async def log_workflow_complete(
        self,
        request_id: str,
        patient_id: str,
        intent: str,
        outcome: str,
        agent_outputs: dict | None = None,
        latency_ms: int | None = None,
    ) -> AuditLogDocument:
        """Log a completed workflow run."""
        return await self.log_event(
            request_id=request_id,
            action="workflow_completed",
            outcome=outcome,
            actor_id=patient_id,
            metadata={
                "intent": intent,
                "agents_executed": list(agent_outputs.keys()) if agent_outputs else [],
            },
            latency_ms=latency_ms,
        )

    async def log_access_denied(
        self,
        request_id: str,
        patient_id: str,
        reason: str,
    ) -> AuditLogDocument:
        """Log an authorization failure."""
        return await self.log_event(
            request_id=request_id,
            action="access_denied",
            outcome="failure",
            actor_id=patient_id,
            metadata={"reason": reason},
        )

    async def get_request_logs(self, request_id: str) -> list[AuditLogDocument]:
        """Retrieve all log entries for a request."""
        return await self.audit_repository.get_by_request(request_id)
