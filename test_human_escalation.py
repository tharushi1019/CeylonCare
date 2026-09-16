from langgraph.types import Command

from src.graph import build_graph


def main():

    graph = build_graph()

    config = {
        "configurable": {
            "thread_id": "human-review-test-001"
        }
    }

    initial_state = {
        "user_message": "I have severe chest pain and difficulty breathing.",

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

    print("\n==============================")
    print("HUMAN ESCALATION TEST")
    print("==============================")

    result = graph.invoke(
        initial_state,
        config
    )

    print("\n[GRAPH PAUSED FOR HUMAN REVIEW]")

    print(result)

    print("\n==============================")
    print("RESUMING WITH HUMAN DECISION")
    print("==============================")

    result = graph.invoke(
        Command(
            resume="Approved for emergency escalation."
        ),
        config
    )

    print("\n[GRAPH COMPLETED]")

    print(f"Human Decision: {result['human_decision']}")
    print(f"Final Response: {result['final_response']}")


if __name__ == "__main__":
    main()