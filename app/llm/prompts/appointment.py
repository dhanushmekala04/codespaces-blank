"""Appointment Agent Prompt"""

APPOINTMENT_SYSTEM_PROMPT = """
You are an Appointment Management Agent for a healthcare platform.

Your responsibilities:
- Retrieve appointment information
- Explain appointment details
- Help with scheduling questions
- Provide appointment history

AVAILABLE DATA:
You will receive appointment records for the patient.

RULES:
- Use ONLY the appointment data provided
- Never invent appointment information
- Be clear about appointment dates and times
- Explain appointment status clearly

APPOINTMENT STATUSES:
- scheduled: Future appointment confirmed
- completed: Appointment already happened
- cancelled: Appointment was cancelled
- rescheduled: Appointment was moved
- no_show: Patient didn't attend

OUTPUT FORMAT:
{
    "summary": "brief summary of appointments",
    "upcoming_appointments": [list of future appointments],
    "past_appointments": [list of completed appointments],
    "response": "patient-friendly explanation"
}
"""


def get_appointment_prompt(
    message: str,
    appointments: list[dict],
) -> str:
    """Generate appointment analysis prompt."""

    # Format appointments
    appointments_text = "APPOINTMENT RECORDS:\n"

    if appointments:
        upcoming = []
        past = []

        for apt in appointments:
            # Support both field names: scheduled_at (DB) and appointment_date (legacy)
            scheduled = (
                apt.get("scheduled_at")
                or apt.get("appointment_date")
                or "unknown date"
            )
            status = apt.get("status", "unknown")
            reason = apt.get("reason", "")
            provider = apt.get("provider_id", "")
            apt_id = apt.get("appointment_id") or apt.get("_id", "")

            apt_info = f"- [{status.upper()}] {scheduled}"
            if reason:
                apt_info += f" — {reason}"
            if provider:
                apt_info += f" (Provider: {provider})"
            if apt_id:
                apt_info += f" [ID: {apt_id}]"

            if status in ["scheduled", "confirmed"]:
                upcoming.append(apt_info)
            else:
                past.append(apt_info)

        if upcoming:
            appointments_text += "\nUPCOMING:\n" + "\n".join(upcoming)
        else:
            appointments_text += "\nUPCOMING:\nNo upcoming appointments found.\n"

        if past:
            appointments_text += "\n\nPAST:\n" + "\n".join(past[:5])
    else:
        appointments_text += "No appointments found.\n"
    
    prompt = f"""
PATIENT QUESTION: "{message}"

{appointments_text}

Analyze the appointments and provide a helpful response.
If asking about "next appointment", focus on upcoming scheduled appointments.
If asking about history, mention recent past appointments.

Return JSON only.
"""
    
    return prompt
