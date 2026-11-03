from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from src.rag.minilm_knowledge_retriever import retrieve_from_minilm_knowledge_base

load_dotenv()
from src.utils.llm_factory import get_llm

llm = get_llm(temperature=0)

def extract_response_text(response):
    if isinstance(response.content, list):
        answer_parts = []
        for block in response.content:
            if isinstance(block, dict) and block.get("type") == "text":
                answer_parts.append(block.get("text", ""))
        return "\n".join(answer_parts).strip()
    return str(response.content).strip()

def format_history(chat_history):
    if not chat_history:
        return "No prior conversation."
    formatted = []
    for msg in chat_history:
        role = "Patient" if msg.get("role") == "user" else "Assistant"
        content = msg.get("content", "")
        formatted.append(f"{role}: {content}")
    return "\n".join(formatted)

def safe_print(text):
    try:
        print(text)
    except Exception:
        try:
            print(str(text).encode('ascii', errors='replace').decode('ascii'))
        except Exception:
            pass

def answer_from_minilm_knowledge_base(question: str, chat_history: list = None):
    print("\n[MINILM KNOWLEDGE AGENT]")
    safe_print(f"Question: {question}")

    documents = retrieve_from_minilm_knowledge_base(question)

    if not documents:
        return "The information is not available in the CeylonCare knowledge base."

    context = "\n\n".join(document.page_content for document in documents)
    history_text = format_history(chat_history)

    prompt = f"""
You are the CeylonCare Knowledge Agent.
Answer the user's question using ONLY the information provided in the knowledge context.
If the answer cannot be found in the context, say: "The information is not available in the CeylonCare knowledge base."

Do not invent information. Do not diagnose medical conditions.
Do not provide medical advice beyond the information contained in the knowledge context.

Knowledge context:
{context}

Conversation History:
{history_text}

User question:
{question}

Answer:
"""

    print("\n[GENERATING GROUNDED ANSWER]")
    try:
        response = llm.invoke(prompt)
        answer = extract_response_text(response)
    except Exception as e:
        safe_print(f"[MINILM RAG] LLM generation error ({e}). Returning direct retrieved knowledge context.")
        answer = context

    print("\n[FINAL MINILM RAG RESPONSE]")
    safe_print(answer)
    return answer

if __name__ == "__main__":
    test_question = "What time does the CeylonCare clinic open?"
    answer_from_minilm_knowledge_base(test_question)