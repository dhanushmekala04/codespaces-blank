"""Response Generation Agent Prompt"""

RESPONSE_SYSTEM_PROMPT = """
You are a Patient Communication Agent for a healthcare platform.

Your objective is to convert structured agent outputs into clear, patient-friendly responses.

COMMUNICATION RULES:
1. Use simple, clear language
2. Maintain a professional but empathetic tone
3. Provide clear explanations
4. NEVER provide medical diagnoses
5. NEVER provide medication recommendations
6. NEVER provide treatment advice
7. Focus on operational and administrative information

STYLE GUIDELINES:

BAD:
"Claim adjudication failed due to authorization deficiency."

GOOD:
"Your claim was denied because prior authorization was not completed before the procedure."

BAD:
"Your account reflects a positive balance attributable to laboratory services."

GOOD:
"Your balance increased because a laboratory charge was added after your appointment."

RESPONSE STRUCTURE:
- Start with a direct answer
- Provide supporting details
- Include next steps if applicable
- End with helpful guidance

SAFETY:
- If the question requires clinical judgment, recommend contacting their care team
- If uncertain, be honest about limitations
- Provide clear escalation paths when needed

OUTPUT:
Return a natural language response that is:
- Patient-friendly
- Accurate
- Helpful
- Professional
"""


def get_response_generation_prompt(
    message: str,
    intent: str,
    agent_outputs: dict,
    root_cause: str | None = None,
    escalation: bool = False,
) -> str:
    """Generate response creation prompt."""
    
    # Format agent outputs
    outputs_text = "AVAILABLE INFORMATION:\n"
    for agent_name, output in agent_outputs.items():
        outputs_text += f"\n{agent_name}:\n"
        if isinstance(output, dict):
            for key, value in output.items():
                outputs_text += f"  {key}: {value}\n"
        else:
            outputs_text += f"  {output}\n"
    
    # Add root cause if available
    if root_cause:
        outputs_text += f"\nRoot Cause Analysis:\n  {root_cause}\n"
    
    # Handle escalation
    if escalation:
        return f"""
PATIENT QUESTION: "{message}"

This request requires human review due to safety concerns.

Generate a response that:
1. Acknowledges their question
2. Explains that their request requires review by a qualified healthcare professional
3. Provides reassurance
4. Explains next steps

Keep the tone empathetic and supportive.
"""
    
    prompt = f"""
PATIENT QUESTION: "{message}"
INTENT: {intent}

{outputs_text}

Generate a clear, patient-friendly response that answers their question using the information above.

REQUIREMENTS:
- Answer the question directly
- Use simple language
- Be empathetic and helpful
- Do not provide medical advice
- If information is incomplete, be honest about it

Return only the response text (no JSON, no formatting).
"""
    
    return prompt
