"""Verification Agent Prompt"""

VERIFICATION_SYSTEM_PROMPT = """
You are a Verification Agent responsible for validating AI agent outputs.

Your objective is to check for:
1. Hallucinations - statements without evidence
2. Unsupported claims - assertions not backed by data
3. Missing evidence - claims that need citations
4. Contradictions - inconsistent information
5. Invalid references - mentioning data not provided

RULES:
- Review all agent outputs critically
- Flag ANY unsupported statement
- Do NOT let hallucinations pass
- Verify claims against source data
- Be strict but fair

OUTPUT FORMAT:
{
    "status": "PASS" or "FAIL",
    "issues": ["list", "of", "problems", "found"],
    "confidence": 0.0-1.0
}

If all outputs are properly supported by data: PASS
If ANY output makes unsupported claims: FAIL
"""


def get_verification_prompt(
    agent_outputs: dict,
    available_data: dict,
) -> str:
    """Generate verification prompt."""
    
    # Format agent outputs
    outputs_text = "AGENT OUTPUTS TO VERIFY:\n\n"
    for agent_name, output in agent_outputs.items():
        outputs_text += f"=== {agent_name} ===\n"
        if isinstance(output, dict):
            for key, value in output.items():
                outputs_text += f"{key}: {value}\n"
        else:
            outputs_text += f"{output}\n"
        outputs_text += "\n"
    
    # Format available data
    data_text = "AVAILABLE SOURCE DATA:\n\n"
    for source_name, data in available_data.items():
        data_text += f"=== {source_name} ===\n"
        data_text += f"{data}\n\n"
    
    prompt = f"""
{outputs_text}

{data_text}

Verify that ALL agent outputs are supported by the available source data.

Check for:
- Hallucinations (made-up information)
- Unsupported claims
- References to data not provided
- Contradictions between outputs

If everything is properly supported: PASS
If ANY problems found: FAIL with list of issues

Return JSON only.
"""
    
    return prompt
