from src.agents.appointment_agent import appointment_agent
from src.services.patient_service import (
    get_patient,
    get_patient_appointments,
)


def main():

    print("\n========================================")
    print("CEYLONCARE PATIENT APPOINTMENT TEST")
    print("========================================")

    patient_id = "P001"

    # --------------------------------------------------
    # Verify synthetic patient exists
    # --------------------------------------------------

    patient = get_patient(patient_id)

    print("\nPATIENT:")
    print(patient)

    if not patient:
        print("ERROR: Patient was not found.")
        return

    # --------------------------------------------------
    # Build appointment state
    # --------------------------------------------------

    state = {
        "user_message": "Yes, confirm the appointment.",
        "patient_id": patient_id,

        "intent": "appointment",
        "selected_agent": "appointment_agent",
        "confidence": 1.0,
        "supervisor_reason": "",
        "final_response": "",

        "appointment_specialist": "cardiologist",
        "appointment_date": "2026-08-25",
        "appointment_time": "10:00 AM",
        "appointment_confirmed": False,
        "appointment_id": "",

        "human_escalation_required": False,
        "human_decision": "",
    }

    # --------------------------------------------------
    # Run Appointment Agent
    # --------------------------------------------------

    result = appointment_agent(state)

    print("\nAPPOINTMENT AGENT RESULT:")
    print(result)

    # --------------------------------------------------
    # Verify appointment was confirmed
    # --------------------------------------------------

    assert result["appointment_confirmed"] is True
    assert result["appointment_id"]

    print("\nAPPOINTMENT ID:")
    print(result["appointment_id"])

    # --------------------------------------------------
    # Verify persistence in Patient Service
    # --------------------------------------------------

    appointments = get_patient_appointments(patient_id)

    print("\nPATIENT APPOINTMENTS:")
    print(appointments)

    matching = [
        appointment
        for appointment in appointments
        if appointment["appointment_id"]
        == result["appointment_id"]
    ]

    assert matching

    print("\n========================================")
    print("INTEGRATION TEST: PASS")
    print("Patient → Appointment → Patient Service")
    print("========================================")


if __name__ == "__main__":
    main()