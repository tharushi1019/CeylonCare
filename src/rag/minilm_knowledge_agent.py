from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI

from src.rag.minilm_knowledge_retriever import (
    retrieve_from_minilm_knowledge_base,
)


# ============================================================
# CeylonCare MiniLM RAG Knowledge Agent
#
# This is an independent test version.
#
# It uses:
#   all-MiniLM-L6-v2 -> ChromaDB -> Gemini LLM
#
# It does NOT modify the existing Knowledge Agent.
# ============================================================


load_dotenv()


from src.utils.llm_factory import get_llm

llm = get_llm(temperature=0)


# ============================================================
# Extract Gemini response text safely
# ============================================================

def extract_response_text(response):

    if isinstance(response.content, list):

        answer_parts = []

        for block in response.content:

            if (
                isinstance(block, dict)
                and block.get("type") == "text"
            ):

                answer_parts.append(
                    block.get("text", "")
                )

        return "\n".join(
            answer_parts
        ).strip()

    return str(
        response.content
    ).strip()


# ============================================================
# Main MiniLM RAG function
# ============================================================

def answer_from_minilm_knowledge_base(
    question: str
):

    print(
        "\n[MINILM KNOWLEDGE AGENT]"
    )

    print(
        f"Question: {question}"
    )


    # --------------------------------------------------------
    # Retrieve relevant knowledge
    # --------------------------------------------------------

    documents = (
        retrieve_from_minilm_knowledge_base(
            question
        )
    )


    # --------------------------------------------------------
    # Check whether anything was retrieved
    # --------------------------------------------------------

    if not documents:

        return (
            "The information is not available "
            "in the CeylonCare knowledge base."
        )


    # --------------------------------------------------------
    # Build knowledge context
    # --------------------------------------------------------

    context = "\n\n".join(
        document.page_content
        for document in documents
    )


    # --------------------------------------------------------
    # Grounded prompt
    # --------------------------------------------------------

    prompt = f"""
You are the CeylonCare Knowledge Agent.

Answer the user's question using ONLY the
information provided in the knowledge context.

If the answer cannot be found in the context,
say:

"The information is not available in the
CeylonCare knowledge base."

Do not invent information.

Do not diagnose medical conditions.

Do not provide medical advice beyond the
information contained in the knowledge context.

Knowledge context:
{context}

User question:
{question}

Answer:
"""


    # --------------------------------------------------------
    # Generate grounded answer
    # --------------------------------------------------------

    print(
        "\n[GENERATING GROUNDED ANSWER]"
    )

    try:
        response = llm.invoke(
            prompt
        )

        answer = extract_response_text(
            response
        )
    except Exception as e:
        print(f"[MINILM RAG] LLM generation error ({e}). Returning direct retrieved knowledge context.")
        answer = context

    # --------------------------------------------------------
    # Display result
    # --------------------------------------------------------

    print(
        "\n[FINAL MINILM RAG RESPONSE]"
    )

    print(answer)

    return answer


# ============================================================
# Standalone test
# ============================================================

if __name__ == "__main__":

    test_question = (
        "What time does the "
        "CeylonCare clinic open?"
    )

    answer_from_minilm_knowledge_base(
        test_question
    )