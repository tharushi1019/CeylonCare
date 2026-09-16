from pathlib import Path

from sentence_transformers import SentenceTransformer

from langchain_chroma import Chroma
from langchain_core.documents import Document


# ============================================================
# CeylonCare MiniLM RAG Knowledge Base Builder
#
# IMPORTANT:
# This creates a NEW Chroma database.
# It does NOT modify data/chroma.
# ============================================================


KNOWLEDGE_FILE = Path(
    "knowledge/clinic_information.txt"
)

CHROMA_DIR = "data/chroma_minilm"

COLLECTION_NAME = (
    "ceyloncare_knowledge_minilm"
)


# ============================================================
# 1. Check knowledge file
# ============================================================

print("[1/6] Checking knowledge file...")

if not KNOWLEDGE_FILE.exists():

    raise FileNotFoundError(
        f"Knowledge file not found: {KNOWLEDGE_FILE}"
    )

print(
    f"       Found: {KNOWLEDGE_FILE}"
)


# ============================================================
# 2. Read knowledge
# ============================================================

print("[2/6] Reading knowledge file...")

text = KNOWLEDGE_FILE.read_text(
    encoding="utf-8"
)

sections = [
    section.strip()
    for section in text.split("\n\n")
    if section.strip()
]

documents = []

for index, section in enumerate(
    sections
):

    documents.append(
        Document(
            page_content=section,
            metadata={
                "source": "clinic_information.txt",
                "section": index,
            },
        )
    )

print(
    f"       Loaded {len(documents)} sections."
)


# ============================================================
# 3. Load assignment-provided MiniLM model
# ============================================================

print(
    "[3/6] Loading "
    "all-MiniLM-L6-v2..."
)

model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

print(
    "       MiniLM model loaded."
)

print(
    "       Embedding dimension:",
    model.get_embedding_dimension(),
)


# ============================================================
# 4. Create embeddings
# ============================================================

print("[4/6] Creating embeddings...")

texts = [
    document.page_content
    for document in documents
]

vectors = model.encode(
    texts,
    normalize_embeddings=True,
)

print(
    f"       Created {len(vectors)} embeddings."
)

print(
    "       Vector dimension:",
    len(vectors[0]),
)


# ============================================================
# 5. Create NEW Chroma database
# ============================================================

print(
    "[5/6] Creating NEW Chroma database..."
)

print(
    f"       Directory: {CHROMA_DIR}"
)

print(
    f"       Collection: {COLLECTION_NAME}"
)


# We use a simple embedding wrapper so that
# Chroma can embed future queries using MiniLM.

class MiniLMEmbeddings:

    def embed_documents(
        self,
        texts,
    ):

        embeddings = model.encode(
            texts,
            normalize_embeddings=True,
        )

        return embeddings.tolist()

    def embed_query(
        self,
        text,
    ):

        embedding = model.encode(
            text,
            normalize_embeddings=True,
        )

        return embedding.tolist()


embedding_function = MiniLMEmbeddings()


vector_store = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=embedding_function,
    persist_directory=CHROMA_DIR,
)


# ------------------------------------------------------------
# Check existing records
# ------------------------------------------------------------

collection = vector_store._collection

existing_count = collection.count()

print(
    f"       Existing records: "
    f"{existing_count}"
)


# ------------------------------------------------------------
# Add documents only if database is empty
# ------------------------------------------------------------

if existing_count == 0:

    ids = [
        f"clinic_minilm_section_{index}"
        for index in range(
            len(documents)
        )
    ]

    collection.add(
        ids=ids,
        embeddings=[
            vector.tolist()
            for vector in vectors
        ],
        documents=texts,
        metadatas=[
            document.metadata
            for document in documents
        ],
    )

    print(
        f"       Added {len(documents)} "
        "documents to MiniLM Chroma."
    )

else:

    print(
        "       MiniLM Chroma already "
        "contains documents."
    )

    print(
        "       Skipping duplicate insertion."
    )


print(
    "       MiniLM Chroma database ready."
)


# ============================================================
# 6. Retrieval test
# ============================================================

print()
print("=" * 60)
print(
    "CEYLONCARE MINILM RAG RETRIEVAL TEST"
)
print("=" * 60)

query = (
    "What time does the "
    "CeylonCare clinic open?"
)

print(
    f"Question: {query}"
)

print()
print(
    "Searching MiniLM Chroma..."
)

results = vector_store.similarity_search(
    query,
    k=2,
)


for index, document in enumerate(
    results,
    start=1,
):

    print()
    print(
        f"--- Result {index} ---"
    )

    print(
        document.page_content
    )

    print(
        f"Source: {document.metadata}"
    )


print()
print("=" * 60)
print(
    "MINILM RAG BUILD COMPLETE"
)
print("=" * 60)