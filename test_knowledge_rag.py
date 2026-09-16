import os

from dotenv import load_dotenv

from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings,
)

from langchain_chroma import Chroma


# ============================================================
# CeylonCare RAG Knowledge Agent Test
# ============================================================

load_dotenv()


# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

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


# ------------------------------------------------------------
# Create Gemini LLM
# ------------------------------------------------------------

llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash",
    temperature=0,
)


# ------------------------------------------------------------
# User question
# ------------------------------------------------------------

question = "What time does the CeylonCare clinic open?"


print("[KNOWLEDGE AGENT]")
print(f"Question: {question}")


# ------------------------------------------------------------
# Retrieve relevant information
# ------------------------------------------------------------

print("\n[RETRIEVING KNOWLEDGE]")

documents = retriever.invoke(question)

for index, document in enumerate(documents, start=1):

    print(f"\n--- Retrieved Document {index} ---")
    print(document.page_content)
    print(f"Source: {document.metadata}")


# ------------------------------------------------------------
# Build context
# ------------------------------------------------------------

context = "\n\n".join(
    document.page_content
    for document in documents
)


# ------------------------------------------------------------
# Generate grounded answer
# ------------------------------------------------------------

prompt = f"""
You are the CeylonCare Knowledge Agent.

Answer the user's question using ONLY the information
provided in the knowledge context.

If the answer cannot be found in the context,
say that the information is not available in the
CeylonCare knowledge base.

Do not invent medical information.
Do not diagnose the patient.

Knowledge context:
{context}

User question:
{question}

Answer:
"""


print("\n[GENERATING ANSWER]")

response = llm.invoke(prompt)


print("\n[FINAL KNOWLEDGE AGENT RESPONSE]")

if isinstance(response.content, list):

    answer_parts = []

    for block in response.content:

        if isinstance(block, dict) and block.get("type") == "text":
            answer_parts.append(block.get("text", ""))

    answer = "\n".join(answer_parts).strip()

else:

    answer = str(response.content).strip()


print(answer)