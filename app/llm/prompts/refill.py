"""Refill Agent Prompt"""

REFILL_SYSTEM_PROMPT = """
You are a Healthcare Prescription Refill Tracking Agent.

Your objective is to provide clear, accurate information about prescription refill status.

RESPONSIBILITIES:
- Report current refill status for active medications
- List any pending refill requests
- Summarize recent refill history
- Direct patients to contact their provider for clinical questions

STRICT RULES — YOU MUST FOLLOW:
- Do NOT provide medication advice, dosage recommendations, or drug interactions
- Do NOT suggest whether a patient should or should not take a medication
- Do NOT make clinical assessments or recommendations
- ALWAYS direct clinical questions to a licensed healthcare provider
- Use ONLY the provided refill data — never invent prescriptions or statuses

OUTPUT FORMAT (return JSON only):
{
    "summary": "brief plain-language summary of refill status",
    "pending_refills": ["list of pending refill descriptions if any"],
    "active_medications_count": 0,
    "response": "patient-friendly message about their refill status"
}
"""


def get_refill_prompt(
    message: str,
    refill_status: dict,
    medications: list,
    history: list,
) -> str:
    """Generate a refill tracking prompt for the LLM."""

    status_text = "REFILL STATUS:\n"
    status_text += f"  Status: {refill_status.get('status', 'unknown')}\n"

    pending = refill_status.get("pending_refills", [])
    if pending:
        status_text += "\nPENDING REFILLS:\n"
        for r in pending:
            status_text += f"  - {r}\n"
    else:
        status_text += "  No pending refills.\n"

    meds_text = ""
    if medications:
        meds_text = "\nACTIVE MEDICATIONS:\n"
        for med in medications[:10]:
            if isinstance(med, dict):
                name = med.get("name", "Unknown")
                meds_text += f"  - {name}\n"
            else:
                meds_text += f"  - {med}\n"
    else:
        meds_text = "\nNo active medications on record.\n"

    history_text = ""
    if history:
        history_text = "\nRECENT REFILL HISTORY:\n"
        for entry in history[:5]:
            if isinstance(entry, dict):
                med = entry.get("medication", "Unknown")
                status = entry.get("status", "unknown")
                date = entry.get("requested_at", "")
                history_text += f"  - {med}: {status}"
                if date:
                    history_text += f" ({date})"
                history_text += "\n"

    prompt = f"""
PATIENT QUESTION: "{message}"

{status_text}
{meds_text}
{history_text}

Summarize the patient's refill status based on the data above.
For any clinical or dosage questions, instruct the patient to contact their healthcare provider.

Return JSON only.
"""
    return prompt
