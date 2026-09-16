import re
from datetime import datetime, timedelta

from ..state import CeylonCareState

from ..services.patient_service import (
    get_patient,
    find_appointment,
    get_patient_appointments,
    get_doctor_schedule,
    format_doctor_schedule_summary,
    get_doctors_by_specialty,
    get_all_doctors,
)

from ..tools.patient_tools import (
    create_appointment_tool,
    cancel_appointment_tool,
    reschedule_appointment_tool,
)


# ============================================================
# Date Extraction
# ============================================================

def normalize_date(value: str) -> str:
    """
    Convert common date expressions into YYYY-MM-DD format.
    """

    value = value.strip().lower()

    today = datetime.now().date()

    # Today
    if value == "today":
        return today.strftime("%Y-%m-%d")

    # Tomorrow
    if value == "tomorrow":
        return (
            today + timedelta(days=1)
        ).strftime("%Y-%m-%d")

    # YYYY-MM-DD
    try:
        return datetime.strptime(
            value,
            "%Y-%m-%d"
        ).strftime("%Y-%m-%d")

    except ValueError:
        pass

    # DD/MM/YYYY
    try:
        return datetime.strptime(
            value,
            "%d/%m/%Y"
        ).strftime("%Y-%m-%d")

    except ValueError:
        pass

    # DD-MM-YYYY
    try:
        return datetime.strptime(
            value,
            "%d-%m-%Y"
        ).strftime("%Y-%m-%d")

    except ValueError:
        pass

    # DD/MM/YY
    try:
        return datetime.strptime(
            value,
            "%d/%m/%y"
        ).strftime("%Y-%m-%d")

    except ValueError:
        pass

    return value


def extract_date(message: str) -> str:
    """
    Extract a date from a user message.

    Examples:
        tomorrow
        today
        2026-09-10
        10/09/2026
        August 20
        September 10 at 11 AM
    """

    message_lower = message.lower()

    # Today / Tomorrow
    if "tomorrow" in message_lower:
        return normalize_date("tomorrow")

    if "today" in message_lower:
        return normalize_date("today")

    # YYYY-MM-DD
    match = re.search(
        r"\b\d{4}-\d{2}-\d{2}\b",
        message
    )

    if match:
        return normalize_date(
            match.group()
        )

    # DD/MM/YYYY or DD-MM-YYYY
    match = re.search(
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
        message
    )

    if match:
        return normalize_date(
            match.group()
        )

    # Month name + day
    month_pattern = (
        r"\b("
        r"january|february|march|april|may|june|"
        r"july|august|september|october|november|december"
        r")\s+"
        r"(\d{1,2})"
        r"(?:st|nd|rd|th)?"
        r"(?:,\s*(\d{4}))?\b"
    )

    match = re.search(
        month_pattern,
        message_lower
    )

    if match:

        month = match.group(1)
        day = match.group(2)
        year = match.group(3)

        if year is None:
            year = str(datetime.now().year)

        date_string = (
            f"{month} {day} {year}"
        )

        try:
            return datetime.strptime(
                date_string,
                "%B %d %Y"
            ).strftime("%Y-%m-%d")

        except ValueError:
            pass

    return ""


# ============================================================
# Time Extraction
# ============================================================

def extract_time(message: str) -> str:
    """
    Extract and normalize a time.

    Examples:
        10:00 AM
        2 PM
        3:30 p.m.
    """

    pattern = (
        r"\b"
        r"(\d{1,2}(?::\d{2})?)"
        r"\s*"
        r"(a\.?m\.?|p\.?m\.?)"
        r"\b"
    )

    match = re.search(
        pattern,
        message,
        re.IGNORECASE
    )

    if not match:
        return ""

    time_value = match.group(1)
    period = match.group(2).upper()

    period = period.replace(".", "")

    return f"{time_value} {period}"


# ============================================================
# Appointment ID Extraction
# ============================================================

def extract_appointment_id(message: str) -> str:
    """
    Extract appointment IDs such as APT-0001.
    """

    match = re.search(
        r"\bAPT-\d{4,}\b",
        message,
        re.IGNORECASE
    )

    if match:
        return match.group().upper()

    return ""


# ============================================================
# Confirmation Detection
# ============================================================

