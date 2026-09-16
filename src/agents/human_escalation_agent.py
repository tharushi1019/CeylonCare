from langgraph.types import interrupt

from ..state import CeylonCareState


def human_escalation_agent(state: CeylonCareState):
    """
    Pauses the CeylonCare workflow and requests
    a human decision for high-risk cases.
    """

    print("\n[HUMAN ESCALATION AGENT]")
    print("[HUMAN ESCALATION] Requesting human review.")

    decision = interrupt(
        {
            "type": "human_review",
            "message": (
                "A high-risk medical request requires human review. "
                "Please decide how the request should proceed."
            ),
            "user_message": state["user_message"],
        }
    )

    print(f"[HUMAN ESCALATION] Human decision: {decision}")

    return {
        "human_escalation_required": True,
        "human_decision": str(decision),
        "final_response": (
            "Your request has been reviewed by a human operator. "
            f"Decision: {decision}"
        ),
    }