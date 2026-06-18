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
        metadata: dict | None = None,
        latency_ms: int | None = None,
    ) -> AuditLogDocument:
        log = AuditLogDocument(
            request_id=request_id,
            action=action,
            outcome=outcome,
            metadata=metadata or {},
            latency_ms=latency_ms,
        )
        return await self.audit_repository.create(log)
