from typing import TypedDict
from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    message: str


def test_node(state: State):
    print("LangGraph node is running!")
    return {
        "message": "CeylonCare LangGraph is working!"
    }


builder = StateGraph(State)

builder.add_node("test", test_node)

builder.add_edge(START, "test")
builder.add_edge("test", END)

graph = builder.compile()

result = graph.invoke({
    "message": "Hello CeylonCare"
})

print("Result:", result)