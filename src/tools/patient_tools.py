from langchain_core.tools import tool

from ..services.patient_service import (
    get_patient,
    get_patient_appointments,
    create_appointment,
    find_appointment,
    cancel_appointment,
    reschedule_appointment,
)


# ============================================================
# Patient Tool
# ============================================================

@tool
def get_patient_tool(patient_id: str) -> dict:
    """
    Retrieve a synthetic CeylonCare patient record by patient ID.

    This tool is intended for the CeylonCare academic prototype.
    It validates the patient ID before accessing the patient service.
    """

    print("\n[PATIENT TOOL]")
    print(
        f"[PATIENT TOOL] Requested patient ID: {patient_id}"
    )

    # --------------------------------------------------------
    # Input validation
    # --------------------------------------------------------

    patient_id = patient_id.strip()

    if not patient_id:
        return {
            "success": False,
            "error": "Patient ID is required."
        }

    if len(patient_id) > 20:
        return {
            "success": False,
            "error": "Patient ID is invalid."
        }

    # --------------------------------------------------------
    # Patient service
    # --------------------------------------------------------

    patient = get_patient(patient_id)

    if not patient:

        print(
            "[PATIENT TOOL] "
            "Patient was not found."
        )

        return {
            "success": False,
            "error": (
                f"No patient record was found for "
                f"patient ID {patient_id}."
            )
        }

    print(
        "[PATIENT TOOL] "
        "Patient record retrieved successfully."
    )

    return {
        "success": True,
        "patient": patient,
    }


# ============================================================
# Patient Appointments Tool
# ============================================================

@tool
def get_patient_appointments_tool(
    patient_id: str
) -> dict:
    """
    Retrieve all appointments belonging to a synthetic
    CeylonCare patient.

    Use this tool when appointment information is required
    for a specific patient.
    """

    print("\n[PATIENT APPOINTMENT TOOL]")

    print(
        f"[PATIENT APPOINTMENT TOOL] "
        f"Requested patient ID: {patient_id}"
    )

    # --------------------------------------------------------
    # Input validation
    # --------------------------------------------------------

    patient_id = patient_id.strip()

    if not patient_id:
        return {
            "success": False,
            "error": "Patient ID is required."
        }

    if len(patient_id) > 20:
        return {
            "success": False,
            "error": "Patient ID is invalid."
        }

    # --------------------------------------------------------
    # Verify patient exists
    # --------------------------------------------------------

    patient = get_patient(patient_id)

    if not patient:
        return {
            "success": False,
            "error": (
                f"No patient record was found for "
                f"patient ID {patient_id}."
            )
        }

    # --------------------------------------------------------
    # Retrieve appointments
    # --------------------------------------------------------

    appointments = get_patient_appointments(
        patient_id
    )

    print(
        "[PATIENT APPOINTMENT TOOL] "
        f"Retrieved {len(appointments)} appointment(s)."
    )

    return {
        "success": True,
        "patient_id": patient_id,
        "appointments": appointments,
    }


# ============================================================
# Create Appointment Tool
# ============================================================

