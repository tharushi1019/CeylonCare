from src.graph import build_graph


def main():
    graph = build_graph()

    user_message = (
        "I have severe chest pain and difficulty breathing."
    )

    initial_state = {
        "user_message": user_message,
        "intent": "",
        "selected_agent": "",
        "confidence": 0.0,
        "supervisor_reason": "",
        "final_response": "",
    }

    result = graph.invoke(initial_state)

    print("\n==============================")
    print("CEYLONCARE SUPERVISOR RESULT")
    print("==============================")

    print(f"User: {result['user_message']}")
    print(f"Intent: {result['intent']}")
    print(f"Agent: {result['selected_agent']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Reason: {result['supervisor_reason']}")
    print(f"Final Response: {result['final_response']}")


if __name__ == "__main__":
    main()