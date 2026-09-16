from src.graph import build_graph


def main():
    graph = build_graph()

    user_message = (
        "I want to book an appointment tomorrow."
    )

    initial_state = {
    	"user_message": user_message,
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

    result = graph.invoke(
    	initial_state,
    	config={
        	"configurable": {
            	"thread_id": "supervisor-test-1"
         	}
    	}
    )

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