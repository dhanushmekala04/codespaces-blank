"""
Seed sample data for PatientCare Platform testing.

Usage:
    python -m scripts.seed_sample_data            # seed (skip if data exists)
    python -m scripts.seed_sample_data --reset    # drop + re-seed
    python -m scripts.seed_sample_data --dry-run  # print counts only

Test patients created:
    PAT001 — John Doe   (consent granted, active insurance, denied claim)
    PAT002 — Jane Smith (consent granted, active insurance, approved claim)
"""

import argparse
import asyncio
import sys
from datetime import datetime, timedelta, timezone

# ---------------------------------------------------------------------------
# Bootstrap path so we can run as  python -m scripts.seed_sample_data
# ---------------------------------------------------------------------------
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.mongo import close_mongo, get_database, init_mongo
from app.schemas.event import EventTypes

NOW = datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def dt(days_offset: int) -> datetime:
    """Return UTC datetime offset from now by days_offset days."""
    return NOW + timedelta(days=days_offset)


async def upsert_many(collection, docs: list[dict], id_field: str = "_id") -> int:
    """Insert docs, replacing any with the same _id."""
    from pymongo import ReplaceOne
    ops = [ReplaceOne({id_field: d[id_field]}, d, upsert=True) for d in docs]
    result = await collection.bulk_write(ops)
    return result.upserted_count + result.modified_count


async def drop_collections(db, names: list[str]) -> None:
    for name in names:
        await db[name].delete_many({})


# ---------------------------------------------------------------------------
# Patients  (match PatientDocument schema exactly)
# ---------------------------------------------------------------------------

PATIENTS = [
    {
        "_id": "PAT001",
        "patient_id": "PAT001",
        "tenant_id": "TENANT001",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "+1-555-0101",
        "date_of_birth": "1980-01-15",
        "status": "active",
        "consent_status": "granted",          # ← required for authorization to pass
        "preferred_language": "en",
        "is_deleted": False,
        "created_at": dt(-180),
        "updated_at": dt(-1),
    },
    {
        "_id": "PAT002",
        "patient_id": "PAT002",
        "tenant_id": "TENANT001",
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane.smith@example.com",
        "phone": "+1-555-0202",
        "date_of_birth": "1975-06-22",
        "status": "active",
        "consent_status": "granted",
        "preferred_language": "en",
        "is_deleted": False,
        "created_at": dt(-180),
        "updated_at": dt(-1),
    },
    {
        "_id": "PAT003",
        "patient_id": "PAT003",
        "tenant_id": "TENANT001",
        "first_name": "Carlos",
        "last_name": "Rivera",
        "email": "carlos.rivera@example.com",
        "phone": "+1-555-0303",
        "date_of_birth": "1990-03-10",
        "status": "active",
        "consent_status": "revoked",          # ← tests consent-denied path
        "preferred_language": "es",
        "is_deleted": False,
        "created_at": dt(-90),
        "updated_at": dt(-10),
    },
]


# ---------------------------------------------------------------------------
# Appointments  (match AppointmentDocument: uses scheduled_at, appointment_id)
# ---------------------------------------------------------------------------

APPOINTMENTS = [
    # PAT001 — completed annual checkup 30 days ago
    {
        "_id": "APT001",
        "patient_id": "PAT001",
        "appointment_id": "APT001",
        "provider_id": "PROV001",
        "scheduled_at": dt(-30),
        "status": "completed",
        "reason": "Annual Checkup",
        "notes": "Patient reported fatigue. Labs ordered.",
        "is_deleted": False,
        "created_at": dt(-40),
        "updated_at": dt(-30),
    },
    # PAT001 — upcoming follow-up in 15 days
    {
        "_id": "APT002",
        "patient_id": "PAT001",
        "appointment_id": "APT002",
        "provider_id": "PROV001",
        "scheduled_at": dt(15),
        "status": "scheduled",
        "reason": "Follow-up: Lab Results & Claim Appeal",
        "notes": None,
        "is_deleted": False,
        "created_at": dt(-5),
        "updated_at": dt(-5),
    },
    # PAT001 — cancelled appointment last week
    {
        "_id": "APT003",
        "patient_id": "PAT001",
        "appointment_id": "APT003",
        "provider_id": "PROV002",
        "scheduled_at": dt(-7),
        "status": "cancelled",
        "reason": "Specialist Referral",
        "notes": "Patient cancelled due to scheduling conflict.",
        "is_deleted": False,
        "created_at": dt(-20),
        "updated_at": dt(-7),
    },
    # PAT002 — completed cardiology consult
    {
        "_id": "APT004",
        "patient_id": "PAT002",
        "appointment_id": "APT004",
        "provider_id": "PROV002",
        "scheduled_at": dt(-14),
        "status": "completed",
        "reason": "Cardiology Consultation",
        "notes": "EKG performed. Results normal.",
        "is_deleted": False,
        "created_at": dt(-21),
        "updated_at": dt(-14),
    },
    # PAT002 — upcoming appointment next week
    {
        "_id": "APT005",
        "patient_id": "PAT002",
        "appointment_id": "APT005",
        "provider_id": "PROV001",
        "scheduled_at": dt(7),
        "status": "scheduled",
        "reason": "Routine Check-up",
        "notes": None,
        "is_deleted": False,
        "created_at": dt(-3),
        "updated_at": dt(-3),
    },
]


