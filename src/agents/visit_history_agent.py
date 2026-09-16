from ..state import CeylonCareState

from ..services.patient_service import (
    get_patient,
    get_visit_history,
)


def visit_history_agent(state: CeylonCareState):
    """
    Handles patient visit-history requests.

    This agent retrieves synthetic patient visit records
    from the CeylonCare patient-management service and
    prepares an administrative summary.

    The service contains synthetic/mock data only.
    """

    print("\n[VISIT HISTORY AGENT]")

    patient_id = state.get("patient_id", "").strip()

    # --------------------------------------------------
    # Patient ID validation
    # --------------------------------------------------

    if not patient_id:

        print(
            "[VISIT HISTORY AGENT] "
            "Patient ID is missing."
        )

        return {
            "final_response": (
                "I need a valid patient ID to retrieve "
                "the visit history."
            )
        }

    print(
        "[VISIT HISTORY AGENT] "
        f"Patient ID: {patient_id}"
    )

    # --------------------------------------------------
    # Verify patient exists
    # --------------------------------------------------

    patient = get_patient(patient_id)

    if not patient:

        print(
            "[VISIT HISTORY AGENT] "
            f"Patient {patient_id} was not found."
        )

        return {
            "final_response": (
                f"No patient record was found for "
                f"patient ID {patient_id}."
            )
        }

    # --------------------------------------------------
    # Retrieve visit history
    # --------------------------------------------------

    visits = get_visit_history(patient_id)

    if not visits:

        print(
            "[VISIT HISTORY AGENT] "
            "No visit history found."
        )

        return {
            "final_response": (
                f"No visit history is available for "
                f"patient {patient_id}."
            )
        }

    # --------------------------------------------------
    # Build administrative summary
    # --------------------------------------------------

    lines = [
        "Patient Visit History",
        "",
        f"Patient ID: {patient['patient_id']}",
        f"Patient Name: {patient['name']}",
        "",
        f"Number of recorded visits: {len(visits)}",
    ]

    for visit in visits:

        lines.extend(
            [
                "",
                f"Visit ID: {visit['visit_id']}",
                f"Date: {visit['date']}",
                f"Department: {visit['department']}",
                f"Reason: {visit['reason']}",
                f"Summary: {visit['summary']}",
                f"Outcome: {visit['outcome']}",
            ]
        )

    response = "\n".join(lines)

    print(
        "[VISIT HISTORY AGENT] "
        f"Retrieved {len(visits)} visit(s)."
    )

    return {
        "final_response": response
    }