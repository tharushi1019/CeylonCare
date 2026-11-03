from ..state import CeylonCareState
from ..utils.llm_factory import get_llm
from ..schemas import TriageDecision

_structured_model = None

def _get_structured_model():
    global _structured_model
    if _structured_model is None:
        llm = get_llm(temperature=0)
        _structured_model = llm.with_structured_output(TriageDecision)
    return _structured_model

TRIAGE_PROMPT = """
You are the CeylonCare Triage Agent. Your role is to empathetically evaluate a patient's symptoms and determine if they require emergency medical attention.

Instructions:
1. Review the conversation history and the patient's latest message.
2. Ask clarifying questions if the symptom description is too vague (e.g. "How long has this been happening?").
3. Determine if the symptoms represent a medical emergency (e.g. severe chest pain, difficulty breathing, severe bleeding, loss of consciousness).
4. If it is an emergency, set `human_escalation_required` to true and instruct the patient to seek immediate medical care.
5. If it is not an emergency, provide empathetic guidance, recommend seeing a doctor, but DO NOT diagnose the condition.
6. Always format your output using the TriageDecision schema.

Conversation History:
{chat_history}

Patient's latest message:
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


def triage_agent(state: CeylonCareState):
    print("\n[TRIAGE AGENT]")

    user_message = state.get("user_message", "")
    chat_history = state.get("chat_history", [])

    prompt = TRIAGE_PROMPT.format(
        chat_history=format_history(chat_history),
        user_message=user_message
    )

    try:
        structured_model = _get_structured_model()
        decision = structured_model.invoke(prompt)
        
        response = decision.final_response
        is_emergency = decision.human_escalation_required
        
        print(f"[TRIAGE LEVEL] {'EMERGENCY' if is_emergency else 'GENERAL'}")
        
    except Exception as e:
        print(f"[TRIAGE ERROR] {e}")
        response = (
            "I can help identify the urgency of your symptoms, "
            "but I cannot diagnose a medical condition. "
            "Please provide more details about your symptoms. "
            "If your symptoms are severe or rapidly worsening, seek "
            "immediate medical attention."
        )
        is_emergency = False

    return {
        "final_response": response,
        "human_escalation_required": is_emergency,
    }
