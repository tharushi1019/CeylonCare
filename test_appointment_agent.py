from src.agents.appointment_agent import appointment_agent


def main():

    state = {
        "user_message": (
            "I need to book an appointment "
            "with a cardiologist tomorrow."
        ),
        "intent": "appointment",
        "selected_agent": "appointment_agent",
        "confidence": 1.0,
        "supervisor_reason": "",
        "final_response": "",
    }

    result = appointment_agent(state)

    print("\n==============================")
    print("CEYLONCARE APPOINTMENT TEST")
    print("==============================")

    print(f"User: {state['user_message']}")
    print(f"Response: {result['final_response']}")


if __name__ == "__main__":
    main()