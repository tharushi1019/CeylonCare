import os
from dotenv import load_dotenv

from .utils.llm_factory import get_llm
from .schemas import SupervisorDecision
from .state import CeylonCareState

load_dotenv()

_structured_model = None

def _get_structured_model():
    global _structured_model
    if _structured_model is None:
        model = get_llm(temperature=0)
        try:
            _structured_model = model.with_structured_output(SupervisorDecision)
        except Exception as e:
            print(f"[SUPERVISOR] Structured model binding warning: {e}")
            _structured_model = model
    return _structured_model

# ============================================================
# Supervisor Prompt
# ============================================================

SUPERVISOR_PROMPT = """
You are the Supervisor Agent for CeylonCare.

Your responsibility is to understand the user's request
and route it to the correct specialist agent.

Available agents:

1. appointment_agent
   Handles:
   - appointment booking
   - appointment availability
   - appointment cancellation
   - appointment rescheduling

2. knowledge_agent
   Handles:
   - clinic information
   - doctor information
   - healthcare information
   - general non-emergency questions

3. triage_agent
   Handles:
   - symptom assessment
   - urgency assessment
   - emergency-related requests

4. visit_history_agent
   Handles:
   - patient visit history
   - previous visit information
   - administrative visit summaries

5. unknown
   Use when the request cannot be reliably classified.

Important:

- Do not provide medical diagnosis.
- Do not invent information.
- Choose only one specialist agent.
- Return a structured routing decision.
"""


# ============================================================
# Supervisor Node
# ============================================================

def supervisor_node(state: CeylonCareState):
    """
    Analyze the user's request and determine
    which CeylonCare specialist agent should handle it.
    """

    user_message = state["user_message"]

    prompt = f"""
{SUPERVISOR_PROMPT}

User request:
{user_message}
"""

    structured_model = _get_structured_model()
    decision = structured_model.invoke(prompt)

    print("\n[SUPERVISOR NODE]")
    print(f"Intent: {decision.intent}")
    print(f"Selected Agent: {decision.selected_agent}")
    print(f"Confidence: {decision.confidence}")
    print(f"Reason: {decision.reason}")

    # ========================================================
    # Supervisor Guardrail
    # ========================================================

    intent = decision.intent
    selected_agent = decision.selected_agent
    confidence = decision.confidence
    reason = decision.reason

    # If confidence is too low, use the safe unknown route
    if confidence < 0.7:
        intent = "unknown"
        selected_agent = "unknown"

    # Ensure unknown intent always goes to unknown agent
    elif intent == "unknown":
        selected_agent = "unknown"

    # Ensure valid intent-agent combinations
    elif intent == "appointment":
        selected_agent = "appointment_agent"

    elif intent == "knowledge":
        selected_agent = "knowledge_agent"

    elif intent == "triage":
        selected_agent = "triage_agent"

    elif intent == "visit_history":
        selected_agent = "visit_history_agent"

    # Any unexpected intent goes to unknown
    else:
        intent = "unknown"
        selected_agent = "unknown"

    print("\n[SUPERVISOR GUARDRAIL]")
    print(f"Validated Intent: {intent}")
    print(f"Validated Agent: {selected_agent}")
    print(f"Validated Confidence: {confidence}")

    return {
        "intent": intent,
        "selected_agent": selected_agent,
        "confidence": confidence,
        "supervisor_reason": reason,
    }
