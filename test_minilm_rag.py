from src.rag.minilm_knowledge_agent import (
    answer_from_minilm_knowledge_base,
)


# ============================================================
# CeylonCare MiniLM RAG Evaluation
# ============================================================


def run_test(
    test_id,
    description,
    question,
    expected_text,
):

    print("\n" + "=" * 70)
    print(f"{test_id} - {description}")
    print("=" * 70)

    print(f"Question: {question}")
    print(f"Expected text: {expected_text}")

    try:

        response = (
            answer_from_minilm_knowledge_base(
                question
            )
        )

        passed = (
            expected_text.lower()
            in response.lower()
        )

        print("\nResponse:")
        print(response)

        if passed:

            print("\nRESULT: PASS")

        else:

            print("\nRESULT: FAIL")

        return passed

    except Exception as e:

        print("\nERROR:")
        print(e)

        print("\nRESULT: FAIL")

        return False


def main():

    print("\n" + "#" * 70)
    print("CEYLONCARE MINILM RAG EVALUATION")
    print("#" * 70)

    results = []


    # --------------------------------------------------------
    # TC01 - Clinic hours
    # --------------------------------------------------------

    results.append(
        run_test(
            "TC01",
            "Clinic opening hours",
            "What time does the CeylonCare clinic open?",
            "8:00 AM",
        )
    )


    # --------------------------------------------------------
    # TC02 - Weekday closing time
    # --------------------------------------------------------

    results.append(
        run_test(
            "TC02",
            "Clinic closing time",
            "What time does the CeylonCare clinic close?",
            "5:00 PM",
        )
    )


    # --------------------------------------------------------
    # TC03 - Saturday availability
    # --------------------------------------------------------

    results.append(
        run_test(
            "TC03",
            "Saturday availability",
            "Is the CeylonCare clinic open on Saturday?",
            "Monday to Friday",
        )
    )


    # --------------------------------------------------------
    # TC04 - Unsupported information
    # --------------------------------------------------------

    results.append(
        run_test(
            "TC04",
            "Unsupported information",
            "Does CeylonCare have an MRI machine?",
            "not available",
        )
    )


    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    passed = sum(results)
    total = len(results)

    print("\n" + "#" * 70)
    print("MINILM RAG EVALUATION SUMMARY")
    print("#" * 70)

    print(f"Total Tests : {total}")
    print(f"Passed      : {passed}")
    print(f"Failed      : {total - passed}")

    accuracy = (
        passed / total
    ) * 100

    print(
        f"Accuracy    : {accuracy:.1f}%"
    )

    if passed == total:

        print(
            "\nOVERALL RESULT: PASS"
        )

    else:

        print(
            "\nOVERALL RESULT: REVIEW FAILED TESTS"
        )


if __name__ == "__main__":

    main()