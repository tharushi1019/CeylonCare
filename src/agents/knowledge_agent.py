import re
import html

from ..state import CeylonCareState

# ============================================================
# WHO ICD-11 Tool
# ============================================================

from ..tools.icd11_tool import (
    icd11_search_tool,
)

# ============================================================
# Primary RAG
# ============================================================

from ..rag.minilm_knowledge_agent import (
    answer_from_minilm_knowledge_base,
)

# ============================================================
# Existing Gemini RAG fallback
#
# IMPORTANT:
# We keep the original implementation available.
# If MiniLM RAG encounters an unexpected error,
# CeylonCare can fall back to the previous RAG system.
# ============================================================

from ..rag.knowledge_retriever import (
    answer_from_knowledge_base,
)

def extract_icd11_term(question: str) -> str:
    """
    Extract the medical term from an ICD-11 reference question.
    """

    question_clean = question.strip().rstrip("?.!")

    patterns = [
        r"\bfor\s+(.+)$",
        r"\bof\s+(.+)$",
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            question_clean,
            re.IGNORECASE
        )

        if match:
            return match.group(1).strip()

    return question_clean

# ============================================================
# CeylonCare Knowledge Agent
# ============================================================

def knowledge_agent(
    state: CeylonCareState
):
    """
    Handles general CeylonCare information requests.

    Primary system:
        all-MiniLM-L6-v2
        +
        ChromaDB
        +
        grounded Gemini generation

    WHO reference:
        WHO ICD-11 LangChain tool

    Fallback system:
        Original Gemini embedding RAG
    """

    print("\n[KNOWLEDGE AGENT]")

    # --------------------------------------------------------
    # Get user's question
    # --------------------------------------------------------

    question = state["user_message"]

    print(
        f"[KNOWLEDGE AGENT] Question: {question}"
    )

    # --------------------------------------------------------
    # WHO ICD-11 Tool
    # --------------------------------------------------------

    question_lower = question.lower()

    icd11_keywords = [
        "icd-11",
        "icd11",
        "icd 11",
        "who icd",
        "icd code",
        "icd classification",
    ]

    is_icd11_question = any(
        keyword in question_lower
        for keyword in icd11_keywords
    )

    if is_icd11_question:

        print(
            "[KNOWLEDGE AGENT] "
            "ICD-11 reference question detected."
        )

        try:

            icd11_term = extract_icd11_term(
                question
            )

            print(
                f"[KNOWLEDGE AGENT] "
                f"Extracted ICD-11 term: {icd11_term}"
            )

            result = icd11_search_tool.invoke(
                {
                    "term": icd11_term
                }
            )

            title = result.get("title")
            code = result.get("code")
            browser_url = result.get("browser_url")
            found = result.get("found", False)

            # --------------------------------------------------------
            # Clean WHO HTML highlighting
            # --------------------------------------------------------

            if title:
                title = re.sub(
                    r"<[^>]+>",
                    "",
                    title
                )

                title = html.unescape(title)

            # --------------------------------------------------------
            # Build clean response
            # --------------------------------------------------------

            if not found:

                return {
                    "final_response": (
                        f"No WHO ICD-11 reference was found "
                        f"for '{icd11_term}'."
                    )
                }

            response_parts = [
                "According to the WHO ICD-11 reference:"
            ]

            if title:
                response_parts.append(
                    f"Term: {title}"
                )

            if code:
                response_parts.append(
                    f"ICD-11 Code: {code}"
                )

            if browser_url:
                response_parts.append(
                    f"Reference: {browser_url}"
                )

            response_parts.append(
                "\nThis reference information does not "
                "constitute a medical diagnosis."
            )

            return {
                "final_response": "\n".join(
                    response_parts
                )
            }

        except Exception as e:

            print(
                "[KNOWLEDGE AGENT] "
                f"WHO ICD-11 tool failed: {e}"
            )

            return {
                "final_response": (
                    "I was unable to retrieve the "
                    "WHO ICD-11 reference at this time."
                )
            }

    # --------------------------------------------------------
    # Primary: MiniLM RAG
    # --------------------------------------------------------

    try:

        print(
            "[KNOWLEDGE AGENT] "
            "Using MiniLM RAG."
        )

        answer = (
            answer_from_minilm_knowledge_base(
                question
            )
        )

        print(
            "[KNOWLEDGE AGENT] "
            "MiniLM RAG completed successfully."
        )

        return {
            "final_response": answer
        }

    # --------------------------------------------------------
    # Fallback: Existing Gemini RAG
    # --------------------------------------------------------

    except Exception as e:

        print(
            "[KNOWLEDGE AGENT] "
            "MiniLM RAG failed."
        )

        print(
            f"[KNOWLEDGE AGENT] Error: {e}"
        )

        print(
            "[KNOWLEDGE AGENT] "
            "Falling back to existing Gemini RAG."
        )

        try:

            answer = (
                answer_from_knowledge_base(
                    question
                )
            )

            return {
                "final_response": answer
            }

        except Exception as fallback_error:

            print(
                "[KNOWLEDGE AGENT] "
                "Fallback RAG also failed."
            )

            print(
                f"[KNOWLEDGE AGENT] "
                f"Fallback error: {fallback_error}"
            )

            return {
                "final_response": (
                    "Sorry, I am currently unable "
                    "to retrieve the requested "
                    "CeylonCare information."
                )
            }