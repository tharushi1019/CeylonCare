from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

from .state import CeylonCareState
from .supervisor import supervisor_node

from .agents.knowledge_agent import knowledge_agent
from .agents.appointment_agent import appointment_agent
from .agents.triage_agent import triage_agent
from .agents.visit_history_agent import visit_history_agent
from .agents.human_escalation_agent import human_escalation_agent


# ============================================================
# Entry Routing
# ============================================================

def route_entry(state: CeylonCareState):
    """
    Decide whether the current message is:

    1. A continuation of an active appointment conversation
    2. A new request that should go to the Supervisor
    """

    appointment_active = state.get(
        "appointment_active",
        False
    )
    user_message = state.get("user_message", "").lower()

    # Emergency safety escape: symptoms must always be prioritized over in-progress booking
    emergency_keywords = [
        "severe chest pain", "difficulty breathing", "can't breathe", "cannot breathe",
        "shortness of breath", "loss of consciousness", "unconscious", "severe bleeding",
        "emergency"
    ]
    if any(k in user_message for k in emergency_keywords):
        print("[ENTRY ROUTER] Emergency symptom detected. Prioritizing supervisor/triage.")
        return "supervisor"

    # Global reset escape
    if any(w in user_message for w in ["start over", "reset", "main menu", "menu"]):
        print("[ENTRY ROUTER] User requested session reset. Routing to supervisor.")
        return "supervisor"

    print("\n[ENTRY ROUTER]")
    print(
        f"[ENTRY ROUTER] "
        f"Appointment active: {appointment_active}"
    )

    # --------------------------------------------------------
    # Active appointment conversation
    # --------------------------------------------------------

    if appointment_active:

        print(
            "[ENTRY ROUTER] Active appointment "
            "conversation found."
        )

        print(
            "[ENTRY ROUTER] Continuing with "
            "appointment_agent."
        )

        return "appointment_agent"

    # --------------------------------------------------------
    # New request
    # --------------------------------------------------------

    print(
        "[ENTRY ROUTER] No active appointment "
        "conversation."
    )

    print(
        "[ENTRY ROUTER] Sending request to supervisor."
    )

    return "supervisor"


# ============================================================
# Supervisor Routing
# ============================================================

def route_from_supervisor(state: CeylonCareState):
    """
    Route the Supervisor decision to the appropriate
    specialist agent.
    """

    selected_agent = state.get(
        "selected_agent",
        ""
    )

    print("\n[SUPERVISOR ROUTER]")

    print(
        f"[SUPERVISOR ROUTER] "
        f"Selected agent: {selected_agent}"
    )

    # --------------------------------------------------------
    # Knowledge
    # --------------------------------------------------------

    if selected_agent == "knowledge_agent":

        print(
            "[SUPERVISOR ROUTER] "
            "Routing to knowledge_agent."
        )

        return "knowledge_agent"

    # --------------------------------------------------------
    # Appointment
    # --------------------------------------------------------

    if selected_agent == "appointment_agent":

        print(
            "[SUPERVISOR ROUTER] "
            "Routing to appointment_agent."
        )

        return "appointment_agent"

    # --------------------------------------------------------
    # Triage
    # --------------------------------------------------------

    if selected_agent == "triage_agent":

        print(
            "[SUPERVISOR ROUTER] "
            "Routing to triage_agent."
        )

        return "triage_agent"

    # --------------------------------------------------------
    # Visit History
    # --------------------------------------------------------

    if selected_agent == "visit_history_agent":

        print(
            "[SUPERVISOR ROUTER] "
            "Routing to visit_history_agent."
        )

        return "visit_history_agent"

    # --------------------------------------------------------
    # Unknown
    # --------------------------------------------------------

    print(
        "[SUPERVISOR ROUTER] "
        "Unknown or invalid agent."
    )

    print(
        "[SUPERVISOR ROUTER] "
        "Routing to unknown handler."
    )

    return "unknown"


