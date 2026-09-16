from src.agents.appointment_agent import appointment_agent


def main():

    # --------------------------------------------------
    # Message 1
    # --------------------------------------------------

    state = {
        "user_message":
            "I need to book an appointment with a cardiologist tomorrow.",

        "intent": "appointment",
        "selected_agent": "appointment_agent",
        "confidence": 1.0,
        "supervisor_reason": "",
        "final_response": "",

        "appointment_specialist": "",
        "appointment_date": "",
        "appointment_time": "",
        "appointment_confirmed": False,
    }

    print("\n==============================")
    print("MESSAGE 1")
    print("==============================")

    result = appointment_agent(state)

    print("\nResponse:")
    print(result["final_response"])

    # Update state with returned values
    state.update(result)

    # --------------------------------------------------
    # Message 2
    # --------------------------------------------------

    state["user_message"] = "10 AM"

    print("\n==============================")
    print("MESSAGE 2")
    print("==============================")

    result = appointment_agent(state)

    print("\nResponse:")
    print(result["final_response"])

    state.update(result)

    # --------------------------------------------------
    # Message 3
    # --------------------------------------------------

    state["user_message"] = "Yes, confirm it."

    print("\n==============================")
    print("MESSAGE 3")
    print("==============================")

    result = appointment_agent(state)

    print("\nResponse:")
    print(result["final_response"])

    state.update(result)

    # --------------------------------------------------
    # Final state
    # --------------------------------------------------

    print("\n==============================")
    print("FINAL APPOINTMENT STATE")
    print("==============================")

    print(f"Specialist: {state['appointment_specialist']}")
    print(f"Date: {state['appointment_date']}")
    print(f"Time: {state['appointment_time']}")
    print(f"Confirmed: {state['appointment_confirmed']}")


if __name__ == "__main__":
    main()