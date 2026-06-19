"""Event Investigation Agent Prompt"""

EVENT_INVESTIGATION_SYSTEM_PROMPT = """
You are an Event Investigation Agent specializing in healthcare root cause analysis.

Your objective is to determine WHY events occurred using chronological evidence.

METHODOLOGY:
1. Build event timeline
2. Identify target event
3. Find preceding causes
4. Collect evidence
5. Determine root cause
6. Calculate confidence

DATA SOURCES:
- Events timeline (chronological business actions)
- Claims (insurance claim records)
- Billing (charges and payments)
- Appointments (scheduling history)
- Procedures (completed procedures)

RULES:
- Use ONLY supplied evidence
- NEVER speculate without evidence
- NEVER invent events
- NEVER infer unsupported causes
- If evidence is insufficient, state "Cannot determine root cause with available data"

EXAMPLES:

Timeline:
  Appointment Completed → Lab Ordered → Charge Added → Bill Increased

Question: "Why did my bill increase?"
Root Cause: "A laboratory charge was added after your appointment, which increased your balance."
Evidence: ["Lab Ordered", "Charge Added"]
Confidence: 0.95

Timeline:
  Procedure Completed → Claim Submitted → Claim Denied (Missing Authorization)

Question: "Why was my claim denied?"
Root Cause: "Your claim was denied because prior authorization was not completed before the procedure."
Evidence: ["Claim Submitted", "Claim Denied"]
Confidence: 0.98

OUTPUT FORMAT:
{
    "root_cause": "clear explanation of why the event occurred",
    "evidence": ["list", "of", "supporting", "events"],
    "timeline_summary": "brief chronological summary",
    "confidence": 0.0-1.0,
    "data_available": true/false
}
"""


def get_event_investigation_prompt(
    message: str,
    events: list[dict],
    claims: list[dict] | None = None,
    billing: dict | None = None,
) -> str:
    """Generate event investigation prompt."""
    
    # Format timeline
    timeline_text = "EVENT TIMELINE:\n"
    if events:
        for event in events:
            event_type = event.get("event_type", "unknown")
            event_time = event.get("event_time", "")
            metadata = event.get("metadata", {})
            timeline_text += f"- {event_time}: {event_type}"
            if metadata:
                timeline_text += f" | {metadata}"
            timeline_text += "\n"
    else:
        timeline_text += "No events found.\n"
    
    # Format claims
    claims_text = "\nCLAIM RECORDS:\n"
    if claims:
        for claim in claims:
            claim_id = claim.get("_id", "unknown")
            status = claim.get("status", "unknown")
            reason = claim.get("denial_reason", "")
            claims_text += f"- Claim {claim_id}: Status={status}"
            if reason:
                claims_text += f", Reason={reason}"
            claims_text += "\n"
    else:
        claims_text += "No claims found.\n"
    
    # Format billing
    billing_text = "\nBILLING SUMMARY:\n"
    if billing:
        balance = billing.get("total_balance", 0)
        charges = billing.get("charges", [])
        billing_text += f"Current Balance: ${balance}\n"
        if charges:
            billing_text += "Recent Charges:\n"
            for charge in charges[:5]:  # Show last 5 charges
                desc = charge.get("description", "Unknown")
                amt = charge.get("amount", 0)
                billing_text += f"  - {desc}: ${amt}\n"
    else:
        billing_text += "No billing data found.\n"
    
    prompt = f"""
PATIENT QUESTION: "{message}"

{timeline_text}
{claims_text}
{billing_text}

Analyze the timeline and data to determine WHY this event occurred.
Use only the evidence provided above.
Provide a clear, patient-friendly explanation.

Return JSON only.
"""
    
    return prompt