# ---------------------------------------------------------------------------
# Billing  (match BillingDocument: account_id, amount_due, amount_paid Decimal)
# ---------------------------------------------------------------------------

BILLING = [
    # PAT001 — office visit charge, unpaid (claim denied)
    {
        "_id": "BILL001",
        "patient_id": "PAT001",
        "account_id": "ACC-PAT001-001",
        "amount_due": "150.00",
        "amount_paid": "0.00",
        "currency": "USD",
        "status": "open",
        "due_date": dt(30),
        "is_deleted": False,
        "created_at": dt(-28),
        "updated_at": dt(-20),
    },
    # PAT001 — lab test charge, partially paid (claim approved $80 of $100)
    {
        "_id": "BILL002",
        "patient_id": "PAT001",
        "account_id": "ACC-PAT001-002",
        "amount_due": "100.00",
        "amount_paid": "80.00",          # insurance paid $80
        "currency": "USD",
        "status": "partial",
        "due_date": dt(30),
        "is_deleted": False,
        "created_at": dt(-28),
        "updated_at": dt(-22),
    },
    # PAT002 — cardiology consult, fully paid
    {
        "_id": "BILL003",
        "patient_id": "PAT002",
        "account_id": "ACC-PAT002-001",
        "amount_due": "300.00",
        "amount_paid": "300.00",
        "currency": "USD",
        "status": "paid",
        "due_date": dt(-5),
        "is_deleted": False,
        "created_at": dt(-14),
        "updated_at": dt(-5),
    },
    # PAT002 — EKG charge, overdue
    {
        "_id": "BILL004",
        "patient_id": "PAT002",
        "account_id": "ACC-PAT002-002",
        "amount_due": "75.00",
        "amount_paid": "0.00",
        "currency": "USD",
        "status": "overdue",
        "due_date": dt(-10),
        "is_deleted": False,
        "created_at": dt(-14),
        "updated_at": dt(-10),
    },
]


# ---------------------------------------------------------------------------
# Insurance  (match InsuranceDocument: plan_id, payer_name, member_id)
# ---------------------------------------------------------------------------

INSURANCE = [
    {
        "_id": "INS001",
        "patient_id": "PAT001",
        "plan_id": "PLAN-BCBS-GOLD",
        "payer_name": "Blue Cross Blue Shield",
        "member_id": "BCBS-MEM-001",
        "status": "active",
        "coverage_start": "2026-01-01",
        "coverage_end": "2026-12-31",
        "provider_name": "Blue Cross Blue Shield",
        "plan_name": "Premium Gold PPO",
        "is_deleted": False,
        "created_at": dt(-180),
        "updated_at": dt(-180),
    },
    {
        "_id": "INS002",
        "patient_id": "PAT002",
        "plan_id": "PLAN-AETNA-SILVER",
        "payer_name": "Aetna",
        "member_id": "AET-MEM-002",
        "status": "active",
        "coverage_start": "2026-01-01",
        "coverage_end": "2026-12-31",
        "provider_name": "Aetna",
        "plan_name": "Silver HMO",
        "is_deleted": False,
        "created_at": dt(-180),
        "updated_at": dt(-180),
    },
]

