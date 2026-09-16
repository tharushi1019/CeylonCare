from sentence_transformers import SentenceTransformer

from langchain_chroma import Chroma


# ============================================================
# CeylonCare MiniLM Knowledge Retriever
#
# Uses the assignment-provided:
# sentence-transformers/all-MiniLM-L6-v2
#
# IMPORTANT:
# This uses data/chroma_minilm.
# The original data/chroma database is NOT touched.
# ============================================================


CHROMA_DIR = "data/chroma_minilm"

COLLECTION_NAME = (
    "ceyloncare_knowledge_minilm"
)


# ============================================================
# Load MiniLM model
# ============================================================

print(
    "\n[MINILM RAG] Loading "
    "all-MiniLM-L6-v2..."
)

model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

print(
    "[MINILM RAG] Model loaded."
)

print(
    "[MINILM RAG] Embedding dimension:",
    model.get_embedding_dimension(),
)


# ============================================================
# MiniLM embedding wrapper for Chroma
# ============================================================

class MiniLMEmbeddings:
    """
    Adapter that allows Sentence Transformers
    MiniLM embeddings to be used by ChromaDB.
    """

    def embed_documents(self, texts):

        embeddings = model.encode(
            texts,
            normalize_embeddings=True,
        )

        return embeddings.tolist()

    def embed_query(self, text):

        embedding = model.encode(
            text,
            normalize_embeddings=True,
        )

        return embedding.tolist()


embedding_function = MiniLMEmbeddings()


# ============================================================
# Load MiniLM Chroma database
# ============================================================

vector_store = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=embedding_function,
    persist_directory=CHROMA_DIR,
)


# ============================================================
# Create retriever
# ============================================================

retriever = vector_store.as_retriever(
    search_kwargs={
        "k": 2
    }
)


# ============================================================
# Retrieval function
# ============================================================

def retrieve_from_minilm_knowledge_base(
    question: str
):
    """
    Retrieve relevant documents from the
    MiniLM-powered CeylonCare knowledge base.
    """

    print(
        "\n[MINILM RAG RETRIEVAL]"
    )

    print(
        f"Question: {question}"
    )

    documents = retriever.invoke(
        question
    )

    print(
        f"Retrieved {len(documents)} "
        "knowledge documents."
    )

    for index, document in enumerate(
        documents,
        start=1,
    ):

        print(
            f"\n--- Retrieved Document "
            f"{index} ---"
        )

        print(
            document.page_content
        )

        print(
            f"Source: {document.metadata}"
        )

    return documents


# ============================================================
# Standalone test
# ============================================================

if __name__ == "__main__":

    question = (
        "What time does the "
        "CeylonCare clinic open?"
    )

    documents = (
        retrieve_from_minilm_knowledge_base(
            question
        )
    )

    print(
        "\n[MINILM RAG TEST COMPLETE]"
    )