# ============================================================
# Unknown Request Handler
# ============================================================

def unknown_agent(state: CeylonCareState):
    """
    Handles requests that cannot be reliably classified.
    """

    print("\n[UNKNOWN HANDLER]")

    return {
        "final_response": (
            "I'm not completely sure which CeylonCare "
            "service can help with your request. "
            "Could you please provide a little more "
            "information?"
        )
    }


# ============================================================
# Triage Routing
# ============================================================

def route_from_triage(state: CeylonCareState):
    """
    Decide whether a triage request requires
    human escalation.
    """

    human_escalation_required = state.get(
        "human_escalation_required",
        False
    )

    print("\n[TRIAGE ROUTER]")

    print(
        "[TRIAGE ROUTER] "
        f"Human escalation required: "
        f"{human_escalation_required}"
    )

    # --------------------------------------------------------
    # Emergency / high-risk case
    # --------------------------------------------------------

    if human_escalation_required:

        print(
            "[TRIAGE ROUTER] "
            "Emergency detected."
        )

        print(
            "[TRIAGE ROUTER] "
            "Sending to human escalation agent."
        )

        return "human_escalation_agent"

    # --------------------------------------------------------
    # Normal triage
    # --------------------------------------------------------

    print(
        "[TRIAGE ROUTER] "
        "No human escalation required."
    )

    print(
        "[TRIAGE ROUTER] "
        "Ending triage workflow."
    )

    return "end"


# ============================================================
# Build Graph
# ============================================================

def build_graph():
    """
    Build and compile the CeylonCare LangGraph workflow.
    """

    builder = StateGraph(
        CeylonCareState
    )

    # ========================================================
    # Nodes
    # ========================================================

    builder.add_node(
        "supervisor",
        supervisor_node
    )

    builder.add_node(
        "knowledge_agent",
        knowledge_agent
    )

    builder.add_node(
        "appointment_agent",
        appointment_agent
    )

    builder.add_node(
        "triage_agent",
        triage_agent
    )

    builder.add_node(
        "visit_history_agent",
        visit_history_agent
    )

    builder.add_node(
        "human_escalation_agent",
        human_escalation_agent
    )

    builder.add_node(
        "unknown",
        unknown_agent
    )

    # ========================================================
    # START → Entry Router
    # ========================================================

    builder.add_conditional_edges(
        START,
        route_entry,
        {
            "supervisor": "supervisor",
            "appointment_agent": "appointment_agent",
        }
    )

    # ========================================================
    # Supervisor → Specialist Agent
    # ========================================================

    builder.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {
            "knowledge_agent": "knowledge_agent",
            "appointment_agent": "appointment_agent",
            "triage_agent": "triage_agent",
            "visit_history_agent": "visit_history_agent",
            "unknown": "unknown",
        }
    )

    # ========================================================
    # Knowledge Agent → END
    # ========================================================

    builder.add_edge(
        "knowledge_agent",
        END
    )

    # ========================================================
    # Appointment Agent → END
    # ========================================================

    builder.add_edge(
        "appointment_agent",
        END
    )

    # ========================================================
    # Visit History Agent → END
    # ========================================================

    builder.add_edge(
        "visit_history_agent",
        END
    )

    # ========================================================
    # Triage Agent → Human Escalation / END
    # ========================================================

    builder.add_conditional_edges(
        "triage_agent",
        route_from_triage,
        {
            "human_escalation_agent":
                "human_escalation_agent",

            "end":
                END,
        }
    )

    # ========================================================
    # Human Escalation Agent → END
    # ========================================================

    builder.add_edge(
        "human_escalation_agent",
        END
    )

    # ========================================================
    # Unknown → END
    # ========================================================

    builder.add_edge(
        "unknown",
        END
    )

    # ========================================================
    # LangGraph Short-Term Memory
    # ========================================================

    checkpointer = InMemorySaver()

    graph = builder.compile(
        checkpointer=checkpointer
    )

    return graph