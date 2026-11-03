import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from src.utils.llm_factory import get_llm

load_dotenv()

CHROMA_DIR = "data/chroma"
COLLECTION_NAME = "ceyloncare_knowledge"

_retriever = None

def _get_retriever():
    global _retriever
    if _retriever is None:
        try:
            embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2-preview")
            vector_store = Chroma(
                collection_name=COLLECTION_NAME,
                embedding_function=embeddings,
                persist_directory=CHROMA_DIR,
            )
            _retriever = vector_store.as_retriever(search_kwargs={"k": 2})
        except Exception as e:
            print(f"[KNOWLEDGE RETRIEVER] Init warning: {e}")
            _retriever = None
    return _retriever


def extract_response_text(response):
    if isinstance(response.content, list):
        parts = []
        for block in response.content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
        return "\n".join(parts).strip()
    return str(response.content).strip()


def answer_from_knowledge_base(question: str) -> str:
    retriever = _get_retriever()
    if not retriever:
        return "The information is not available in the CeylonCare knowledge base."

    try:
        docs = retriever.invoke(question)
        if not docs:
            return "The information is not available in the CeylonCare knowledge base."
        context = "\n\n".join(d.page_content for d in docs)
        llm = get_llm(temperature=0)
        prompt = f"Answer using only this context:\n{context}\n\nQuestion: {question}"
        resp = llm.invoke(prompt)
        return extract_response_text(resp)
    except Exception as e:
        print(f"[KNOWLEDGE RETRIEVER ERROR] {e}")
        return "The information is not available in the CeylonCare knowledge base."
