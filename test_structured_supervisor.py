import os
from typing import Literal

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI


# --------------------------------------------------
# 1. Load environment variables
# --------------------------------------------------

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY was not found.")


# --------------------------------------------------
# 2. Define the Supervisor decision schema
# --------------------------------------------------

class SupervisorDecision(BaseModel):
    intent: Literal[
        "appointment",
        "knowledge",
        "triage",
        "unknown"
    ] = Field(
        description="The user's main intent."
    )

    selected_agent: Literal[
        "appointment_agent",
        "knowledge_agent",
        "triage_agent",
        "unknown"
    ] = Field(
        description="The specialist agent that should handle the request."
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence in the routing decision, from 0 to 1."
    )

    reason: str = Field(
        description="Short explanation for why this agent was selected."
    )


# --------------------------------------------------
# 3. Create Gemini model
# --------------------------------------------------

model = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash",
    google_api_key=api_key,
    temperature=0,
)


# --------------------------------------------------
# 4. Create structured-output model
# --------------------------------------------------

structured_model = model.with_structured_output(
    SupervisorDecision
)


# --------------------------------------------------
# 5. Test a user request
# --------------------------------------------------

user_message = (
    "I need to book an appointment with a cardiologist tomorrow."
)

prompt = f"""
You are the Supervisor Agent for CeylonCare.

Your job is to understand the user's request and decide
which specialist agent should handle it.

Available specialist agents:

1. appointment_agent
   - appointment booking
   - appointment availability
   - appointment cancellation
   - appointment rescheduling

2. knowledge_agent
   - clinic information
   - doctor information
   - general healthcare information

3. triage_agent
   - symptom assessment
   - urgency assessment
   - emergency-related guidance

4. unknown
   - use when the request cannot be classified reliably

User request:
{user_message}

Return the appropriate structured Supervisor decision.
"""

decision = structured_model.invoke(prompt)


# --------------------------------------------------
# 6. Display the result
# --------------------------------------------------

print("\n[SUPERVISOR DECISION]")

print(f"Intent: {decision.intent}")
print(f"Selected Agent: {decision.selected_agent}")
print(f"Confidence: {decision.confidence}")
print(f"Reason: {decision.reason}")

print("\n[PYDANTIC OBJECT]")
print(decision)