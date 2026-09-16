import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from typing import TypedDict


# --------------------------------------------------
# 1. Load environment variables
# --------------------------------------------------

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY was not found.")


# --------------------------------------------------
# 2. Create Gemini model
# --------------------------------------------------

model = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash",
    google_api_key=api_key,
    temperature=0,
)


# --------------------------------------------------
# 3. Define LangGraph state
# --------------------------------------------------

class CeylonCareState(TypedDict):
    user_message: str
    intent: str
    response: str


# --------------------------------------------------
# 4. Gemini analysis node
# --------------------------------------------------

def analyze_request(state: CeylonCareState):

    print("\n[AI ANALYSIS NODE]")

    prompt = f"""
You are the intent classifier for the CeylonCare healthcare assistant.

Classify the user's request into exactly ONE of these categories:

- appointment
- knowledge
- triage
- unknown

User request:
{state["user_message"]}

Return ONLY the category name.
"""

    result = model.invoke(prompt)

    if isinstance(result.content, str):
        intent = result.content.strip().lower()
    else:
        intent = ""

        for part in result.content:
            if isinstance(part, dict) and part.get("type") == "text":
                intent = part.get("text", "").strip().lower()
                break

    allowed_intents = {
        "appointment",
        "knowledge",
        "triage",
        "unknown",
    }

    if intent not in allowed_intents:
        intent = "unknown"

    print(f"Detected intent: {intent}")

    return {
        "intent": intent
    }

# --------------------------------------------------
# 5. Response node
# --------------------------------------------------

def generate_response(state: CeylonCareState):

    print("\n[RESPONSE NODE]")

    if state["intent"] == "appointment":
        response = "Your request will be handled by the Appointment Agent."

    elif state["intent"] == "knowledge":
        response = "Your request will be handled by the Knowledge Agent."

    elif state["intent"] == "triage":
        response = "Your request will be handled by the Triage Agent."

    else:
        response = "I need more information to understand your request."

    return {
        "response": response
    }


# --------------------------------------------------
# 6. Build LangGraph
# --------------------------------------------------

builder = StateGraph(CeylonCareState)

builder.add_node("analyze_request", analyze_request)
builder.add_node("generate_response", generate_response)

builder.add_edge(START, "analyze_request")
builder.add_edge("analyze_request", "generate_response")
builder.add_edge("generate_response", END)

graph = builder.compile()


# --------------------------------------------------
# 7. Run the graph
# --------------------------------------------------

initial_state = {
    "user_message": "I need to see a heart specialist tomorrow.",
    "intent": "",
    "response": "",
}

result = graph.invoke(initial_state)


# --------------------------------------------------
# 8. Display final state
# --------------------------------------------------

print("\n[FINAL STATE]")
print(result)