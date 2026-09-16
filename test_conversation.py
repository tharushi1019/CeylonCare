from src.graph import build_graph


def print_result(title, result):

    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

    print(f"User: {result['user_message']}")
    print(f"Intent: {result['intent']}")
    print(f"Agent: {result['selected_agent']}")
    print(f"Response: {result['final_response']}")

    print("\nAppointment State:")
    print(
        f"  Specialist: "
        f"{result.get('appointment_specialist', '')}"
    )
    print(
        f"  Date: "
        f"{result.get('appointment_date', '')}"
    )
    print(
        f"  Time: "
        f"{result.get('appointment_time', '')}"
    )
    print(
        f"  Confirmed: "
        f"{result.get('appointment_confirmed', False)}"
    )


def main():

    # --------------------------------------------------
    # Create graph
    # --------------------------------------------------

    graph = build_graph()

    # --------------------------------------------------
    # Same thread = same conversation
    # --------------------------------------------------

    config = {
        "configurable": {
            "thread_id": "ceyloncare_demo_001"
        }
    }

    # --------------------------------------------------
    # Message 1
    # --------------------------------------------------

    state_1 = {
        "user_message":
            "I need to book an appointment "
            "with a cardiologist tomorrow.",

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

    result_1 = graph.invoke(
        state_1,
        config
    )

    print_result(
        "MESSAGE 1",
        result_1
    )

    # --------------------------------------------------
    # Message 2
    # --------------------------------------------------

    state_2 = {
        "user_message": "10 AM"
    }

    result_2 = graph.invoke(
        state_2,
        config
    )

    print_result(
        "MESSAGE 2",
        result_2
    )

    # --------------------------------------------------
    # Message 3
    # --------------------------------------------------

    state_3 = {
        "user_message": "Yes, confirm it."
    }

    result_3 = graph.invoke(
        state_3,
        config
    )

    print_result(
        "MESSAGE 3",
        result_3
    )


if __name__ == "__main__":
    main()