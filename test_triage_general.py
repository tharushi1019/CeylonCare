from src.graph import build_graph


def main():

    graph = build_graph()

    config = {
        "configurable": {
            "thread_id": "triage-general-test-001"
        }
    }

    initial_state = {
        "user_message": "I have a mild headache.",

        "intent": "",
        "selected_agent": "",
        "confidence": 0.0,
        "supervisor_reason": "",
        "final_response": "",

        "appointment_specialist": "",
        "appointment_date": "",
        "appointment_time": "",
        "appointment_confirmed": False,

        "human_escalation_required": False,
        "human_decision": "",
    }

    result = graph.invoke(
        initial_state,
        config
    )

    print("\n==============================")
    print("GENERAL TRIAGE TEST")
    print("==============================")

    print(f"Intent: {result['intent']}")
    print(f"Agent: {result['selected_agent']}")
    print(
        f"Human Escalation Required: "
        f"{result['human_escalation_required']}"
    )
    print(f"Final Response: {result['final_response']}")


if __name__ == "__main__":
    main()