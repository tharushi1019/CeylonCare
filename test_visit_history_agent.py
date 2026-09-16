from src.agents.visit_history_agent import visit_history_agent


def test_valid_patient():
    """Verify visit history is returned for a valid patient."""

    state = {
        "patient_id": "P001",
        "user_message": "Please show me my visit history.",
    }

    result = visit_history_agent(state)

    assert "Patient Visit History" in result["final_response"]
    assert "Patient ID: P001" in result["final_response"]
    assert "Patient Name: Nimal Perera" in result["final_response"]
    assert "VIS-0001" in result["final_response"]

    print("TEST 1 - Valid patient: PASS")


def test_missing_patient_id():
    """Verify missing patient ID is handled safely."""

    state = {
        "patient_id": "",
        "user_message": "Please show me my visit history.",
    }

    result = visit_history_agent(state)

    assert (
        result["final_response"]
        == "I need a valid patient ID to retrieve the visit history."
    )

    print("TEST 2 - Missing patient ID: PASS")


def test_invalid_patient_id():
    """Verify an unknown patient ID does not expose records."""

    state = {
        "patient_id": "P999",
        "user_message": "Please show me my visit history.",
    }

    result = visit_history_agent(state)

    assert (
        result["final_response"]
        == "No patient record was found for patient ID P999."
    )

    print("TEST 3 - Invalid patient ID: PASS")


def main():
    print("\n========================================")
    print("CEYLONCARE VISIT HISTORY AGENT TEST")
    print("========================================")

    test_valid_patient()
    test_missing_patient_id()
    test_invalid_patient_id()

    print("\n========================================")
    print("ALL VISIT HISTORY TESTS: PASS")
    print("========================================")


if __name__ == "__main__":
    main()