"""
Unit Tests for LangChain Tools in CeylonCare.
Validates input checking, error handling, and tool execution.
"""
import pytest
from src.tools.patient_tools import (
    get_patient_tool,
    get_patient_appointments_tool,
    create_appointment_tool,
    cancel_appointment_tool,
    reschedule_appointment_tool,
)

def test_get_patient_tool_valid():
    result = get_patient_tool.invoke({"patient_id": "P001"})
    assert result["success"] is True
    assert result["patient"]["patient_id"] == "P001"
    assert result["patient"]["name"] == "Nimal Perera"

def test_get_patient_tool_invalid():
    result = get_patient_tool.invoke({"patient_id": "INVALID_999"})
    assert result["success"] is False
    assert "error" in result

def test_get_patient_tool_empty():
    result = get_patient_tool.invoke({"patient_id": ""})
    assert result["success"] is False

def test_patient_appointments_tool():
    result = get_patient_appointments_tool.invoke({"patient_id": "P001"})
    assert result["success"] is True
    assert "appointments" in result
    assert isinstance(result["appointments"], list)

def test_create_and_cancel_appointment_tool():
    create_res = create_appointment_tool.invoke({
        "patient_id": "P002",
        "specialist": "Dermatologist",
        "appointment_date": "2026-12-01",
        "appointment_time": "02:00 PM"
    })
    assert create_res["success"] is True
    assert "appointment" in create_res
    appt_id = create_res["appointment"]["appointment_id"]

    cancel_res = cancel_appointment_tool.invoke({
        "patient_id": "P002",
        "appointment_id": appt_id
    })
    assert cancel_res["success"] is True