@tool
def create_appointment_tool(
    patient_id: str,
    specialist: str,
    appointment_date: str,
    appointment_time: str,
) -> dict:
    """
    Create a confirmed synthetic CeylonCare appointment.

    This tool validates the patient and appointment details
    and prevents duplicate appointment creation.

    Human approval will be added at the orchestration layer
    before this tool is used for autonomous appointment booking.
    """

    print("\n[CREATE APPOINTMENT TOOL]")

    # --------------------------------------------------------
    # Normalize input
    # --------------------------------------------------------

    patient_id = patient_id.strip()
    specialist = specialist.strip()
    appointment_date = appointment_date.strip()
    appointment_time = appointment_time.strip()

    print(
        f"[CREATE APPOINTMENT TOOL] "
        f"Patient ID: {patient_id}"
    )

    print(
        f"[CREATE APPOINTMENT TOOL] "
        f"Specialist: {specialist}"
    )

    print(
        f"[CREATE APPOINTMENT TOOL] "
        f"Date: {appointment_date}"
    )

    print(
        f"[CREATE APPOINTMENT TOOL] "
        f"Time: {appointment_time}"
    )

    # --------------------------------------------------------
    # Required-field validation
    # --------------------------------------------------------

    if not patient_id:
        return {
            "success": False,
            "error": "Patient ID is required."
        }

    if not specialist:
        return {
            "success": False,
            "error": "Specialist is required."
        }

    if not appointment_date:
        return {
            "success": False,
            "error": "Appointment date is required."
        }

    if not appointment_time:
        return {
            "success": False,
            "error": "Appointment time is required."
        }

    # --------------------------------------------------------
    # Length validation
    # --------------------------------------------------------

    if len(patient_id) > 20:
        return {
            "success": False,
            "error": "Patient ID is invalid."
        }

    if len(specialist) > 100:
        return {
            "success": False,
            "error": "Specialist name is invalid."
        }

    if len(appointment_date) > 30:
        return {
            "success": False,
            "error": "Appointment date is invalid."
        }

    if len(appointment_time) > 30:
        return {
            "success": False,
            "error": "Appointment time is invalid."
        }

    # --------------------------------------------------------
    # Verify patient exists
    # --------------------------------------------------------

    patient = get_patient(patient_id)

    if not patient:
        return {
            "success": False,
            "error": (
                f"No patient record was found for "
                f"patient ID {patient_id}."
            )
        }

    # --------------------------------------------------------
    # Prevent duplicate appointment creation
    # --------------------------------------------------------

    existing = find_appointment(
        patient_id,
        specialist,
        appointment_date,
        appointment_time,
    )

    if existing:

        print(
            "[CREATE APPOINTMENT TOOL] "
            "Existing matching appointment found."
        )

        return {
            "success": True,
            "created": False,
            "appointment": existing,
            "message": (
                "An appointment with the same details "
                "already exists."
            ),
        }

    # --------------------------------------------------------
    # Create appointment
    # --------------------------------------------------------

    appointment = create_appointment(
        patient_id,
        specialist,
        appointment_date,
        appointment_time,
    )

    print(
        "[CREATE APPOINTMENT TOOL] "
        f"Appointment created: "
        f"{appointment['appointment_id']}"
    )

    return {
        "success": True,
        "created": True,
        "appointment": appointment,
        "message": "Appointment created successfully.",
    }


# ============================================================
# Cancel Appointment Tool
# ============================================================

