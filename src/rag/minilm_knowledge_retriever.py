from sentence_transformers import SentenceTransformer
from langchain_chroma import Chroma
import os

# ============================================================
# CeylonCare MiniLM Knowledge Retriever
# Uses: sentence-transformers/all-MiniLM-L6-v2 + ChromaDB
# ============================================================

CHROMA_DIR = "data/chroma_minilm"
COLLECTION_NAME = "ceyloncare_knowledge_minilm"

_model = None
_vector_store = None
_retriever = None

class MiniLMEmbeddings:
    """
    Adapter that allows Sentence Transformers
    MiniLM embeddings to be used by ChromaDB.
    """
    def __init__(self, st_model):
        self.model = st_model

    def embed_documents(self, texts):
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()

    def embed_query(self, text):
        embedding = self.model.encode(text, normalize_embeddings=True)
        return embedding.tolist()


def _get_retriever():
    global _model, _vector_store, _retriever
    if _retriever is None:
        print("\n[MINILM RAG] Loading all-MiniLM-L6-v2...")
        _model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        print("[MINILM RAG] Model loaded.")

        embedding_function = MiniLMEmbeddings(_model)
        _vector_store = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=embedding_function,
            persist_directory=CHROMA_DIR,
        )
        _retriever = _vector_store.as_retriever(search_kwargs={"k": 4})
    return _retriever


def retrieve_from_minilm_knowledge_base(question: str):
    """
    Retrieve relevant documents from the MiniLM-powered CeylonCare knowledge base.
    """
    try:
        retriever = _get_retriever()
        documents = retriever.invoke(question)
        print(f"[MINILM RAG RETRIEVAL] Retrieved {len(documents)} knowledge documents.")
        return documents
    except Exception as e:
        print(f"[MINILM RAG RETRIEVAL ERROR] {e}")
        return []


if __name__ == "__main__":
    docs = retrieve_from_minilm_knowledge_base("What time does the CeylonCare clinic open?")
    for d in docs:
        print(d.page_content[:100])