# Claims  (match ClaimDocument: insurance_id, claim_amount float, ClaimStatus)
CLAIMS = [
    # PAT001 — office visit claim DENIED (missing prior auth)
    {
        "_id": "CLM001",
        "patient_id": "PAT001",
        "insurance_id": "INS001",
        "claim_number": "CLM-2026-001",
        "claim_amount": 150.00,
        "approved_amount": None,
        "status": "denied",
        "denial_reason": "Prior authorization not obtained before service",
        "submitted_at": dt(-25),
        "processed_at": dt(-20),
        "is_deleted": False,
        "created_at": dt(-25),
        "updated_at": dt(-20),
    },
    # PAT001 — lab claim APPROVED (partial)
    {
        "_id": "CLM002",
        "patient_id": "PAT001",
        "insurance_id": "INS001",
        "claim_number": "CLM-2026-002",
        "claim_amount": 100.00,
        "approved_amount": 80.00,
        "status": "approved",
        "denial_reason": None,
        "submitted_at": dt(-27),
        "processed_at": dt(-22),
        "is_deleted": False,
        "created_at": dt(-27),
        "updated_at": dt(-22),
    },
    # PAT002 — cardiology claim APPROVED and PAID
    {
        "_id": "CLM003",
        "patient_id": "PAT002",
        "insurance_id": "INS002",
        "claim_number": "CLM-2026-003",
        "claim_amount": 300.00,
        "approved_amount": 300.00,
        "status": "approved",
        "denial_reason": None,
        "submitted_at": dt(-13),
        "processed_at": dt(-5),
        "is_deleted": False,
        "created_at": dt(-13),
        "updated_at": dt(-5),
    },
    # PAT002 — EKG claim PENDING
    {
        "_id": "CLM004",
        "patient_id": "PAT002",
        "insurance_id": "INS002",
        "claim_number": "CLM-2026-004",
        "claim_amount": 75.00,
        "approved_amount": None,
        "status": "pending",
        "denial_reason": None,
        "submitted_at": dt(-13),
        "processed_at": None,
        "is_deleted": False,
        "created_at": dt(-13),
        "updated_at": dt(-13),
    },
]


# ---------------------------------------------------------------------------
# Cases  (match CaseDocument: case_id, title, CaseStatus, opened_at)
# ---------------------------------------------------------------------------

CASES = [
    # PAT001 — open case: denied claim appeal
    {
        "_id": "CASE001",
        "patient_id": "PAT001",
        "case_id": "CASE001",
        "title": "Claim CLM-2026-001 Denial Appeal",
        "status": "open",
        "assigned_provider_id": "PROV001",
        "opened_at": dt(-18),
        "closed_at": None,
        "is_deleted": False,
        "created_at": dt(-18),
        "updated_at": dt(-5),
    },
    # PAT001 — closed case: lab result review
    {
        "_id": "CASE002",
        "patient_id": "PAT001",
        "case_id": "CASE002",
        "title": "Lab Results Review — CBC Panel",
        "status": "closed",
        "assigned_provider_id": "PROV001",
        "opened_at": dt(-28),
        "closed_at": dt(-15),
        "is_deleted": False,
        "created_at": dt(-28),
        "updated_at": dt(-15),
    },
    # PAT002 — in-review cardiology case
    {
        "_id": "CASE003",
        "patient_id": "PAT002",
        "case_id": "CASE003",
        "title": "Cardiology Follow-up & EKG Pending Claim",
        "status": "in_review",
        "assigned_provider_id": "PROV002",
        "opened_at": dt(-14),
        "closed_at": None,
        "is_deleted": False,
        "created_at": dt(-14),
        "updated_at": dt(-3),
    },
]


# ---------------------------------------------------------------------------
# Events  (match EventDocument schema exactly — uses entity_type Literal)
# ---------------------------------------------------------------------------

def _ev(eid, patient_id, entity_type, entity_id, event_type,
        days_offset, actor_type="system", actor_id="SYSTEM", **meta):
    t = dt(days_offset)
    return {
        "_id": eid,
        "event_id": eid,
        "patient_id": patient_id,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "event_type": event_type,
        "event_time": t,
        "actor_type": actor_type,
        "actor_id": actor_id,
        "metadata": meta,
        "is_deleted": False,
        "created_at": t,
        "updated_at": t,
    }


