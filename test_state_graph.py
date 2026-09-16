from typing import TypedDict

from langgraph.graph import StateGraph, START, END


# --------------------------------------------------
# 1. Define the shared state
# --------------------------------------------------

class CeylonCareState(TypedDict):
    user_message: str
    intent: str
    response: str


# --------------------------------------------------
# 2. First node: analyze the request
# --------------------------------------------------

def analyze_request(state: CeylonCareState):
    print("\n[ANALYZE NODE]")

    message = state["user_message"].lower()

    if "appointment" in message or "book" in message:
        intent = "appointment"
    elif "doctor" in message or "clinic" in message:
        intent = "knowledge"
    else:
        intent = "unknown"

    print(f"Detected intent: {intent}")

    return {
        "intent": intent
    }


# --------------------------------------------------
# 3. Second node: generate a simple response
# --------------------------------------------------

def generate_response(state: CeylonCareState):
    print("\n[RESPONSE NODE]")

    if state["intent"] == "appointment":
        response = "I can help you with an appointment."
    elif state["intent"] == "knowledge":
        response = "I can help you with clinic information."
    else:
        response = "I need more information to help you."

    return {
        "response": response
    }


# --------------------------------------------------
# 4. Build the LangGraph
# --------------------------------------------------

builder = StateGraph(CeylonCareState)

builder.add_node("analyze_request", analyze_request)
builder.add_node("generate_response", generate_response)

builder.add_edge(START, "analyze_request")
builder.add_edge("analyze_request", "generate_response")
builder.add_edge("generate_response", END)

graph = builder.compile()


# --------------------------------------------------
# 5. Run the graph
# --------------------------------------------------

initial_state = {
    "user_message": "I want to book an appointment with a cardiologist.",
    "intent": "",
    "response": "",
}

result = graph.invoke(initial_state)


# --------------------------------------------------
# 6. Display the final state
# --------------------------------------------------

print("\n[FINAL STATE]")
print(result)