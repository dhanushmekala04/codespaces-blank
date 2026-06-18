from dataclasses import dataclass


@dataclass(frozen=True)
class AgentModelConfig:
    reasoning_model: str = "GLM-5.1"
    deep_reasoning_model: str = "Nemotron-3 Super 120B A12B"


AGENT_MODEL_MAP = {
    "AuthorizationAgent": "No LLM / Rules",
    "RiskAgent": "GLM-5.1",
    "IntentAgent": "GLM-5.1",
    "PlannerAgent": "GLM-5.1",
    "AppointmentAgent": "GLM-5.1",
    "BillingAgent": "GLM-5.1",
    "InsuranceAgent": "GLM-5.1",
    "RefillAgent": "GLM-5.1",
    "CaseAgent": "Nemotron-3 Super 120B A12B",
    "EventInvestigationAgent": "Nemotron-3 Super 120B A12B",
    "VerificationAgent": "GLM-5.1",
    "ReflectionAgent": "GLM-5.1",
    "ResponseAgent": "GLM-5.1",
    "AuditAgent": "No LLM Required",
}
