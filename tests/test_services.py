"""
Unit & Integration Tests for CeylonCare Core Patient Services.
Tests patient EHR lookup, doctor directory, authentication, appointment workflows, and patient feedback.
"""
import pytest
from src.services.patient_service import (
    get_patient,
    get_all_patients,
    authenticate_user,
    register_patient,
    get_all_doctors,
    get_all_branches,
    get_doctor_schedule,
    get_doctors_by_specialty,
    create_appointment,
    cancel_appointment,
    reschedule_appointment,
    get_patient_appointments,
    format_visit_history,
    submit_patient_feedback,
    get_all_feedback,
    get_feedback_summary,
)

def test_get_all_doctors():
    doctors = get_all_doctors()
    assert isinstance(doctors, list)
    assert len(doctors) >= 5
    first_doc = doctors[0]
    assert "name" in first_doc
    assert "specialty" in first_doc
    assert "branch" in first_doc

def test_get_all_branches():
    branches = get_all_branches()
    assert isinstance(branches, list)
    assert len(branches) >= 3
    branch_names = [b["name"] for b in branches]
    assert "Colombo Central Hospital" in branch_names

def test_doctor_schedule_lookup():
    schedule_text = get_doctor_schedule("Cardiologist")
    assert schedule_text is not None
    assert "Perera" in schedule_text.get("name", "") or "Fernando" in schedule_text.get("name", "")

def test_patient_lookup():
    patient = get_patient("P001")
    assert patient is not None
    assert patient["name"] == "Nimal Perera"
    assert "Colombo" in patient.get("city", "")

def test_authentication():
    # Valid patient
    success, user, role = authenticate_user("P001", "password123")
    assert success is True
    assert role == "patient"
    assert user["name"] == "Nimal Perera"

    # Valid operator
    success, op, role = authenticate_user("operator@ceyloncare.lk", "admin")
    assert success is True
    assert role == "operator"

    # Invalid credentials
    success, _, _ = authenticate_user("P001", "wrong_password")
    assert success is False

def test_appointment_lifecycle():
    # 1. Create appointment
    appt = create_appointment(
        patient_id="P001",
        specialist="Cardiologist",
        appointment_date="2026-12-15",
        appointment_time="10:30 AM",
        doctor="Dr. K. Perera",
        branch="Colombo Central Hospital"
    )
    assert appt is not None
    assert "appointment_id" in appt
    appt_id = appt["appointment_id"]
    assert appt["status"] == "confirmed"

    # 2. Slot collision detection: attempt to book exact same slot
    collision_attempt = create_appointment(
        patient_id="P002",
        specialist="Cardiologist",
        appointment_date="2026-12-15",
        appointment_time="10:30 AM",
        doctor="Dr. K. Perera",
        branch="Colombo Central Hospital"
    )
    assert collision_attempt["status"] == "conflict"
    assert "already booked" in collision_attempt["error"]

    # 3. Retrieve appointments
    appts = get_patient_appointments("P001")
    assert any(a["appointment_id"] == appt_id for a in appts)

    # 4. Reschedule appointment
    rescheduled = reschedule_appointment("P001", appt_id, "2026-12-18", "11:00 AM")
    assert rescheduled is not None
    assert rescheduled["date"] == "2026-12-18"
    assert rescheduled["time"] == "11:00 AM"

    # 5. Cancel appointment
    cancelled = cancel_appointment("P001", appt_id)
    assert cancelled is not None
    assert cancelled["status"] == "cancelled"

def test_format_visit_history():
    history_md = format_visit_history("P001")
    assert "Nimal Perera" in history_md
    assert "Visit ID" in history_md or "Cardiology" in history_md

def test_patient_feedback():
    fb = submit_patient_feedback(
        patient_id="P001",
        rating=5,
        comment="Excellent assistant! Booked appointment in 30 seconds.",
        service_category="Appointment Booking"
    )
    assert fb is not None
    assert fb["rating"] == 5
    assert fb["patient_id"] == "P001"

    summary = get_feedback_summary()
    assert summary["count"] >= 1
    assert summary["average_rating"] >= 1.0
