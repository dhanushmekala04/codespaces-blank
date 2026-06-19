"""Case Agent Prompt - Patient 360 Summary"""

CASE_SYSTEM_PROMPT = """
You are a Patient Case Analysis Agent specializing in Patient 360 operational summaries.

Your objective is to build a comprehensive understanding of the patient's current healthcare status.

METHODOLOGY:
1. Review all available data sources
2. Identify active items and pending tasks
3. Summarize recent activity
4. Highlight important items requiring attention

DATA SOURCES:
- Appointments (scheduled and past)
- Claims (active and processed)
- Billing (charges and payments)
- Events (timeline of activities)
- Refills (prescription status)

RULES:
- Use ONLY operational information provided
- Do NOT provide medical diagnoses
- Do NOT recommend treatments
- Focus on administrative and operational status
- Be comprehensive yet concise

OUTPUT FORMAT:
{
    "case_summary": "overall patient operational status",
    "active_items": ["list", "of", "active", "matters"],
    "pending_items": ["list", "of", "pending", "tasks"],
    "recent_events": ["recent", "activity", "summary"],
    "response": "patient-friendly comprehensive summary"
}
"""


def get_case_analysis_prompt(
    message: str,
    appointments: list[dict] | None,
    claims: list[dict] | None,
    billing: dict | None,
    events: list[dict] | None,
) -> str:
    """Generate Patient 360 case analysis prompt."""
    
    data_text = "PATIENT 360 DATA:\n"
    
    # Appointments
    data_text += "\n=== APPOINTMENTS ===\n"
    if appointments:
        for apt in appointments[:5]:
            # Use scheduled_at (DB field name)
            date = apt.get("scheduled_at") or apt.get("appointment_date", "unknown")
            status = apt.get("status", "unknown")
            reason = apt.get("reason", "")
            data_text += f"- {status.upper()}: {date}"
            if reason:
                data_text += f" - {reason}"
            data_text += "\n"
    else:
        data_text += "No appointments\n"
    
    # Claims
    data_text += "\n=== CLAIMS ===\n"
    if claims:
        for claim in claims:
            claim_id = claim.get("_id", "unknown")
            status = claim.get("status", "unknown")
            amount = claim.get("claim_amount", 0)
            data_text += f"- Claim {claim_id}: {status.upper()} (${amount:.2f})\n"
    else:
        data_text += "No claims\n"
    
    # Billing
    data_text += "\n=== BILLING ===\n"
    if billing:
        balance = billing.get("total_balance", 0)
        data_text += f"Current Balance: ${balance:.2f}\n"
        charges = billing.get("charges", [])
        if charges:
            data_text += f"Recent Charges: {len(charges)} items\n"
    else:
        data_text += "No billing information\n"
    
    # Events
    data_text += "\n=== RECENT ACTIVITY ===\n"
    if events:
        for event in events[:10]:
            event_type = event.get("event_type", "unknown")
            event_time = event.get("event_time", "")
            data_text += f"- {event_type} ({event_time})\n"
    else:
        data_text += "No recent events\n"
    
    prompt = f"""
PATIENT QUESTION: "{message}"

{data_text}

Build a comprehensive Patient 360 operational summary.
Identify:
1. Active items (upcoming appointments, open claims, outstanding balance)
2. Pending items (items requiring attention)
3. Recent activity summary

Provide a clear, comprehensive response that gives the patient a complete picture of their healthcare status.

Return JSON only.
"""
    
    return prompt
