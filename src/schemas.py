from typing import Literal

from pydantic import BaseModel, Field


class SupervisorDecision(BaseModel):
    """
    Structured routing decision produced by the CeylonCare Supervisor.
    """

    intent: Literal[
        "appointment",
        "knowledge",
        "triage",
        "visit_history",
        "unknown",
    ] = Field(
        description="The main intent of the user's request."
    )

    selected_agent: Literal[
        "appointment_agent",
        "knowledge_agent",
        "triage_agent",
        "visit_history_agent",
        "unknown",
    ] = Field(
        description="The specialist agent responsible for the request."
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Routing confidence between 0 and 1."
    )

    reason: str = Field(
        description="Short explanation for the routing decision."
    )


class TriageDecision(BaseModel):
    """
    Structured triage evaluation produced by the Triage Agent.
    """

    final_response: str = Field(
        description="The empathetic response to the patient."
    )

    human_escalation_required: bool = Field(
        description="True if the symptoms describe a severe or life-threatening medical emergency."
    )