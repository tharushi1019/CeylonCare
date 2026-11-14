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
Your role is to help patients book, reschedule, or cancel doctor appointments.

Instructions:
1. Review the conversation history.
2. If the user wants to book an appointment, you must gather:
   - The specialist or doctor name (e.g. Dr. K. Perera, Cardiologist)
   - The preferred date (e.g. 2026-11-15, or convert 'tomorrow' into an explicit YYYY-MM-DD date)
   - The preferred time (e.g. 10:00 AM, 10:30 AM)
3. If any detail is missing, ask the user politely and specify what is needed.
4. If you have the specialist/doctor, date, and time:
   - Call the `create_appointment_tool` with:
     * patient_id: '{patient_id}'
     * specialist: doctor name or specialty
     * appointment_date: YYYY-MM-DD
     * appointment_time: e.g. '10:30 AM'
5. When `create_appointment_tool` succeeds:
   - Celebrate and confirm the booking clearly:
     * State that the appointment is CONFIRMED.
     * State the Doctor, Date, Time, and the Appointment ID (e.g. APT-1002).
     * Explicitly inform the patient: "You can view and manage your confirmed appointment anytime under the 'My Health Records & Appointments' tab."
6. If a slot conflict occurs, politely notify the patient that this slot is already taken and suggest an alternate time.
7. If the user wants to cancel or reschedule, ask for the Appointment ID if not provided, or call `get_patient_appointments_tool` to list their bookings.

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
    appointment_created = False

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
                if "patient_id" not in tool_args or not tool_args["patient_id"]:
                    tool_args["patient_id"] = patient_id
                    
                selected_tool = tool_map[tool_name]
                result = selected_tool.invoke(tool_args)
                tool_results.append(f"Tool {tool_name} result: {json.dumps(result)}")

                if tool_name == "create_appointment_tool" and result.get("success"):
                    appointment_created = True
            
            # Step 3: Pass tool results back to LLM to get a final conversational response
            followup_prompt = prompt + "\n\nTool Results:\n" + "\n".join(tool_results) + "\n\nPlease summarize the result for the patient. Ensure you mention that they can view the booking in their 'My Health Records & Appointments' tab."
            final_response = llm.invoke(followup_prompt).content
            
        else:
            # LLM just wants to talk (e.g. asking for a date or time)
            final_response = response.content
            
    except Exception as e:
        print(f"[APPOINTMENT ERROR] {e}")
        final_response = "I encountered an error while processing your appointment request. Please try again."

    # Normalize unicode non-breaking spaces in response
    if isinstance(final_response, str):
        final_response = final_response.replace("\u202f", " ").replace("\xa0", " ")

    # Active conversation continues if appointment is still being negotiated
    still_active = not appointment_created

    return {
        "final_response": final_response,
        "appointment_active": still_active,
    }
