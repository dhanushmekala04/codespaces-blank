"""
Seed Pinecone with healthcare knowledge documents.

Namespaces (per PINECONE_STRATEGY.md):
    clinic_policies       — clinic rules, hours, procedures
    insurance_policies    — coverage, prior-auth, appeals
    faq                   — common patient questions
    patient_education     — condition info, medications
    provider_guidelines   — clinical SOPs
    consent_documents     — consent forms / HIPAA notices

Usage:
    python -m scripts.seed_pinecone               # upsert (safe, skip existing)
    python -m scripts.seed_pinecone --reset       # delete namespace vectors first
    python -m scripts.seed_pinecone --dry-run     # print docs, no API calls
"""

import argparse
import asyncio
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings

# ---------------------------------------------------------------------------
# Knowledge documents
# Each doc: id, namespace, title, text, metadata
# ---------------------------------------------------------------------------

DOCS = [
    # ── clinic_policies ─────────────────────────────────────────────────────
    {
        "id": "CP001",
        "namespace": "clinic_policies",
        "title": "Appointment Cancellation Policy",
        "text": (
            "Patients must cancel appointments at least 24 hours in advance. "
            "Late cancellations or no-shows may incur a $50 fee. "
            "To cancel, call the clinic or use the patient portal. "
            "Repeat no-shows (3 or more) may result in discharge from the practice."
        ),
        "category": "clinic_policies",
    },
    {
        "id": "CP002",
        "namespace": "clinic_policies",
        "title": "Clinic Hours and Contact",
        "text": (
            "The clinic is open Monday to Friday, 8 AM to 6 PM. "
            "Saturday hours are 9 AM to 1 PM. The clinic is closed on Sundays and public holidays. "
            "For urgent after-hours care, call the nurse line at 1-800-NURSE-24. "
            "Emergency services should be accessed via 911 or the nearest ER."
        ),
        "category": "clinic_policies",
    },
    {
        "id": "CP003",
        "namespace": "clinic_policies",
        "title": "Referral and Prior Authorization Policy",
        "text": (
            "Referrals to specialists require a written order from your primary care provider. "
            "Prior authorization must be obtained before certain procedures, imaging (CT, MRI), "
            "and specialist visits. Failure to obtain prior authorization may result in claim denial. "
            "Allow 3-5 business days for prior authorization processing. "
            "Urgent authorizations can be processed within 24 hours with physician justification."
        ),
        "category": "clinic_policies",
    },
    {
        "id": "CP004",
        "namespace": "clinic_policies",
        "title": "Prescription Refill Policy",
        "text": (
            "Prescription refills require an up-to-date visit within the past 12 months. "
            "Refill requests should be submitted 5-7 days before medication runs out. "
            "Controlled substances require an in-person visit and cannot be refilled via phone. "
            "Refill requests can be submitted via the patient portal or by calling the clinic."
        ),
        "category": "clinic_policies",
    },

    # ── insurance_policies ──────────────────────────────────────────────────
    {
        "id": "INS001",
        "namespace": "insurance_policies",
        "title": "Prior Authorization Requirements",
        "text": (
            "Prior authorization is required for: MRI, CT scans, PET scans, specialist referrals, "
            "elective surgery, durable medical equipment, home health services, and certain medications. "
            "Procedures performed without prior authorization will likely be denied. "
            "To appeal a denial due to missing prior auth, submit a retrospective authorization "
            "request with clinical justification within 30 days of the denial."
        ),
        "category": "insurance_policies",
    },
    {
        "id": "INS002",
        "namespace": "insurance_policies",
        "title": "Claim Denial and Appeals Process",
        "text": (
            "If your insurance claim is denied, you have the right to appeal. "
            "Step 1: Request the denial reason in writing from your insurer. "
            "Step 2: Gather supporting documentation (medical records, physician letters). "
            "Step 3: Submit a formal appeal within 60 days of the denial notice. "
            "Step 4: If the internal appeal is denied, you may request an external review. "
            "Common denial reasons: prior auth not obtained, out-of-network provider, "
            "service not covered, duplicate claim, coding errors."
        ),
        "category": "insurance_policies",
    },
    {
        "id": "INS003",
        "namespace": "insurance_policies",
        "title": "Coverage: Preventive Care",
        "text": (
            "Most insurance plans cover 100% of preventive care at no cost to the patient "
            "when seen by an in-network provider. Covered preventive services include: "
            "annual wellness exams, immunizations, cancer screenings (mammogram, colonoscopy), "
            "blood pressure and cholesterol checks, diabetes screening, and depression screening. "
            "Note: If a preventive visit also addresses a medical problem, you may be billed "
            "for the additional services."
        ),
        "category": "insurance_policies",
    },
    {
        "id": "INS004",
        "namespace": "insurance_policies",
        "title": "Deductible, Copay, and Out-of-Pocket Maximum",
        "text": (
            "Deductible: The amount you pay before insurance begins covering costs. "
            "Copay: A fixed fee paid at each visit (e.g., $20 for primary care, $50 for specialist). "
            "Coinsurance: Your share of costs after deductible (e.g., 20% of the bill). "
            "Out-of-Pocket Maximum: The most you will pay in a year; after this, insurance covers 100%. "
            "In-network providers have lower cost-sharing than out-of-network providers."
        ),
        "category": "insurance_policies",
    },

    # ── faq ─────────────────────────────────────────────────────────────────
    {
        "id": "FAQ001",
        "namespace": "faq",
        "title": "How do I schedule an appointment?",
        "text": (
            "You can schedule an appointment through the patient portal, by calling the clinic, "
            "or by visiting in person. Online booking is available 24/7 via the portal. "
            "Same-day appointments may be available for urgent needs — call the clinic directly. "
            "Telehealth (video) appointments are available for follow-ups and minor concerns."
        ),
        "category": "faq",
    },
    {
        "id": "FAQ002",
        "namespace": "faq",
        "title": "How do I get my lab results?",
        "text": (
            "Lab results are typically available within 2-5 business days. "
            "You will be notified via the patient portal once results are ready. "
            "Your provider will contact you directly if any results require immediate attention. "
            "You can also call the clinic to request your results after 5 business days."
        ),
        "category": "faq",
    },
    {
        "id": "FAQ003",
        "namespace": "faq",
        "title": "Why was my insurance claim denied?",
        "text": (
            "Common reasons for claim denial include: "
            "1. Prior authorization was not obtained before the service. "
            "2. The service is not covered under your plan. "
            "3. The provider is out-of-network. "
            "4. Incorrect billing codes were used. "
            "5. The claim was submitted after the filing deadline. "
            "Contact your insurance company for the specific denial reason, "
            "then speak with your provider's billing office to determine next steps or file an appeal."
        ),
        "category": "faq",
    },
    {
        "id": "FAQ004",
        "namespace": "faq",
        "title": "How do I request a prescription refill?",
        "text": (
            "To request a refill: use the patient portal, call the pharmacy (they can request on your behalf), "
            "or call the clinic directly. Allow 2-3 business days for processing. "
            "If you are running low on a controlled substance, an in-person visit is required. "
            "Make sure your annual wellness visit is up to date or the refill may be denied."
        ),
        "category": "faq",
    },
    {
        "id": "FAQ005",
        "namespace": "faq",
        "title": "How do I pay my medical bill?",
        "text": (
            "Bills can be paid online via the patient portal, by phone, by mail, or in person. "
            "We accept credit/debit cards, checks, and electronic bank transfer. "
            "Payment plans are available for balances over $200 — ask billing to set one up. "
            "Financial assistance programs are available for qualifying patients — contact billing for details."
        ),
        "category": "faq",
    },

    # ── patient_education ───────────────────────────────────────────────────
    {
        "id": "PE001",
        "namespace": "patient_education",
        "title": "Understanding Anemia",
        "text": (
            "Anemia occurs when you have fewer red blood cells than normal or low hemoglobin levels. "
            "Common symptoms include fatigue, weakness, pale skin, shortness of breath, and dizziness. "
            "The most common type is iron-deficiency anemia, often caused by low dietary iron or blood loss. "
            "Treatment depends on the cause: iron supplements, dietary changes, B12 injections, or treating underlying conditions. "
            "A CBC (Complete Blood Count) blood test is used to diagnose anemia."
        ),
        "category": "patient_education",
    },
    {
        "id": "PE002",
        "namespace": "patient_education",
        "title": "What is an EKG (Electrocardiogram)?",
        "text": (
            "An EKG (also called an ECG) measures the electrical activity of your heart. "
            "It is a painless, non-invasive test that takes about 10 minutes. "
            "EKGs are used to detect arrhythmias, heart attacks, enlarged heart, and other conditions. "
            "Normal sinus rhythm means your heart is beating in a normal, regular pattern. "
            "Your doctor will review the results and discuss any findings with you."
        ),
        "category": "patient_education",
    },
    {
        "id": "PE003",
        "namespace": "patient_education",
        "title": "Managing High Blood Pressure",
        "text": (
            "High blood pressure (hypertension) is when blood pressure consistently reads above 130/80 mmHg. "
            "Lifestyle changes: reduce sodium intake, exercise regularly, maintain healthy weight, limit alcohol, quit smoking. "
            "Medications such as ACE inhibitors, beta blockers, and diuretics may be prescribed. "
            "Monitor blood pressure at home and keep a log to share with your provider. "
            "Uncontrolled hypertension increases risk of heart attack, stroke, and kidney disease."
        ),
        "category": "patient_education",
    },

    # ── provider_guidelines ─────────────────────────────────────────────────
    {
        "id": "PG001",
        "namespace": "provider_guidelines",
        "title": "Prior Authorization SOP",
        "text": (
            "Before ordering any procedure requiring prior auth: "
            "1. Verify coverage with the patient's insurer via phone or portal. "
            "2. Submit prior auth request with diagnosis codes, procedure codes, and clinical justification. "
            "3. Document the auth number in the patient chart. "
            "4. Inform the patient that the service cannot proceed until auth is approved. "
            "5. If urgent, request expedited review with written physician attestation. "
            "Failure to follow this SOP may result in claim denial and patient financial liability."
        ),
        "category": "provider_guidelines",
    },
    {
        "id": "PG002",
        "namespace": "provider_guidelines",
        "title": "Lab Ordering Guidelines",
        "text": (
            "Order labs only when clinically indicated. Document the reason in the chart. "
            "Standard panels: CBC (fatigue, infection workup), CMP (metabolic, kidney, liver), "
            "Lipid panel (cardiovascular risk), HbA1c (diabetes monitoring), TSH (thyroid). "
            "Critical values must be called to the ordering provider within 1 hour. "
            "Notify patients of all results within 5 business days, sooner if abnormal."
        ),
        "category": "provider_guidelines",
    },

    # ── consent_documents ───────────────────────────────────────────────────
    {
        "id": "CD001",
        "namespace": "consent_documents",
        "title": "HIPAA Notice of Privacy Practices",
        "text": (
            "Your health information is protected under HIPAA (Health Insurance Portability and Accountability Act). "
            "We may use and share your information for treatment, payment, and healthcare operations. "
            "We will not share your information for marketing without your written consent. "
            "You have the right to access your records, request corrections, and receive an accounting of disclosures. "
            "To file a privacy complaint, contact the clinic privacy officer or the HHS Office for Civil Rights."
        ),
        "category": "consent_documents",
    },
    {
        "id": "CD002",
        "namespace": "consent_documents",
        "title": "Patient Consent for Treatment",
        "text": (
            "By consenting to treatment, you agree to allow the clinic's healthcare providers "
            "to perform examinations, diagnostic tests, and treatments deemed necessary for your care. "
            "You have the right to refuse any treatment and to ask questions before any procedure. "
            "You may withdraw consent at any time. Consent does not cover experimental procedures "
            "or major surgery, which require separate specific informed consent."
        ),
        "category": "consent_documents",
    },
]