@tool
def cancel_appointment_tool(
    patient_id: str,
    appointment_id: str,
) -> dict:
    """
    Cancel an existing synthetic CeylonCare appointment.

    The tool validates the patient and appointment identifiers,
    checks the current appointment status before cancellation,
    and then requests cancellation from the patient service.

    Human approval will be added at the orchestration layer
    before this tool is used for autonomous cancellation.
    """

    print("\n[CANCEL APPOINTMENT TOOL]")

    # --------------------------------------------------------
    # Normalize input
    # --------------------------------------------------------

    patient_id = patient_id.strip()
    appointment_id = appointment_id.strip()

    print(
        f"[CANCEL APPOINTMENT TOOL] "
        f"Patient ID: {patient_id}"
    )

    print(
        f"[CANCEL APPOINTMENT TOOL] "
        f"Appointment ID: {appointment_id}"
    )

    # --------------------------------------------------------
    # Required-field validation
    # --------------------------------------------------------

    if not patient_id:
        return {
            "success": False,
            "error": "Patient ID is required."
        }

    if not appointment_id:
        return {
            "success": False,
            "error": "Appointment ID is required."
        }

    # --------------------------------------------------------
    # Length validation
    # --------------------------------------------------------

    if len(patient_id) > 20:
        return {
            "success": False,
            "error": "Patient ID is invalid."
        }

    if len(appointment_id) > 30:
        return {
            "success": False,
            "error": "Appointment ID is invalid."
        }

    # --------------------------------------------------------
    # Verify patient exists
    # --------------------------------------------------------

    patient = get_patient(patient_id)

    if not patient:
        return {
            "success": False,
            "error": (
                f"No patient record was found for "
                f"patient ID {patient_id}."
            )
        }

    # --------------------------------------------------------
    # Find current appointment
    # --------------------------------------------------------

    appointments = get_patient_appointments(
        patient_id
    )

    target_appointment = None

    for appointment in appointments:

        if (
            appointment["appointment_id"].lower()
            == appointment_id.lower()
        ):
            target_appointment = appointment
            break

    # --------------------------------------------------------
    # Appointment not found
    # --------------------------------------------------------

    if target_appointment is None:

        print(
            "[CANCEL APPOINTMENT TOOL] "
            "Appointment was not found."
        )

        return {
            "success": False,
            "error": (
                f"No appointment {appointment_id} "
                f"was found for patient {patient_id}."
            )
        }

    # --------------------------------------------------------
    # Already cancelled
    # --------------------------------------------------------

    if (
        target_appointment["status"].lower()
        == "cancelled"
    ):

        print(
            "[CANCEL APPOINTMENT TOOL] "
            "Appointment is already cancelled."
        )

        return {
            "success": True,
            "cancelled": False,
            "appointment": target_appointment,
            "message": (
                "The appointment is already cancelled."
            ),
        }

    # --------------------------------------------------------
    # Cancel confirmed appointment
    # --------------------------------------------------------

    appointment = cancel_appointment(
        patient_id,
        appointment_id,
    )

    # --------------------------------------------------------
    # Cancellation failed
    # --------------------------------------------------------

    if appointment is None:

        print(
            "[CANCEL APPOINTMENT TOOL] "
            "Cancellation failed."
        )

        return {
            "success": False,
            "error": (
                f"Unable to cancel appointment "
                f"{appointment_id}."
            )
        }

    # --------------------------------------------------------
    # Successful cancellation
    # --------------------------------------------------------

    print(
        "[CANCEL APPOINTMENT TOOL] "
        f"Appointment cancelled: "
        f"{appointment['appointment_id']}"
    )

    return {
        "success": True,
        "cancelled": True,
        "appointment": appointment,
        "message": "Appointment cancelled successfully.",
    }

# ============================================================
# Reschedule Appointment Tool
# ============================================================

