from src.agents.knowledge_agent import knowledge_agent


def main():

    state = {
        "user_message": "What time does the CeylonCare clinic open?",
        "intent": "knowledge",
        "selected_agent": "knowledge_agent",
        "confidence": 1.0,
        "supervisor_reason": "",
        "final_response": "",
    }

    result = knowledge_agent(state)

    print("\n==============================")
    print("KNOWLEDGE AGENT RESULT")
    print("==============================")

    print(
        f"Final Response: {result['final_response']}"
    )


if __name__ == "__main__":
    main()