# ---------------------------------------------------------------------------
# Embedding using NVIDIA NIM (via shared wrapper)
# ---------------------------------------------------------------------------

def get_embeddings(texts: list[str]) -> list[list[float]]:
    """Embed texts using NVIDIA NIM via the shared LLM wrapper."""
    from app.llm.wrapper import get_embeddings as _get_embeddings
    embedder = _get_embeddings()
    return embedder.embed_documents(texts)


# ---------------------------------------------------------------------------
# Pinecone helpers
# ---------------------------------------------------------------------------

def get_or_create_index(pc, index_name: str, dimension: int = 1024):
    """Create index if it doesn't exist, then return it."""
    existing = [idx.name for idx in pc.list_indexes()]
    if index_name not in existing:
        print(f"  Creating Pinecone index '{index_name}' (dim={dimension}, cosine)...")
        from pinecone import ServerlessSpec
        pc.create_index(
            name=index_name,
            dimension=dimension,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
        # Wait for index to be ready
        for _ in range(30):
            desc = pc.describe_index(index_name)
            if desc.status.get("ready", False):
                break
            print("  Waiting for index to be ready...")
            time.sleep(5)
    else:
        print(f"  Index '{index_name}' already exists.")
    return pc.Index(index_name)


def delete_namespace(index, namespace: str):
    """Delete all vectors in a namespace."""
    try:
        index.delete(delete_all=True, namespace=namespace)
        print(f"  Cleared namespace: {namespace}")
    except Exception as e:
        print(f"  Warning: could not clear namespace '{namespace}': {e}")


def upsert_docs(index, docs: list[dict], embeddings: list[list[float]]):
    """Upsert vectors into Pinecone with metadata."""
    vectors = []
    for doc, emb in zip(docs, embeddings):
        vectors.append({
            "id": doc["id"],
            "values": emb,
            "metadata": {
                "title": doc["title"],
                "text": doc["text"][:500],   # Pinecone metadata 40KB limit — store snippet
                "category": doc["category"],
                "namespace": doc["namespace"],
            },
        })
    # Upsert in batches of 100
    batch_size = 100
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i : i + batch_size]
        index.upsert(vectors=batch, namespace=docs[i]["namespace"])


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Seed Pinecone with healthcare knowledge")
    parser.add_argument("--reset",   action="store_true",
                        help="Delete existing vectors per namespace before upserting")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print docs without making any API calls")
    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("  PatientCare Platform — Pinecone Knowledge Seeder")
    print("=" * 60)

    if args.dry_run:
        print("\n[DRY RUN] Would upsert:")
        from collections import Counter
        ns_counts = Counter(d["namespace"] for d in DOCS)
        for ns, count in sorted(ns_counts.items()):
            print(f"  {ns:<25} {count:>2} docs")
        print(f"\n  Total: {len(DOCS)} documents\n")
        return

    # Validate API key
    if not settings.pinecone_api_key or settings.pinecone_api_key == "your_pinecone_api_key":
        print("\n❌  PINECONE_API_KEY is not set in .env")
        print("    Get your key from https://app.pinecone.io → API Keys")
        print("    Then update PINECONE_API_KEY in your .env file\n")
        sys.exit(1)

    if not settings.nvidia_api_key:
        print("\n❌  NVIDIA_API_KEY is not set in .env\n")
        sys.exit(1)

    from pinecone import Pinecone

    print(f"\n  Index  : {settings.pinecone_index}")
    print(f"  Docs   : {len(DOCS)}")
    print(f"  Mode   : {'RESET + upsert' if args.reset else 'upsert (safe)'}\n")

    # Group docs by namespace for orderly processing
    from collections import defaultdict
    by_namespace: dict[str, list[dict]] = defaultdict(list)
    for doc in DOCS:
        by_namespace[doc["namespace"]].append(doc)

    # Init Pinecone
    pc = Pinecone(api_key=settings.pinecone_api_key)
    index = get_or_create_index(pc, settings.pinecone_index, dimension=1024)

    total_upserted = 0

    for namespace, docs in sorted(by_namespace.items()):
        print(f"\n  Namespace: {namespace} ({len(docs)} docs)")

        if args.reset:
            delete_namespace(index, namespace)

        # Embed
        print(f"    Embedding {len(docs)} documents...")
        texts = [f"{d['title']}\n\n{d['text']}" for d in docs]
        embeddings = get_embeddings(texts)

        # Upsert per namespace (all docs in this loop share same namespace)
        vectors = []
        for doc, emb in zip(docs, embeddings):
            vectors.append({
                "id": doc["id"],
                "values": emb,
                "metadata": {
                    "title": doc["title"],
                    "text": doc["text"][:500],
                    "category": doc["category"],
                    "namespace": namespace,
                },
            })
        index.upsert(vectors=vectors, namespace=namespace)
        print(f"    ✓ Upserted {len(vectors)} vectors → namespace '{namespace}'")
        total_upserted += len(vectors)

    print(f"\n{'=' * 60}")
    print(f"  ✅  Done — {total_upserted} vectors upserted across {len(by_namespace)} namespaces")
    print(f"{'=' * 60}")
    print("""
Namespaces seeded:
  clinic_policies       — cancellation, hours, referrals, refills
  insurance_policies    — prior auth, appeals, coverage, deductibles
  faq                   — appointments, labs, billing, refills
  patient_education     — anemia, EKG, blood pressure
  provider_guidelines   — prior auth SOP, lab ordering
  consent_documents     — HIPAA notice, treatment consent
""")


if __name__ == "__main__":
    main()