EVENTS = [
    # ── PAT001 timeline ─────────────────────────────────────────────────────
    _ev("EVT001", "PAT001", "appointment", "APT001",
        EventTypes.APPOINTMENT_CREATED, -40,
        actor_type="patient", actor_id="PAT001",
        reason="Annual Checkup"),

    _ev("EVT002", "PAT001", "appointment", "APT001",
        EventTypes.APPOINTMENT_COMPLETED, -30,
        actor_type="provider", actor_id="PROV001",
        notes="Labs ordered due to reported fatigue"),

    _ev("EVT003", "PAT001", "lab", "LAB001",
        EventTypes.LAB_ORDERED, -30,
        actor_type="provider", actor_id="PROV001",
        lab_name="CBC Complete Panel", reason="Fatigue workup"),

    _ev("EVT004", "PAT001", "lab", "LAB001",
        EventTypes.LAB_COMPLETED, -28,
        lab_name="CBC Complete Panel",
        result_summary="Mild anemia noted"),

    _ev("EVT005", "PAT001", "billing", "BILL001",
        EventTypes.CHARGE_ADDED, -28,
        description="Office Visit — Annual Checkup", amount=150.00,
        procedure_code="99213"),

    _ev("EVT006", "PAT001", "billing", "BILL002",
        EventTypes.CHARGE_ADDED, -28,
        description="Laboratory Test — CBC Panel", amount=100.00,
        procedure_code="85025"),

    _ev("EVT007", "PAT001", "case", "CASE002",
        EventTypes.CASE_OPENED, -28,
        actor_type="provider", actor_id="PROV001",
        title="Lab Results Review — CBC Panel"),

    _ev("EVT008", "PAT001", "claim", "CLM002",
        EventTypes.CLAIM_SUBMITTED, -27,
        claim_amount=100.00, description="Lab Test Claim"),

    _ev("EVT009", "PAT001", "claim", "CLM001",
        EventTypes.CLAIM_SUBMITTED, -25,
        claim_amount=150.00, description="Office Visit Claim"),

    _ev("EVT010", "PAT001", "claim", "CLM002",
        EventTypes.CLAIM_APPROVED, -22,
        actor_type="insurance", actor_id="INS001",
        approved_amount=80.00, original_amount=100.00,
        note="Partial approval — deductible applied"),

    _ev("EVT011", "PAT001", "billing", "BILL002",
        EventTypes.PAYMENT_RECEIVED, -22,
        amount=80.00, payer="Blue Cross Blue Shield",
        payment_type="insurance_payment"),

    _ev("EVT012", "PAT001", "claim", "CLM001",
        EventTypes.CLAIM_DENIED, -20,
        actor_type="insurance", actor_id="INS001",
        reason="Prior authorization not obtained before service",
        claim_amount=150.00,
        denial_code="AUTH001"),

    _ev("EVT013", "PAT001", "case", "CASE002",
        EventTypes.CASE_CLOSED, -15,
        actor_type="provider", actor_id="PROV001",
        resolution="Lab results reviewed with patient"),

    _ev("EVT014", "PAT001", "case", "CASE001",
        EventTypes.CASE_OPENED, -18,
        actor_type="staff", actor_id="STAFF001",
        title="Claim CLM-2026-001 Denial Appeal",
        reason="Patient disputing denied office visit claim"),

    _ev("EVT015", "PAT001", "appointment", "APT003",
        EventTypes.APPOINTMENT_CANCELLED, -7,
        actor_type="patient", actor_id="PAT001",
        reason="Scheduling conflict"),

    _ev("EVT016", "PAT001", "appointment", "APT002",
        EventTypes.APPOINTMENT_CREATED, -5,
        actor_type="staff", actor_id="STAFF001",
        reason="Follow-up: Lab Results & Claim Appeal"),

    # ── PAT002 timeline ─────────────────────────────────────────────────────
    _ev("EVT017", "PAT002", "appointment", "APT004",
        EventTypes.APPOINTMENT_CREATED, -21,
        actor_type="patient", actor_id="PAT002",
        reason="Cardiology Consultation"),

    _ev("EVT018", "PAT002", "appointment", "APT004",
        EventTypes.APPOINTMENT_COMPLETED, -14,
        actor_type="provider", actor_id="PROV002",
        notes="EKG performed. Results normal."),

    _ev("EVT019", "PAT002", "procedure", "PROC001",
        EventTypes.PROCEDURE_COMPLETED, -14,
        actor_type="provider", actor_id="PROV002",
        procedure="EKG", result="Normal sinus rhythm"),

    _ev("EVT020", "PAT002", "billing", "BILL003",
        EventTypes.CHARGE_ADDED, -14,
        description="Cardiology Consultation", amount=300.00,
        procedure_code="99244"),

    _ev("EVT021", "PAT002", "billing", "BILL004",
        EventTypes.CHARGE_ADDED, -14,
        description="EKG — 12-Lead", amount=75.00,
        procedure_code="93000"),

    _ev("EVT022", "PAT002", "case", "CASE003",
        EventTypes.CASE_OPENED, -14,
        actor_type="provider", actor_id="PROV002",
        title="Cardiology Follow-up & EKG Pending Claim"),

    _ev("EVT023", "PAT002", "claim", "CLM003",
        EventTypes.CLAIM_SUBMITTED, -13,
        claim_amount=300.00, description="Cardiology Consult Claim"),

    _ev("EVT024", "PAT002", "claim", "CLM004",
        EventTypes.CLAIM_SUBMITTED, -13,
        claim_amount=75.00, description="EKG Claim"),

    _ev("EVT025", "PAT002", "claim", "CLM003",
        EventTypes.CLAIM_APPROVED, -5,
        actor_type="insurance", actor_id="INS002",
        approved_amount=300.00),

    _ev("EVT026", "PAT002", "billing", "BILL003",
        EventTypes.PAYMENT_RECEIVED, -5,
        amount=300.00, payer="Aetna",
        payment_type="insurance_payment"),

    _ev("EVT027", "PAT002", "appointment", "APT005",
        EventTypes.APPOINTMENT_CREATED, -3,
        actor_type="patient", actor_id="PAT002",
        reason="Routine Check-up"),
]


