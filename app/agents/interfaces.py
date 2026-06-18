from app.graph.state import PatientState


class AuthorizationAgent:
    async def run(self, state: PatientState) -> PatientState:
        return state


class RiskAgent:
    async def run(self, state: PatientState) -> PatientState:
        return state


class IntentAgent:
    async def run(self, state: PatientState) -> PatientState:
        return state


class PlannerAgent:
    async def run(self, state: PatientState) -> PatientState:
        return state


class AppointmentAgent:
    async def run(self, state: PatientState) -> PatientState:
        return state


class BillingAgent:
    async def run(self, state: PatientState) -> PatientState:
        return state


class InsuranceAgent:
    async def run(self, state: PatientState) -> PatientState:
        return state


class RefillAgent:
    async def run(self, state: PatientState) -> PatientState:
        return state


class CaseAgent:
    async def run(self, state: PatientState) -> PatientState:
        return state


class EventInvestigationAgent:
    async def run(self, state: PatientState) -> PatientState:
        return state


class VerificationAgent:
    async def run(self, state: PatientState) -> PatientState:
        return state


class ReflectionAgent:
    async def run(self, state: PatientState) -> PatientState:
        return state


class ResponseAgent:
    async def run(self, state: PatientState) -> PatientState:
        return state


class AuditAgent:
    async def run(self, state: PatientState) -> PatientState:
        return state