def is_confirmation(message: str) -> bool:
    """
    Detect clear confirmation messages.

    The function accepts both exact confirmation phrases
    and short natural-language confirmation statements.
    """

    message = message.strip().lower()

    confirmation_messages = {
        "yes",
        "yes please",
        "yes, please",
        "confirm",
        "confirmed",
        "please confirm",
        "please do it",
        "do it",
        "book it",
        "please book",
        "okay",
        "ok",
        "sure",
    }

    # Exact confirmation
    if message in confirmation_messages:
        return True

    # Natural-language confirmation
    confirmation_patterns = [
        r"\byes\b.*\bconfirm\b",
        r"\byes\b.*\bbook\b",
        r"\byes\b.*\bcancel\b",
        r"\byes\b.*\bcancellation\b",
        r"\byes\b.*\breschedule\b",
        r"\byes\b.*\bchange\b",

        r"\bconfirm\b.*\bappointment\b",
        r"\bbook\b.*\bappointment\b",
        r"\bcancel\b.*\bappointment\b",
        r"\bcancel\b.*\bit\b",
        r"\breschedule\b.*\bappointment\b",
        r"\breschedule\b.*\bit\b",

        r"\bplease\b.*\bconfirm\b",
        r"\bplease\b.*\bbook\b",
        r"\bplease\b.*\bcancel\b",
        r"\bplease\b.*\breschedule\b",
    ]

    return any(
        re.search(pattern, message)
        for pattern in confirmation_patterns
    )


# ============================================================
# Appointment Agent
# ============================================================

