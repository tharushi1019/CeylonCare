from src.graph import route_entry


def test_new_request():

    state = {
        "user_message": "I need help.",
        "intent": "",
        "selected_agent": "",
        "confidence": 0.0,
        "supervisor_reason": "",
        "final_response": "",

        "appointment_specialist": "",
        "appointment_date": "",
        "appointment_time": "",
        "appointment_confirmed": False,
    }

    result = route_entry(state)

    print("\nTEST 1 - NEW REQUEST")
    print(f"Result: {result}")

    assert result == "supervisor"


def test_active_appointment():

    state = {
        "user_message": "10 AM",
        "intent": "appointment",
        "selected_agent": "appointment_agent",
        "confidence": 1.0,
        "supervisor_reason": "",
        "final_response": "",

        "appointment_specialist": "cardiologist",
        "appointment_date": "tomorrow",
        "appointment_time": "",
        "appointment_confirmed": False,
    }

    result = route_entry(state)

    print("\nTEST 2 - ACTIVE APPOINTMENT")
    print(f"Result: {result}")

    assert result == "appointment_agent"


def test_confirmed_appointment():

    state = {
        "user_message": "I want another appointment.",
        "intent": "appointment",
        "selected_agent": "appointment_agent",
        "confidence": 1.0,
        "supervisor_reason": "",
        "final_response": "",

        "appointment_specialist": "cardiologist",
        "appointment_date": "tomorrow",
        "appointment_time": "10 AM",
        "appointment_confirmed": True,
    }

    result = route_entry(state)

    print("\nTEST 3 - CONFIRMED APPOINTMENT")
    print(f"Result: {result}")

    assert result == "supervisor"


if __name__ == "__main__":

    test_new_request()
    test_active_appointment()
    test_confirmed_appointment()

    print("\n==============================")
    print("ALL ENTRY ROUTER TESTS PASSED")
    print("==============================")