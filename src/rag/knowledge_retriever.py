from dotenv import load_dotenv

from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings,
)

from langchain_chroma import Chroma


# Load API keys from .env
load_dotenv()


# ============================================================
# CeylonCare Knowledge Base Retriever
# ============================================================

CHROMA_DIR = "data/chroma"
COLLECTION_NAME = "ceyloncare_knowledge"


# ------------------------------------------------------------
# Create Gemini embedding model
# ------------------------------------------------------------

embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-2-preview"
)


# ------------------------------------------------------------
# Load existing Chroma database
# ------------------------------------------------------------

vector_store = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
    persist_directory=CHROMA_DIR,
)


# ------------------------------------------------------------
# Create retriever
# ------------------------------------------------------------

retriever = vector_store.as_retriever(
    search_kwargs={"k": 2}
)


from src.utils.llm_factory import get_llm

llm = get_llm(temperature=0)


# ------------------------------------------------------------
# Extract text safely from Gemini response
# ------------------------------------------------------------

def extract_response_text(response):
    """
    Extract plain text from Gemini/LangChain response.
    Handles both string and structured content responses.
    """

    if isinstance(response.content, list):

        answer_parts = []

        for block in response.content:

            if isinstance(block, dict) and block.get("type") == "text":
                answer_parts.append(
                    block.get("text", "")
                )

        return "\n".join(answer_parts).strip()

    return str(response.content).strip()


# ------------------------------------------------------------
# Main RAG function
# ------------------------------------------------------------

def answer_from_knowledge_base(question: str):
    """
    Retrieve relevant CeylonCare knowledge and generate
    a grounded answer using Gemini.
    """

    print("\n[RAG RETRIEVAL]")

    print(f"Question: {question}")

    # Retrieve relevant documents
    documents = retriever.invoke(question)

    print(
        f"Retrieved {len(documents)} knowledge documents."
    )

    # Display retrieved documents
    for index, document in enumerate(
        documents,
        start=1
    ):

        print(
            f"\n--- Retrieved Document {index} ---"
        )

        print(document.page_content)

        print(
            f"Source: {document.metadata}"
        )

    # Build context
    context = "\n\n".join(
        document.page_content
        for document in documents
    )

    # Grounded prompt
    prompt = f"""
You are the CeylonCare Knowledge Agent.

Answer the user's question using ONLY the information
provided in the knowledge context.

If the answer cannot be found in the context,
say that the information is not available in the
CeylonCare knowledge base.

Do not invent medical information.
Do not diagnose the patient.
Do not provide medical advice beyond the information
contained in the knowledge context.

Knowledge context:
{context}

User question:
{question}

Answer:
"""

    print("\n[GENERATING GROUNDED ANSWER]")

    response = llm.invoke(prompt)

    answer = extract_response_text(response)

    return answer