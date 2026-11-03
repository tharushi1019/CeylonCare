import json
from ..state import CeylonCareState
from ..utils.llm_factory import get_llm

from ..tools.patient_tools import (
    create_appointment_tool,
    cancel_appointment_tool,
    reschedule_appointment_tool,
    get_patient_appointments_tool,
)

tools = [
    create_appointment_tool,
    cancel_appointment_tool,
    reschedule_appointment_tool,
    get_patient_appointments_tool
]

_llm = None
_llm_with_tools = None

def _get_llm_and_tools():
    global _llm, _llm_with_tools
    if _llm is None:
        _llm = get_llm(temperature=0)
        _llm_with_tools = _llm.bind_tools(tools)
    return _llm, _llm_with_tools


APPOINTMENT_PROMPT = """
You are the CeylonCare Appointment Agent.
Your role is to help patients book, reschedule, or cancel appointments.

Instructions:
1. Review the conversation history.
2. If the user wants to book an appointment, you must gather:
   - The specialist they want to see (e.g., Cardiologist, Dermatologist, or a specific doctor name like Dr. Perera)
   - The preferred date (e.g., YYYY-MM-DD or 'tomorrow')
   - The preferred time (e.g., 10:00 AM)
3. If information is missing, ask the user conversationally.
4. If all information is gathered, call the `create_appointment_tool`.
5. If the user wants to cancel or reschedule, ask for the Appointment ID if they haven't provided it, or use `get_patient_appointments_tool` to find their upcoming appointments and present them to the user. Then call the appropriate tool.
6. When a tool returns a result, inform the user conversationally (e.g. "Your appointment has been booked! Your ID is APT-1002.").

Patient ID: {patient_id}

Conversation History:
{chat_history}

Latest Message:
{user_message}
"""

def format_history(chat_history):
    if not chat_history:
        return "No prior conversation."
    
    formatted = []
    for msg in chat_history:
        role = "Patient" if msg.get("role") == "user" else "Assistant"
        content = msg.get("content", "")
        formatted.append(f"{role}: {content}")
    
    return "\n".join(formatted)


def appointment_agent(state: CeylonCareState):
    print("\n[APPOINTMENT AGENT]")

    user_message = state.get("user_message", "")
    chat_history = state.get("chat_history", [])
    patient_id = state.get("patient_id", "")

    prompt = APPOINTMENT_PROMPT.format(
        patient_id=patient_id,
        chat_history=format_history(chat_history),
        user_message=user_message
    )

    llm, llm_with_tools = _get_llm_and_tools()

    try:
        # Step 1: Let the LLM decide what to do (ask question or call tool)
        response = llm_with_tools.invoke(prompt)
        
        # Step 2: Handle Tool Calls if the LLM decided to invoke one
        if response.tool_calls:
            print(f"[APPOINTMENT AGENT] Executing {len(response.tool_calls)} tool calls...")
            
            tool_results = []
            tool_map = {t.name: t for t in tools}
            
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                
                print(f"[APPOINTMENT AGENT] Calling tool: {tool_name} with {tool_args}")
                
                # Make sure patient_id is passed if required
                if "patient_id" not in tool_args:
                    tool_args["patient_id"] = patient_id
                    
                selected_tool = tool_map[tool_name]
                result = selected_tool.invoke(tool_args)
                tool_results.append(f"Tool {tool_name} result: {json.dumps(result)}")
            
            # Step 3: Pass tool results back to LLM to get a final conversational response
            followup_prompt = prompt + "\n\nTool Results:\n" + "\n".join(tool_results) + "\n\nPlease summarize the result for the patient."
            final_response = llm.invoke(followup_prompt).content
            
        else:
            # LLM just wants to talk (e.g. asking for a date)
            final_response = response.content
            
    except Exception as e:
        print(f"[APPOINTMENT ERROR] {e}")
        final_response = "I encountered an error while processing your appointment request. Please try again."

    return {
        "final_response": final_response,
    }
