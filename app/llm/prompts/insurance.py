"""Insurance Agent Prompt"""

INSURANCE_SYSTEM_PROMPT = """
You are a Healthcare Insurance Specialist Agent.

Your objective is to analyze insurance and claims information.

RESPONSIBILITIES:
- Explain claim status
- Provide claim history
- Clarify coverage details
- Explain denial reasons

AVAILABLE DATA:
You will receive:
- Insurance plan information
- Claims records
- Claim statuses and reasons

CLAIM STATUSES:
- draft: Claim being prepared
- submitted: Sent to insurance
- processing: Under review
- approved: Claim accepted
- denied: Claim rejected
- paid: Payment issued

RULES:
- Use ONLY provided claim data
- Never guess at coverage
- Explain denial reasons clearly
- Never provide insurance advice
- Be transparent about claim status

OUTPUT FORMAT:
{
    "claim_status": "status of requested claim",
    "denial_reason": "if denied, the reason",
    "claims_summary": "summary of claims",
    "response": "patient-friendly explanation"
}
"""


def get_insurance_prompt(
    message: str,
    insurance_data: dict | None,
    claims_data: list[dict] | None,
) -> str:
    """Generate insurance analysis prompt."""
    
    # Format insurance info
    insurance_text = "INSURANCE INFORMATION:\n"
    
    if insurance_data:
        provider = insurance_data.get("provider_name", "Unknown")
        plan = insurance_data.get("plan_name", "Unknown")
        status = insurance_data.get("status", "unknown")
        
        insurance_text += f"Provider: {provider}\n"
        insurance_text += f"Plan: {plan}\n"
        insurance_text += f"Status: {status}\n"
    else:
        insurance_text += "No insurance information found.\n"
    
    # Format claims
    claims_text = "\nCLAIMS RECORDS:\n"
    
    if claims_data:
        for claim in claims_data:
            claim_id = claim.get("_id", "unknown")
            status = claim.get("status", "unknown")
            amount = claim.get("claim_amount", 0)
            denial_reason = claim.get("denial_reason")
            submitted = claim.get("submitted_at", "")
            
            claims_text += f"\n- Claim {claim_id}:\n"
            claims_text += f"  Status: {status}\n"
            claims_text += f"  Amount: ${amount:.2f}\n"
            if submitted:
                claims_text += f"  Submitted: {submitted}\n"
            if denial_reason:
                claims_text += f"  Denial Reason: {denial_reason}\n"
    else:
        claims_text += "No claims found.\n"
    
    prompt = f"""
PATIENT QUESTION: "{message}"

{insurance_text}
{claims_text}

Analyze the insurance and claims data.
If asking about claim status, provide the current status.
If claim was denied, explain why clearly.

Return JSON only.
"""
    
    return prompt
