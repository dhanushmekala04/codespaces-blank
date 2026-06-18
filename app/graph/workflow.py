from typing import Literal

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


def route_after_risk(state: PatientState) -> str:
    if state.get("triage", {}).get("should_escalate"):
        return "audit_agent"
    return "intent_agent"


def route_after_planner(state: PatientState) -> str:
    intent = state.get("request", {}).get("intent", "")
    if intent == "appointment":
        return "appointment_agent"
    if intent == "billing":
        return "billing_agent"
    if intent == "insurance":
        return "insurance_agent"
    if intent == "refill":
        return "refill_agent"
    if intent == "case":
        return "case_agent"
    if intent == "timeline":
        return "event_agent"
    return "response_agent"


def build_workflow():
    workflow = StateGraph(PatientState)
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

    workflow.set_entry_point("authorization_agent")
    workflow.add_conditional_edges(
        "authorization_agent",
        lambda state: "risk_agent" if state.get("patient_context", {}).get("consent_valid") else "audit_agent",
    )
    workflow.add_conditional_edges(
        "risk_agent",
        route_after_risk,
    )
    workflow.add_edge("intent_agent", "planner_agent")
    workflow.add_conditional_edges(
        "planner_agent",
        route_after_planner,
    )
    workflow.add_edge("appointment_agent", "verification_agent")
    workflow.add_edge("billing_agent", "verification_agent")
    workflow.add_edge("insurance_agent", "verification_agent")
    workflow.add_edge("refill_agent", "verification_agent")
    workflow.add_edge("case_agent", "verification_agent")
    workflow.add_edge("event_agent", "verification_agent")
    workflow.add_edge("verification_agent", "reflection_agent")
    workflow.add_edge("reflection_agent", "response_agent")
    workflow.add_edge("response_agent", "audit_agent")
    workflow.add_edge("audit_agent", END)
    return workflow.compile()