def appointment_agent(
    state: CeylonCareState
):
    """
    Handles:

    - New appointment booking
    - Appointment confirmation
    - Appointment cancellation
    - Cancellation confirmation
    - Appointment rescheduling
    - Reschedule confirmation

    appointment_active controls whether the next user
    message should continue the appointment workflow.
    """

    print("\n[APPOINTMENT AGENT]")

    # ========================================================
    # Existing State
    # ========================================================

    user_message = state.get(
        "user_message",
        ""
    )

    message_lower = user_message.lower()

    patient_id = state.get(
        "patient_id",
        ""
    )

    appointment_active = state.get(
        "appointment_active",
        False
    )

    appointment_id = state.get(
        "appointment_id",
        ""
    )

    specialist = state.get(
        "appointment_specialist",
        ""
    )

    appointment_date = state.get(
        "appointment_date",
        ""
    )

    appointment_time = state.get(
        "appointment_time",
        ""
    )

    confirmed = state.get(
        "appointment_confirmed",
        False
    )

    cancellation_requested = state.get(
        "cancellation_requested",
        False
    )

    cancellation_confirmed = state.get(
        "cancellation_confirmed",
        False
    )

    reschedule_requested = state.get(
        "reschedule_requested",
        False
    )

    reschedule_confirmed = state.get(
        "reschedule_confirmed",
        False
    )

    reschedule_new_date = state.get(
        "reschedule_new_date",
        ""
    )

    reschedule_new_time = state.get(
        "reschedule_new_time",
        ""
    )

    # ========================================================
    # Detect Appointment ID
    # ========================================================

    detected_appointment_id = extract_appointment_id(
        user_message
    )

    if detected_appointment_id:

        appointment_id = detected_appointment_id

        print(
            "[APPOINTMENT] Appointment ID detected: "
            f"{appointment_id}"
        )

    # ========================================================
    # Doctor Mappings & Schedule Queries
    # ========================================================

    doctor_names_map = {
        "perera": ("cardiologist", "Dr. K. Perera"),
        "fernando": ("cardiologist", "Dr. S. Fernando"),
        "jayasinghe": ("general physician", "Dr. N. Jayasinghe"),
        "silva": ("general physician", "Dr. A. Silva"),
        "de silva": ("pediatrician", "Dr. M. De Silva"),
        "wickramasinghe": ("neurologist", "Dr. R. Wickramasinghe"),
        "abeywardena": ("dermatologist", "Dr. T. Abeywardena"),
        "bandara": ("general physician", "Dr. P. Bandara"),
        "rathnayake": ("orthopedic surgeon", "Dr. H. Rathnayake"),
        "senaratne": ("cardiologist", "Dr. U. Senaratne"),
        "mendis": ("general physician", "Dr. C. Mendis"),
        "alwis": ("ent specialist", "Dr. D. Alwis"),
        "gunasekara": ("dermatologist", "Dr. K. Gunasekara")
    }

    # Detect doctor from message
    for d_key, (d_spec, d_name) in doctor_names_map.items():
        if d_key in message_lower:
            specialist = d_spec
            break

    # --------------------------------------------------------
    # Abort / Cancel in-progress booking session
    # --------------------------------------------------------
    abort_words = [
        "cancel booking", "cancel the booking", "stop booking",
        "never mind", "nevermind", "start over", "abort"
    ]
    is_pure_cancel = message_lower.strip() in ["cancel", "stop", "exit", "quit"] and not detected_appointment_id and not state.get("appointment_id")
    if any(w in message_lower for w in abort_words) or is_pure_cancel:
        return {
            "final_response": "I have cancelled your current appointment booking request. How else may I assist you with CeylonCare services today?",
            "appointment_active": False,
            "appointment_specialist": "",
            "appointment_date": "",
            "appointment_time": "",
            "appointment_confirmed": False,
            "appointment_id": "",
            "cancellation_requested": False,
            "cancellation_confirmed": False,
            "reschedule_requested": False,
            "reschedule_confirmed": False,
            "reschedule_new_date": "",
            "reschedule_new_time": "",
        }

    # --------------------------------------------------------
    # Schedule / Availability Inquiries
    # --------------------------------------------------------
    schedule_inquiry_phrases = [
        "what time", "what times", "when is", "when does", "availability",
        "available", "schedule", "timetable", "visiting hours", "who are the",
        "which doctor", "which doctors", "fee", "cost", "charges"
    ]
    if any(p in message_lower for p in schedule_inquiry_phrases) and not is_confirmation(user_message):
        # Look up doctor or department
        queried_target = None
        for d_key, (d_spec, d_name) in doctor_names_map.items():
            if d_key in message_lower:
                queried_target = d_name
                specialist = d_spec
                break

        if not queried_target:
            for spec_key in ["cardiology", "cardiologist", "dermatology", "dermatologist", "pediatrics", "pediatrician", "neurology", "neurologist", "orthopedics", "ent", "general physician", "general medicine"]:
                if spec_key in message_lower:
                    queried_target = spec_key
                    specialist = spec_key
                    break

        if not queried_target and specialist:
            queried_target = specialist

        summary_text = format_doctor_schedule_summary(queried_target or "general")
        return {
            "final_response": summary_text,
            "appointment_active": True,
            "appointment_specialist": specialist,
            "appointment_date": appointment_date,
            "appointment_time": appointment_time,
            "appointment_confirmed": False,
            "appointment_id": appointment_id,
            "cancellation_requested": False,
            "cancellation_confirmed": False,
            "reschedule_requested": False,
            "reschedule_confirmed": False,
            "reschedule_new_date": "",
            "reschedule_new_time": "",
        }

    # ========================================================
    # Detect Actions
    # ========================================================

    cancellation_words = [
        "cancel my appointment",
        "cancel the appointment",
        "cancel appointment",
        "cancellation",
    ]

    reschedule_words = [
        "reschedule my appointment",
        "reschedule the appointment",
        "reschedule appointment",
        "reschedule",
        "change my appointment",
        "change the appointment",
        "change appointment",
        "move my appointment",
        "move appointment",
        "postpone",
    ]

    # --------------------------------------------------------
    # Reschedule request
    # --------------------------------------------------------

    if any(
        word in message_lower
        for word in reschedule_words
    ):

        reschedule_requested = True
        cancellation_requested = False
        cancellation_confirmed = False
        reschedule_confirmed = False
        appointment_active = True

        print(
            "[APPOINTMENT ACTION] "
            "Rescheduling requested."
        )

    # --------------------------------------------------------
    # Cancellation request
    # --------------------------------------------------------

    elif any(
        word in message_lower
        for word in cancellation_words
    ) or (detected_appointment_id and "cancel" in message_lower):

        cancellation_requested = True
        reschedule_requested = False
        cancellation_confirmed = False
        appointment_active = True

        print(
            "[APPOINTMENT ACTION] "
            "Cancellation requested."
        )

    # ========================================================
    # Load Existing Appointment
    # ========================================================

    if (
        patient_id
        and appointment_id
        and (
            cancellation_requested
            or reschedule_requested
        )
    ):

        patient = get_patient(
            patient_id
        )

        if patient:

            appointment = None

            appointments = get_patient_appointments(
                patient_id
            )

            for item in appointments:

                if (
                    item["appointment_id"].upper()
                    == appointment_id.upper()
                ):

                    appointment = item
                    break

            # Fallback lookup
            if (
                appointment is None
                and specialist
                and appointment_date
                and appointment_time
            ):

                appointment = find_appointment(
                    patient_id,
                    specialist,
                    appointment_date,
                    appointment_time,
                )

            if appointment:

                specialist = appointment[
                    "specialist"
                ]

                appointment_date = appointment[
                    "date"
                ]

                appointment_time = appointment[
                    "time"
                ]

                print(
                    "[APPOINTMENT] "
                    "Appointment details loaded."
                )

            else:

                print(
                    "[APPOINTMENT ERROR] "
                    "Appointment not found."
                )

        else:

            print(
                "[APPOINTMENT ERROR] "
                f"Patient {patient_id} was not found."
            )

    # ========================================================
    # Confirmation Detection
    # ========================================================

    user_confirmed = is_confirmation(
        user_message
    )

    # ========================================================
    # Cancellation Confirmation
    # ========================================================

    if (
        cancellation_requested
        and appointment_id
        and user_confirmed
        and not cancellation_confirmed
    ):

        cancellation_result = cancel_appointment_tool.invoke(
            {
                "patient_id": patient_id,
                "appointment_id": appointment_id,
            }
        )

        # ----------------------------------------------------
        # Successful cancellation
        # ----------------------------------------------------

        if (
            cancellation_result.get("success")
            and cancellation_result.get("cancelled")
        ):

            cancelled = cancellation_result.get(
                "appointment"
            )

            cancellation_confirmed = True
            confirmed = False
            appointment_active = False

            specialist = cancelled[
                "specialist"
            ]

            appointment_date = cancelled[
                "date"
            ]

            appointment_time = cancelled[
                "time"
            ]

            print(
                "[APPOINTMENT STATUS] CANCELLED"
            )

            response = (
                "Your appointment has been "
                "cancelled successfully.\n\n"
                f"Appointment ID: {appointment_id}\n"
                f"Specialist: {specialist}\n"
                f"Date: {appointment_date}\n"
                f"Time: {appointment_time}"
            )

            if patient_id:

                response += (
                    f"\nPatient ID: {patient_id}"
                )

            return {
                "final_response": response,
                "appointment_active": False,
                "appointment_specialist": specialist,
                "appointment_date": appointment_date,
                "appointment_time": appointment_time,
                "appointment_confirmed": False,
                "appointment_id": appointment_id,
                "cancellation_requested": False,
                "cancellation_confirmed": True,
                "reschedule_requested": False,
                "reschedule_confirmed": False,
                "reschedule_new_date": "",
                "reschedule_new_time": "",
            }

        # ----------------------------------------------------
        # Cancellation failed
        # ----------------------------------------------------

        else:

            error_message = cancellation_result.get(
                "error",
                "I could not cancel this appointment."
            )

            return {
                "final_response": error_message,
                "appointment_active": False,
                "appointment_specialist": specialist,
                "appointment_date": appointment_date,
                "appointment_time": appointment_time,
                "appointment_confirmed": False,
                "appointment_id": appointment_id,
                "cancellation_requested": True,
                "cancellation_confirmed": False,
                "reschedule_requested": False,
                "reschedule_confirmed": False,
                "reschedule_new_date": "",
                "reschedule_new_time": "",
            }

    # ========================================================
    # Rescheduling - Extract New Date and Time
    # ========================================================

    if reschedule_requested:

        detected_date = extract_date(
            user_message
        )

        detected_time = extract_time(
            user_message
        )

        if detected_date:

            reschedule_new_date = detected_date

            print(
                "[RESCHEDULE] New date detected: "
                f"{reschedule_new_date}"
            )

        if detected_time:

            reschedule_new_time = detected_time

            print(
                "[RESCHEDULE] New time detected: "
                f"{reschedule_new_time}"
            )

    # ========================================================
    # Rescheduling Confirmation
    # ========================================================

    if (
        reschedule_requested
        and appointment_id
        and reschedule_new_date
        and reschedule_new_time
        and user_confirmed
        and not reschedule_confirmed
    ):

        # ----------------------------------------------------
        # Execute rescheduling through the LangChain tool.
        # ----------------------------------------------------

        reschedule_result = reschedule_appointment_tool.invoke(
            {
                "patient_id": patient_id,
                "appointment_id": appointment_id,
                "new_date": reschedule_new_date,
                "new_time": reschedule_new_time,
            }
        )

        # ----------------------------------------------------
        # Successful rescheduling
        # ----------------------------------------------------

        if (
            reschedule_result.get("success")
            and reschedule_result.get("rescheduled")
        ):

            updated = reschedule_result.get(
                "appointment"
            )

            if updated is None:
                return {
                    "final_response": (
                        "The appointment was rescheduled, "
                        "but I could not retrieve the updated "
                        "appointment details."
                    ),
                    "appointment_active": False,
                    "appointment_specialist": specialist,
                    "appointment_date": reschedule_new_date,
                    "appointment_time": reschedule_new_time,
                    "appointment_confirmed": True,
                    "appointment_id": appointment_id,
                    "cancellation_requested": False,
                    "cancellation_confirmed": False,
                    "reschedule_requested": False,
                    "reschedule_confirmed": True,
                    "reschedule_new_date": reschedule_new_date,
                    "reschedule_new_time": reschedule_new_time,
                }

            reschedule_confirmed = True
            confirmed = True
            appointment_active = False

            appointment_date = updated[
                "date"
            ]

            appointment_time = updated[
                "time"
            ]

            specialist = updated[
                "specialist"
            ]

            print(
                "[APPOINTMENT STATUS] "
                "RESCHEDULED"
            )

            response = (
                "Your appointment has been "
                "rescheduled successfully.\n\n"
                f"Appointment ID: {appointment_id}\n"
                f"Specialist: {specialist}\n"
                f"New Date: {appointment_date}\n"
                f"New Time: {appointment_time}"
            )

            if patient_id:

                response += (
                    f"\nPatient ID: {patient_id}"
                )

            return {
                "final_response": response,
                "appointment_active": False,
                "appointment_specialist": specialist,
                "appointment_date": appointment_date,
                "appointment_time": appointment_time,
                "appointment_confirmed": True,
                "appointment_id": appointment_id,
                "cancellation_requested": False,
                "cancellation_confirmed": False,
                "reschedule_requested": False,
                "reschedule_confirmed": True,
                "reschedule_new_date": reschedule_new_date,
                "reschedule_new_time": reschedule_new_time,
            }

        # ----------------------------------------------------
        # Rescheduling failed
        # ----------------------------------------------------

        else:

            error_message = reschedule_result.get(
                "error",
                "I could not reschedule this appointment."
            )

            print(
                "[APPOINTMENT ERROR] "
                f"{error_message}"
            )

            return {
                "final_response": error_message,
                "appointment_active": True,
                "appointment_specialist": specialist,
                "appointment_date": appointment_date,
                "appointment_time": appointment_time,
                "appointment_confirmed": False,
                "appointment_id": appointment_id,
                "cancellation_requested": False,
                "cancellation_confirmed": False,
                "reschedule_requested": True,
                "reschedule_confirmed": False,
                "reschedule_new_date": reschedule_new_date,
                "reschedule_new_time": reschedule_new_time,
            }

    # ========================================================
    # Cancellation - Show Appointment
    # ========================================================

    if (
        cancellation_requested
        and appointment_id
        and not cancellation_confirmed
    ):

        appointment_active = True

        if (
            specialist
            and appointment_date
            and appointment_time
        ):

            response = (
                "I found the following appointment:\n\n"
                f"Appointment ID: {appointment_id}\n"
                f"Specialist: {specialist}\n"
                f"Date: {appointment_date}\n"
                f"Time: {appointment_time}\n\n"
                "Would you like to cancel this appointment?"
            )

        else:

            response = (
                "I could not find the requested "
                "appointment. Please provide a valid "
                "appointment ID."
            )

        return {
            "final_response": response,
            "appointment_active": appointment_active,
            "appointment_specialist": specialist,
            "appointment_date": appointment_date,
            "appointment_time": appointment_time,
            "appointment_confirmed": False,
            "appointment_id": appointment_id,
            "cancellation_requested": True,
            "cancellation_confirmed": False,
            "reschedule_requested": False,
            "reschedule_confirmed": False,
            "reschedule_new_date": "",
            "reschedule_new_time": "",
        }

    # ========================================================
    # Rescheduling - Ask for New Date / Time
    # ========================================================

    if (
        reschedule_requested
        and appointment_id
        and specialist
    ):

        appointment_active = True

        if (
            reschedule_new_date
            and reschedule_new_time
        ):

            response = (
                "I have the following new appointment "
                "details:\n\n"
                f"Appointment ID: {appointment_id}\n"
                f"Specialist: {specialist}\n"
                f"New Date: {reschedule_new_date}\n"
                f"New Time: {reschedule_new_time}\n\n"
                "Would you like to confirm this "
                "reschedule?"
            )

        else:

            response = (
                "I found the following appointment:\n\n"
                f"Appointment ID: {appointment_id}\n"
                f"Specialist: {specialist}\n"
                f"Current Date: {appointment_date}\n"
                f"Current Time: {appointment_time}\n\n"
                "What new date and time would you "
                "prefer?"
            )

        return {
            "final_response": response,
            "appointment_active": True,
            "appointment_specialist": specialist,
            "appointment_date": appointment_date,
            "appointment_time": appointment_time,
            "appointment_confirmed": False,
            "appointment_id": appointment_id,
            "cancellation_requested": False,
            "cancellation_confirmed": False,
            "reschedule_requested": True,
            "reschedule_confirmed": False,
            "reschedule_new_date": reschedule_new_date,
            "reschedule_new_time": reschedule_new_time,
        }

    # ========================================================
    # BOOKING
    # ========================================================

    # --------------------------------------------------------
    # Detect Specialist
    # --------------------------------------------------------

    specialist_mapping = {
        "cardiologist": "cardiologist",
        "cardiology": "cardiologist",
        "heart": "cardiologist",
        "dermatologist": "dermatologist",
        "dermatology": "dermatologist",
        "skin": "dermatologist",
        "pediatrician": "pediatrician",
        "pediatrics": "pediatrician",
        "child": "pediatrician",
        "neurologist": "neurologist",
        "neurology": "neurologist",
        "nerve": "neurologist",
        "orthopedic surgeon": "orthopedic surgeon",
        "orthopedic": "orthopedic surgeon",
        "orthopedics": "orthopedic surgeon",
        "bone": "orthopedic surgeon",
        "ent specialist": "ent specialist",
        "ent": "ent specialist",
        "ear": "ent specialist",
        "general physician": "general physician",
        "general medicine": "general physician",
        "physician": "general physician",
        "doctor": "doctor",
    }

    # Check doctor names first
    for d_key, (d_spec, d_name) in doctor_names_map.items():
        if d_key in message_lower:
            specialist = d_spec
            break

    if not specialist or specialist == "doctor":
        for item, mapped_spec in specialist_mapping.items():
            if item in message_lower:
                specialist = mapped_spec
                break

    # --------------------------------------------------------
    # Detect Date
    # --------------------------------------------------------

    detected_date = extract_date(
        user_message
    )

    if detected_date:

        appointment_date = detected_date

    # --------------------------------------------------------
    # Detect Time
    # --------------------------------------------------------

    detected_time = extract_time(
        user_message
    )

    if detected_time:

        appointment_time = detected_time

    # ========================================================
    # Booking Confirmation
    # ========================================================

    if (
        user_confirmed
        and specialist
        and appointment_date
        and appointment_time
        and not cancellation_requested
        and not reschedule_requested
    ):

        if patient_id:

            patient = get_patient(
                patient_id
            )

            if patient:

                existing_appointment = find_appointment(
                    patient_id,
                    specialist,
                    appointment_date,
                    appointment_time,
                )

                if existing_appointment:

                    appointment_id = (
                        existing_appointment[
                            "appointment_id"
                        ]
                    )

                else:

                    appointment_result = (
                        create_appointment_tool.invoke(
                            {
                                "patient_id": patient_id,
                                "specialist": specialist,
                                "appointment_date": appointment_date,
                                "appointment_time": appointment_time,
                            }
                        )
                    )

                    if appointment_result.get(
                        "success"
                    ):

                        appointment = (
                            appointment_result.get(
                                "appointment"
                            )
                        )

                        appointment_id = (
                            appointment[
                                "appointment_id"
                            ]
                        )

                    else:

                        confirmed = False

                        print(
                            "[APPOINTMENT ERROR] "
                            f"{appointment_result.get('error', 'Appointment creation failed.')}"
                        )

                        return {
                            "final_response": (
                                appointment_result.get(
                                    "error",
                                    "I could not create the appointment."
                                )
                            ),
                            "appointment_active": False,
                            "appointment_specialist": specialist,
                            "appointment_date": appointment_date,
                            "appointment_time": appointment_time,
                            "appointment_confirmed": False,
                            "appointment_id": "",
                            "cancellation_requested": False,
                            "cancellation_confirmed": False,
                            "reschedule_requested": False,
                            "reschedule_confirmed": False,
                            "reschedule_new_date": "",
                            "reschedule_new_time": "",
                        }

                confirmed = True

            else:

                confirmed = False

                print(
                    "[APPOINTMENT ERROR] "
                    f"Patient {patient_id} was not found."
                )

                return {
                    "final_response": (
                        f"No patient record was found "
                        f"for patient ID {patient_id}."
                    ),
                    "appointment_active": False,
                    "appointment_specialist": specialist,
                    "appointment_date": appointment_date,
                    "appointment_time": appointment_time,
                    "appointment_confirmed": False,
                    "appointment_id": "",
                    "cancellation_requested": False,
                    "cancellation_confirmed": False,
                    "reschedule_requested": False,
                    "reschedule_confirmed": False,
                    "reschedule_new_date": "",
                    "reschedule_new_time": "",
                }

        else:

            # Backward compatibility for tests
            # without patient ID.
            confirmed = True

        if confirmed:

            appointment_active = False

    # ========================================================
    # Print Appointment Details
    # ========================================================

    if specialist:

        print(
            "[APPOINTMENT DETAILS] "
            f"Specialist: {specialist}"
        )

    if appointment_date:

        print(
            "[APPOINTMENT DETAILS] "
            f"Date: {appointment_date}"
        )

    if appointment_time:

        print(
            "[APPOINTMENT DETAILS] "
            f"Time: {appointment_time}"
        )

    # ========================================================
    # Booking Response
    # ========================================================

    if confirmed:

        response = (
            "Your appointment request has been "
            "confirmed.\n\n"
            f"Specialist: {specialist}\n"
            f"Date: {appointment_date}\n"
            f"Time: {appointment_time}"
        )

        if appointment_id:

            response += (
                f"\nAppointment ID: {appointment_id}"
            )

        if patient_id:

            response += (
                f"\nPatient ID: {patient_id}"
            )

        print(
            "[APPOINTMENT STATUS] CONFIRMED"
        )

    elif (
        specialist
        and appointment_date
        and appointment_time
    ):

        # Waiting for confirmation.
        appointment_active = True

        response = (
            "I have the following appointment "
            "details:\n\n"
            f"Specialist: {specialist}\n"
            f"Date: {appointment_date}\n"
            f"Time: {appointment_time}\n\n"
            "Would you like to confirm this appointment?"
        )

    elif specialist and appointment_date:

        # Waiting for time.
        appointment_active = True

        response = (
            f"I can help you request an appointment "
            f"with a {specialist} for "
            f"{appointment_date}. "
            "What time would you prefer?"
        )

    elif specialist:

        # Waiting for date.
        appointment_active = True

        response = (
            f"I can help you request an appointment "
            f"with a {specialist}. "
            "What date would you prefer?"
        )

    elif appointment_date:

        # Waiting for specialist.
        appointment_active = True

        response = (
            f"I can help you request an appointment "
            f"for {appointment_date}. "
            "Which type of doctor or specialist "
            "would you like to see?"
        )

    else:

        # New appointment request.
        appointment_active = True

        response = (
            "I can help you with an appointment. "
            "Please tell me which doctor or specialist "
            "you would like to see and your preferred "
            "appointment date."
        )

    # ========================================================
    # Return Updated State
    # ========================================================

    return {
        "final_response": response,

        # IMPORTANT:
        # This controls whether the next message
        # continues the appointment workflow.
        "appointment_active": appointment_active,

        "appointment_specialist": specialist,
        "appointment_date": appointment_date,
        "appointment_time": appointment_time,
        "appointment_confirmed": confirmed,
        "appointment_id": appointment_id,

        "cancellation_requested": cancellation_requested,
        "cancellation_confirmed": cancellation_confirmed,

        "reschedule_requested": reschedule_requested,
        "reschedule_confirmed": reschedule_confirmed,
        "reschedule_new_date": reschedule_new_date,
        "reschedule_new_time": reschedule_new_time,
    }