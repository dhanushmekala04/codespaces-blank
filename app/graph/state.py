from typing import TypedDict


class PatientContext(TypedDict, total=False):
    patient_id: str
    tenant_id: str
    consent_valid: bool
    request_id: str
    denial_reason: str | None  # populated when consent_valid is False


class RequestState(TypedDict, total=False):
    message: str
    patient_id: str
    tenant_id: str
    intent: str
    metadata: dict


class TriageState(TypedDict, total=False):
    is_emergency: bool
    should_escalate: bool
    risk_flags: list[str]
    priority: str | None  # "CRITICAL", "HIGH", or None


class PlanningState(TypedDict, total=False):
    required_agents: list[str]
    plan_summary: str
    execution_mode: str  # "sequential" or "parallel"


class ExecutionState(TypedDict, total=False):
    agent_outputs: dict


class TimelineState(TypedDict, total=False):
    timeline_events: list[dict]
    root_cause: str


class CaseState(TypedDict, total=False):
    case_summary: str
    status: str


class VerificationState(TypedDict, total=False):
    is_verified: bool
    verification_notes: list[str]


class ReflectionState(TypedDict, total=False):
    missing_intents: list[str]
    needs_replan: bool


class ResponseState(TypedDict, total=False):
    response_text: str
    follow_up_actions: list[str]


class AuditState(TypedDict, total=False):
    audit_trace: list[dict]


class PatientState(TypedDict, total=False):
    request: RequestState
    patient_context: PatientContext
    triage: TriageState
    planning: PlanningState
    execution: ExecutionState
    timeline: TimelineState
    case: CaseState
    verification: VerificationState
    reflection: ReflectionState
    response: ResponseState
    audit: AuditState
