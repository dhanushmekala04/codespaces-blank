from langgraph.graph import END, StateGraph

from app.agents.authorization_agent import AuthorizationAgentImpl
from app.agents.risk_agent import RiskAgentImpl
from app.agents.intent_agent import IntentAgentImpl
from app.agents.planner_agent import PlannerAgentImpl
from app.agents.appointment_agent import AppointmentAgentImpl
from app.agents.billing_agent import BillingAgentImpl
from app.agents.insurance_agent import InsuranceAgentImpl
from app.agents.refill_agent import RefillAgentImpl
from app.agents.case_agent import CaseAgentImpl
from app.agents.event_agent import EventInvestigationAgentImpl
from app.agents.verification_agent import VerificationAgentImpl
from app.agents.reflection_agent import ReflectionAgentImpl
from app.agents.response_agent import ResponseAgentImpl
from app.agents.audit_agent import AuditAgentImpl
from app.graph.state import PatientState


async def authorization_node(state: PatientState) -> PatientState:
    return await AuthorizationAgentImpl().run(state)


async def risk_node(state: PatientState) -> PatientState:
    return await RiskAgentImpl().run(state)


async def intent_node(state: PatientState) -> PatientState:
    return await IntentAgentImpl().run(state)


async def planner_node(state: PatientState) -> PatientState:
    return await PlannerAgentImpl().run(state)


async def appointment_node(state: PatientState) -> PatientState:
    return await AppointmentAgentImpl().run(state)


async def billing_node(state: PatientState) -> PatientState:
    return await BillingAgentImpl().run(state)


async def insurance_node(state: PatientState) -> PatientState:
    return await InsuranceAgentImpl().run(state)


async def refill_node(state: PatientState) -> PatientState:
    return await RefillAgentImpl().run(state)


async def case_node(state: PatientState) -> PatientState:
    return await CaseAgentImpl().run(state)


async def event_node(state: PatientState) -> PatientState:
    return await EventInvestigationAgentImpl().run(state)


async def verification_node(state: PatientState) -> PatientState:
    return await VerificationAgentImpl().run(state)


async def reflection_node(state: PatientState) -> PatientState:
    return await ReflectionAgentImpl().run(state)


async def response_node(state: PatientState) -> PatientState:
    return await ResponseAgentImpl().run(state)


async def audit_node(state: PatientState) -> PatientState:
    return await AuditAgentImpl().run(state)


# ---------------------------------------------------------------------------
# Routing functions
# ---------------------------------------------------------------------------

def route_after_authorization(state: PatientState) -> str:
    """
    After authorization: proceed to risk check if consent granted,
    otherwise go straight to response (to surface denial message) then audit.
    """
    if state.get("patient_context", {}).get("consent_valid"):
        return "risk_agent"
    return "response_agent"


def route_after_risk(state: PatientState) -> str:
    """After risk triage: escalate emergencies directly to audit, otherwise classify intent."""
    if state.get("triage", {}).get("should_escalate"):
        return "response_agent"   # Response agent formats the escalation message
    return "intent_agent"


def route_after_planner(state: PatientState) -> str:
    """Route to the correct specialist based on classified intent."""
    intent = state.get("request", {}).get("intent", "")
    routing = {
        "appointment": "appointment_agent",
        "billing": "billing_agent",
        "insurance": "insurance_agent",
        "refill": "refill_agent",
        "case": "case_agent",
        "timeline": "event_agent",
    }
    return routing.get(intent, "response_agent")


# ---------------------------------------------------------------------------
# Graph construction
# ---------------------------------------------------------------------------

def build_workflow():
    workflow = StateGraph(PatientState)

    # Register nodes
    workflow.add_node("authorization_agent", authorization_node)
    workflow.add_node("risk_agent", risk_node)
    workflow.add_node("intent_agent", intent_node)
    workflow.add_node("planner_agent", planner_node)
    workflow.add_node("appointment_agent", appointment_node)
    workflow.add_node("billing_agent", billing_node)
    workflow.add_node("insurance_agent", insurance_node)
    workflow.add_node("refill_agent", refill_node)
    workflow.add_node("case_agent", case_node)
    workflow.add_node("event_agent", event_node)
    workflow.add_node("verification_agent", verification_node)
    workflow.add_node("reflection_agent", reflection_node)
    workflow.add_node("response_agent", response_node)
    workflow.add_node("audit_agent", audit_node)

    # Entry point
    workflow.set_entry_point("authorization_agent")

    # Authorization → risk (consent OK) or response (consent denied)
    workflow.add_conditional_edges(
        "authorization_agent",
        route_after_authorization,
        {
            "risk_agent": "risk_agent",
            "response_agent": "response_agent",
        },
    )

    # Risk → intent (safe) or response (escalate)
    workflow.add_conditional_edges(
        "risk_agent",
        route_after_risk,
        {
            "intent_agent": "intent_agent",
            "response_agent": "response_agent",
        },
    )

    # Intent → Planner (always)
    workflow.add_edge("intent_agent", "planner_agent")

    # Planner → specialist or fallback response
    workflow.add_conditional_edges(
        "planner_agent",
        route_after_planner,
        {
            "appointment_agent": "appointment_agent",
            "billing_agent": "billing_agent",
            "insurance_agent": "insurance_agent",
            "refill_agent": "refill_agent",
            "case_agent": "case_agent",
            "event_agent": "event_agent",
            "response_agent": "response_agent",
        },
    )

    # All specialists → verification
    for specialist in (
        "appointment_agent",
        "billing_agent",
        "insurance_agent",
        "refill_agent",
        "case_agent",
        "event_agent",
    ):
        workflow.add_edge(specialist, "verification_agent")

    # Verification → reflection → response → audit → END
    workflow.add_edge("verification_agent", "reflection_agent")
    workflow.add_edge("reflection_agent", "response_agent")
    workflow.add_edge("response_agent", "audit_agent")
    workflow.add_edge("audit_agent", END)

    return workflow.compile()