# ---------------------------------------------------------------------------
# Seeding functions
# ---------------------------------------------------------------------------

ALL_COLLECTIONS = ["patients", "appointments", "billing", "insurance", "claims",
                   "cases", "events", "audit_logs"]


async def seed(db, reset: bool = False) -> dict[str, int]:
    """
    Insert all seed data.  If reset=True, wipe collections first.
    Returns a dict of {collection: count_written}.
    """
    if reset:
        print("  Dropping existing data...")
        await drop_collections(db, ALL_COLLECTIONS)

    counts = {}

    datasets = [
        ("patients",     PATIENTS),
        ("appointments", APPOINTMENTS),
        ("billing",      BILLING),
        ("insurance",    INSURANCE),
        ("claims",       CLAIMS),
        ("cases",        CASES),
        ("events",       EVENTS),
    ]

    for collection_name, docs in datasets:
        n = await upsert_many(db[collection_name], docs)
        counts[collection_name] = len(docs)
        print(f"  ✓ {collection_name:<14} {len(docs):>3} docs  ({n} changed)")

    return counts


async def main():
    parser = argparse.ArgumentParser(description="Seed PatientCare sample data")
    parser.add_argument("--reset",   action="store_true",
                        help="Drop all collections before seeding")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print counts without touching the database")
    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("  PatientCare Platform — Sample Data Seeder")
    print("=" * 60)

    if args.dry_run:
        print("\n[DRY RUN] Would insert:")
        for name, docs in [
            ("patients",     PATIENTS),
            ("appointments", APPOINTMENTS),
            ("billing",      BILLING),
            ("insurance",    INSURANCE),
            ("claims",       CLAIMS),
            ("cases",        CASES),
            ("events",       EVENTS),
        ]:
            print(f"  {name:<14} {len(docs):>3} docs")
        print("\nTotal:", sum(len(d) for d in
              [PATIENTS, APPOINTMENTS, BILLING, INSURANCE, CLAIMS, CASES, EVENTS]),
              "documents\n")
        return

    await init_mongo()
    db = await get_database()

    try:
        print(f"\n  Mode: {'RESET + seed' if args.reset else 'upsert (safe)'}\n")
        counts = await seed(db, reset=args.reset)

        total = sum(counts.values())
        print(f"\n{'=' * 60}")
        print(f"  ✅  Done — {total} documents across {len(counts)} collections")
        print(f"{'=' * 60}")
        print("""
Test patients:
  PAT001  John Doe    — consent granted | denied claim | open appeal case
  PAT002  Jane Smith  — consent granted | paid claim   | pending EKG claim
  PAT003  Carlos Rivera — consent REVOKED (tests auth-denied path)

Sample queries to try via POST /chat:
  patient_id = PAT001
  • "When is my next appointment?"
  • "What is my current balance?"
  • "Why was my claim denied?"
  • "Give me a full case summary"
  • "What happened in the last 30 days?"
""")
    except Exception as exc:
        print(f"\n❌  Seeding failed: {exc}")
        raise
    finally:
        await close_mongo()


if __name__ == "__main__":
    asyncio.run(main())
