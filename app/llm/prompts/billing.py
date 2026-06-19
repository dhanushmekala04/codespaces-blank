"""Billing Agent Prompt"""

BILLING_SYSTEM_PROMPT = """
You are a Healthcare Billing Specialist Agent.

Your objective is to analyze billing information and provide clear explanations.

RESPONSIBILITIES:
- Explain current balance
- List recent charges
- Describe payment history
- Clarify billing items

AVAILABLE DATA:
You will receive billing records including:
- Total balance
- Individual charges
- Payment history

RULES:
- Use ONLY provided billing data
- Never invent charges or payments
- Be transparent about amounts
- Explain charges clearly
- Never provide financial advice

OUTPUT FORMAT:
{
    "balance": 0.0,
    "charges_summary": "brief summary of charges",
    "recent_charges": [list of charge descriptions],
    "response": "patient-friendly explanation"
}
"""


def get_billing_prompt(
    message: str,
    billing_data: dict | None,
) -> str:
    """Generate billing analysis prompt."""
    
    billing_text = "BILLING INFORMATION:\n"
    
    if billing_data:
        balance = billing_data.get("total_balance", 0)
        charges = billing_data.get("charges", [])
        payments = billing_data.get("payments", [])
        
        billing_text += f"\nCurrent Balance: ${balance:.2f}\n"
        
        if charges:
            billing_text += "\nRECENT CHARGES:\n"
            for charge in charges[:10]:  # Show last 10
                desc = charge.get("description", "Unknown")
                amt = charge.get("amount", 0)
                date = charge.get("date", "")
                billing_text += f"- {desc}: ${amt:.2f}"
                if date:
                    billing_text += f" (Date: {date})"
                billing_text += "\n"
        
        if payments:
            billing_text += "\nRECENT PAYMENTS:\n"
            for payment in payments[:5]:  # Show last 5
                amt = payment.get("amount", 0)
                date = payment.get("date", "")
                method = payment.get("method", "")
                billing_text += f"- ${amt:.2f}"
                if date:
                    billing_text += f" on {date}"
                if method:
                    billing_text += f" via {method}"
                billing_text += "\n"
    else:
        billing_text += "No billing information found.\n"
    
    prompt = f"""
PATIENT QUESTION: "{message}"

{billing_text}

Analyze the billing data and provide a clear, helpful response.
If asking about balance, state the current amount.
If asking about charges, explain what they are for.

Return JSON only.
"""
    
    return prompt
