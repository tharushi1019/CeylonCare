from src.graph import build_graph


def run_test(
    graph,
    test_id,
    description,
    user_message,
    expected_intent,
    expected_agent,
    expected_text=None,
    expect_human_review=False,
):
    print("\n" + "=" * 70)
    print(f"{test_id} - {description}")
    print("=" * 70)

    initial_state = {
        "user_message": user_message,

        "intent": "",
        "selected_agent": "",
        "confidence": 0.0,
        "supervisor_reason": "",
        "final_response": "",

        "appointment_specialist": "",
        "appointment_date": "",
        "appointment_time": "",
        "appointment_confirmed": False,

        "human_escalation_required": False,
        "human_decision": "",
    }

    config = {
        "configurable": {
            "thread_id": f"evaluation-{test_id}"
        }
    }

    try:
        result = graph.invoke(
            initial_state,
            config=config
        )

        actual_intent = result["intent"]
        actual_agent = result["selected_agent"]

        # --------------------------------------------------
        # Check Human-in-the-Loop interrupt
        # --------------------------------------------------

        interrupts = result.get("__interrupt__")

        human_review_triggered = bool(interrupts)

        # Keep the original emergency response.
        response = result.get(
            "final_response",
            ""
        )

        print(f"User: {user_message}")
        print(f"Expected Intent: {expected_intent}")
        print(f"Actual Intent:   {actual_intent}")
        print(f"Expected Agent:  {expected_agent}")
        print(f"Actual Agent:    {actual_agent}")

        print(
            f"Human Review Expected: "
            f"{expect_human_review}"
        )

        print(
            f"Human Review Triggered: "
            f"{human_review_triggered}"
        )

        # --------------------------------------------------
        # Basic routing validation
        # --------------------------------------------------

        passed = (
            actual_intent == expected_intent
            and actual_agent == expected_agent
        )

        # --------------------------------------------------
        # Human escalation validation
        # --------------------------------------------------

        if expect_human_review:

            human_review_passed = (
                human_review_triggered
            )

            print(
                f"Human Review Check: "
                f"{human_review_passed}"
            )

            passed = (
                passed
                and human_review_passed
            )

        # --------------------------------------------------
        # Expected response text
        # --------------------------------------------------

        if expected_text:

            text_found = (
                expected_text.lower()
                in response.lower()
            )

            print(
                f"Expected Text:   "
                f"{expected_text}"
            )

            print(
                f"Text Found:      "
                f"{text_found}"
            )

            passed = passed and text_found

        print(f"\nResponse: {response}")

        # --------------------------------------------------
        # Show interrupt information
        # --------------------------------------------------

        if interrupts:

            print(
                "\nHuman Review Interrupt:"
            )

            print(
                interrupts[0].value
            )

        # --------------------------------------------------
        # Result
        # --------------------------------------------------

        if passed:

            print("\nRESULT: PASS")
            return True

        print("\nRESULT: FAIL")
        return False

    except Exception as e:

        print(f"\nERROR: {e}")
        print("\nRESULT: FAIL")

        return False


def main():

    print("\n" + "#" * 70)
    print("CEYLONCARE SYSTEM EVALUATION")
    print("#" * 70)

    graph = build_graph()

    results = []

    # ==================================================
    # TC01 - Clinic hours
    # ==================================================

    results.append(
        run_test(
            graph,
            "TC01",
            "Clinic opening hours",
            "What time does the CeylonCare clinic open?",
            "knowledge",
            "knowledge_agent",
            "8:00 AM",
        )
    )

    # ==================================================
    # TC02 - Saturday availability
    # ==================================================

    results.append(
        run_test(
            graph,
            "TC02",
            "Saturday availability",
            "Is the CeylonCare clinic open on Saturday?",
            "knowledge",
            "knowledge_agent",
            "not open",
        )
    )

    # ==================================================
    # TC03 - Unsupported knowledge
    # ==================================================

    results.append(
        run_test(
            graph,
            "TC03",
            "Unsupported knowledge question",
            "Does CeylonCare have an MRI machine?",
            "knowledge",
            "knowledge_agent",
            "not available",
        )
    )

    # ==================================================
    # TC04 - Appointment specialist + date
    # ==================================================

    results.append(
        run_test(
            graph,
            "TC04",
            "Appointment with specialist and date",
            "I need to book an appointment with a cardiologist tomorrow.",
            "appointment",
            "appointment_agent",
            "What time",
        )
    )

    # ==================================================
    # TC05 - Appointment missing date
    # ==================================================

    results.append(
        run_test(
            graph,
            "TC05",
            "Appointment missing date",
            "I want to book an appointment with a cardiologist.",
            "appointment",
            "appointment_agent",
            "What date",
        )
    )

    # ==================================================
    # TC06 - Appointment missing specialist
    # ==================================================

    results.append(
        run_test(
            graph,
            "TC06",
            "Appointment missing specialist",
            "I want to book an appointment tomorrow.",
            "appointment",
            "appointment_agent",
            "Which type of doctor",
        )
    )

    # ==================================================
    # TC07 - Mild symptom
    # ==================================================

    results.append(
        run_test(
            graph,
            "TC07",
            "Mild symptom assessment",
            "I have a mild headache.",
            "triage",
            "triage_agent",
            "cannot diagnose",
        )
    )

    # ==================================================
    # TC08 - Emergency symptom
    # ==================================================

    results.append(
        run_test(
            graph,
            "TC08",
            "Emergency symptom detection",
            "I have severe chest pain and difficulty breathing.",
            "triage",
            "triage_agent",
            "urgent medical attention",
            expect_human_review=True,
        )
    )

    # ==================================================
    # TC09 - Emergency priority
    # ==================================================

    results.append(
        run_test(
            graph,
            "TC09",
            "Emergency takes priority over appointment",
            "I have severe chest pain. Can I book an appointment tomorrow?",
            "triage",
            "triage_agent",
            "emergency department",
            expect_human_review=True,
        )
    )

    # ==================================================
    # TC10 - Unknown request
    # ==================================================

    results.append(
        run_test(
            graph,
            "TC10",
            "Unclear request",
            "Can you help me?",
            "unknown",
            "unknown",
            "not completely sure",
        )
    )

    # ==================================================
    # Summary
    # ==================================================

    passed = sum(results)
    total = len(results)
    failed = total - passed

    print("\n" + "#" * 70)
    print("CEYLONCARE EVALUATION SUMMARY")
    print("#" * 70)

    print(f"Total Tests : {total}")
    print(f"Passed      : {passed}")
    print(f"Failed      : {failed}")

    accuracy = (passed / total) * 100

    print(f"Accuracy    : {accuracy:.1f}%")

    if passed == total:

        print("\nOVERALL RESULT: PASS")

    else:

        print(
            "\nOVERALL RESULT: "
            "REVIEW FAILED TESTS"
        )


if __name__ == "__main__":
    main()