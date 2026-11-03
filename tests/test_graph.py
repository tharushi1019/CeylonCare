"""
Unit Tests for CeylonCare Multi-Agent Graph and State Architecture.
"""
import pytest
from src.state import CeylonCareState
from src.graph import route_entry, route_from_supervisor, route_from_triage, build_graph
from src.agents.visit_history_agent import visit_history_agent

def test_entry_routing_emergency():
    # If emergency symptoms are mentioned, entry router must send to supervisor/triage immediately
    state: CeylonCareState = {
        "user_message": "Patient is having severe chest pain and cannot breathe",
        "appointment_active": True  # even if an appointment was previously in progress
    }
    destination = route_entry(state)
    assert destination == "supervisor"

def test_entry_routing_active_appointment():
    state: CeylonCareState = {
        "user_message": "Tomorrow at 10 AM",
        "appointment_active": True
    }
    destination = route_entry(state)
    assert destination == "appointment_agent"

def test_entry_routing_new_session():
    state: CeylonCareState = {
        "user_message": "What are your OPD hours in Colombo?",
        "appointment_active": False
    }
    destination = route_entry(state)
    assert destination == "supervisor"

def test_supervisor_routing():
    assert route_from_supervisor({"selected_agent": "knowledge_agent"}) == "knowledge_agent"
    assert route_from_supervisor({"selected_agent": "appointment_agent"}) == "appointment_agent"
    assert route_from_supervisor({"selected_agent": "triage_agent"}) == "triage_agent"
    assert route_from_supervisor({"selected_agent": "visit_history_agent"}) == "visit_history_agent"
    assert route_from_supervisor({"selected_agent": "other"}) == "unknown"

def test_triage_routing():
    assert route_from_triage({"human_escalation_required": True}) == "human_escalation_agent"
    assert route_from_triage({"human_escalation_required": False}) == "end"

def test_visit_history_agent():
    state: CeylonCareState = {
        "patient_id": "P001",
        "user_message": "Show me my visit history"
    }
    result = visit_history_agent(state)
    assert "final_response" in result
    assert "Nimal Perera" in result["final_response"]

def test_graph_build():
    graph = build_graph()
    assert graph is not None
    # Verify graph contains core nodes
    nodes = graph.nodes
    assert "supervisor" in nodes
    assert "knowledge_agent" in nodes
    assert "appointment_agent" in nodes
    assert "triage_agent" in nodes
    assert "visit_history_agent" in nodes
    assert "human_escalation_agent" in nodes

