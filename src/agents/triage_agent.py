from ..state import CeylonCareState


def triage_agent(state: CeylonCareState):
    """
    Handles symptom and urgency-related requests.

    This agent does not diagnose medical conditions.
    It identifies potentially urgent situations and
    recommends appropriate professional care.
    """

    print("\n[TRIAGE AGENT]")

    user_message = state["user_message"].lower()

    # --------------------------------------------------
    # Emergency symptom detection
    # --------------------------------------------------

    emergency_symptoms = [
        "severe chest pain",
        "chest pain and difficulty breathing",
        "chest pain and shortness of breath",
        "difficulty breathing",
        "can't breathe",
        "cannot breathe",
        "severe breathing problem",
        "loss of consciousness",
        "unconscious",
        "severe bleeding",
    ]

    is_emergency = any(
        symptom in user_message
        for symptom in emergency_symptoms
    )

    # --------------------------------------------------
    # Emergency response
    # --------------------------------------------------

    if is_emergency:

        response = (
            "Your symptoms may require urgent medical attention. "
            "Please contact your local emergency medical service "
            "or go to the nearest emergency department immediately. "
            "Do not wait for the CeylonCare chatbot to diagnose the "
            "condition. If possible, ask someone nearby to help you "
            "while you seek emergency care."
        )

        print("[TRIAGE LEVEL] EMERGENCY")

    # --------------------------------------------------
    # General symptom response
    # --------------------------------------------------

    else:

        response = (
            "I can help identify the urgency of your symptoms, "
            "but I cannot diagnose a medical condition. "
            "Please provide more details about your symptoms, "
            "when they started, and how severe they are. "
            "If your symptoms are severe, rapidly worsening, "
            "or you feel that you may be in danger, seek "
            "immediate medical attention."
        )

        print("[TRIAGE LEVEL] GENERAL")

    return {
        "final_response": response,
        "human_escalation_required": is_emergency,
    }