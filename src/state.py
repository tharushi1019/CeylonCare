from typing import TypedDict


class CeylonCareState(TypedDict, total=False):
    """
    Shared state passed between CeylonCare LangGraph nodes.
    """

    # ========================================================
    # User
    # ========================================================

    user_message: str

    # ========================================================
    # Patient
    # ========================================================

    patient_id: str

    # ========================================================
    # Supervisor Information
    # ========================================================

    intent: str
    selected_agent: str
    confidence: float
    supervisor_reason: str

    # ========================================================
    # Final Response
    # ========================================================

    final_response: str

    # ========================================================
    # Appointment Information
    # ========================================================

    appointment_id: str
    appointment_specialist: str
    appointment_date: str
    appointment_time: str
    appointment_confirmed: bool
    appointment_active: bool

    # ========================================================
    # Appointment Cancellation
    # ========================================================

    cancellation_requested: bool
    cancellation_confirmed: bool

    # ========================================================
    # Appointment Rescheduling
    # ========================================================

    reschedule_requested: bool
    reschedule_confirmed: bool

    # New date/time requested by the patient
    reschedule_new_date: str
    reschedule_new_time: str

    # ========================================================
    # Human-in-the-Loop Information
    # ========================================================

    human_escalation_required: bool
    human_decision: str