@tool
def reschedule_appointment_tool(
    patient_id: str,
    appointment_id: str,
    new_date: str,
    new_time: str,
) -> dict:
    """
    Reschedule an existing confirmed synthetic
    CeylonCare appointment.

    The tool validates the patient and appointment
    identifiers, verifies the current appointment,
    prevents rescheduling cancelled appointments,
    and prevents scheduling conflicts.

    Human approval will be added at the orchestration
    layer before this tool is used for autonomous
    appointment rescheduling.
    """

    print("\n[RESCHEDULE APPOINTMENT TOOL]")

    # --------------------------------------------------------
    # Normalize input
    # --------------------------------------------------------

    patient_id = patient_id.strip()
    appointment_id = appointment_id.strip()
    new_date = new_date.strip()
    new_time = new_time.strip()

    print(
        f"[RESCHEDULE APPOINTMENT TOOL] "
        f"Patient ID: {patient_id}"
    )

    print(
        f"[RESCHEDULE APPOINTMENT TOOL] "
        f"Appointment ID: {appointment_id}"
    )

    print(
        f"[RESCHEDULE APPOINTMENT TOOL] "
        f"New Date: {new_date}"
    )

    print(
        f"[RESCHEDULE APPOINTMENT TOOL] "
        f"New Time: {new_time}"
    )

    # --------------------------------------------------------
    # Required-field validation
    # --------------------------------------------------------

    if not patient_id:
        return {
            "success": False,
            "error": "Patient ID is required."
        }

    if not appointment_id:
        return {
            "success": False,
            "error": "Appointment ID is required."
        }

    if not new_date:
        return {
            "success": False,
            "error": "New appointment date is required."
        }

    if not new_time:
        return {
            "success": False,
            "error": "New appointment time is required."
        }

    # --------------------------------------------------------
    # Length validation
    # --------------------------------------------------------

    if len(patient_id) > 20:
        return {
            "success": False,
            "error": "Patient ID is invalid."
        }

    if len(appointment_id) > 30:
        return {
            "success": False,
            "error": "Appointment ID is invalid."
        }

    if len(new_date) > 30:
        return {
            "success": False,
            "error": "New appointment date is invalid."
        }

    if len(new_time) > 30:
        return {
            "success": False,
            "error": "New appointment time is invalid."
        }

    # --------------------------------------------------------
    # Verify patient exists
    # --------------------------------------------------------

    patient = get_patient(patient_id)

    if not patient:
        return {
            "success": False,
            "error": (
                f"No patient record was found for "
                f"patient ID {patient_id}."
            )
        }

    # --------------------------------------------------------
    # Find current appointment
    # --------------------------------------------------------

    appointments = get_patient_appointments(
        patient_id
    )

    target_appointment = None

    for appointment in appointments:

        if (
            appointment["appointment_id"].lower()
            == appointment_id.lower()
        ):
            target_appointment = appointment
            break

    # --------------------------------------------------------
    # Appointment not found
    # --------------------------------------------------------

    if target_appointment is None:

        print(
            "[RESCHEDULE APPOINTMENT TOOL] "
            "Appointment was not found."
        )

        return {
            "success": False,
            "error": (
                f"No appointment {appointment_id} "
                f"was found for patient {patient_id}."
            )
        }

    # --------------------------------------------------------
    # Only confirmed appointments can be rescheduled
    # --------------------------------------------------------

    if (
        target_appointment["status"].lower()
        != "confirmed"
    ):

        print(
            "[RESCHEDULE APPOINTMENT TOOL] "
            "Appointment is not confirmed."
        )

        return {
            "success": False,
            "error": (
                f"Appointment {appointment_id} "
                f"cannot be rescheduled because "
                f"its current status is "
                f"{target_appointment['status']}."
            ),
            "appointment": target_appointment,
        }

    # --------------------------------------------------------
    # Prevent scheduling conflict
    # --------------------------------------------------------

    for appointment in appointments:

        if (
            appointment["appointment_id"].lower()
            != appointment_id.lower()
            and appointment["date"].lower()
            == new_date.lower()
            and appointment["time"].lower()
            == new_time.lower()
            and appointment["status"].lower()
            == "confirmed"
        ):

            print(
                "[RESCHEDULE APPOINTMENT TOOL] "
                "Scheduling conflict detected."
            )

            return {
                "success": False,
                "error": (
                    "The requested new date and time "
                    "already has another confirmed "
                    "appointment for this patient."
                ),
                "appointment": target_appointment,
            }

    # --------------------------------------------------------
    # Reschedule appointment
    # --------------------------------------------------------

    appointment = reschedule_appointment(
        patient_id,
        appointment_id,
        new_date,
        new_time,
    )

    # --------------------------------------------------------
    # Rescheduling failed
    # --------------------------------------------------------

    if appointment is None:

        print(
            "[RESCHEDULE APPOINTMENT TOOL] "
            "Rescheduling failed."
        )

        return {
            "success": False,
            "error": (
                f"Unable to reschedule "
                f"appointment {appointment_id}."
            )
        }

    # --------------------------------------------------------
    # Successful rescheduling
    # --------------------------------------------------------

    print(
        "[RESCHEDULE APPOINTMENT TOOL] "
        f"Appointment rescheduled: "
        f"{appointment['appointment_id']}"
    )

    return {
        "success": True,
        "rescheduled": True,
        "appointment": appointment,
        "message": (
            "Appointment rescheduled successfully."
        ),
    }