from pathlib import Path
from dotenv import load_dotenv

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document


# ============================================================
# CeylonCare RAG Knowledge Base Builder
# ============================================================

load_dotenv()

KNOWLEDGE_FILE = Path("knowledge/clinic_information.txt")
CHROMA_DIR = "data/chroma"
COLLECTION_NAME = "ceyloncare_knowledge"


# ------------------------------------------------------------
# 1. Check knowledge file
# ------------------------------------------------------------

print("[1/5] Checking knowledge file...")

if not KNOWLEDGE_FILE.exists():
    raise FileNotFoundError(
        f"Knowledge file not found: {KNOWLEDGE_FILE}"
    )

print(f"       Found: {KNOWLEDGE_FILE}")


# ------------------------------------------------------------
# 2. Read knowledge
# ------------------------------------------------------------

print("[2/5] Reading knowledge file...")

text = KNOWLEDGE_FILE.read_text(
    encoding="utf-8"
)

sections = [
    section.strip()
    for section in text.split("\n\n")
    if section.strip()
]

documents = []

for index, section in enumerate(sections):

    documents.append(
        Document(
            page_content=section,
            metadata={
                "source": "clinic_information.txt",
                "section": index
            }
        )
    )

print(f"       Loaded {len(documents)} sections.")


# ------------------------------------------------------------
# 3. Create Gemini embedding model
# ------------------------------------------------------------

print("[3/5] Creating Gemini embedding model...")

embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-2-preview"
)

print("       Embedding model ready.")


# ------------------------------------------------------------
# 4. Create embeddings FIRST
# ------------------------------------------------------------

print("[4/5] Creating embeddings...")
print("       Sending the 10 knowledge sections to Gemini...")

texts = [
    document.page_content
    for document in documents
]

vectors = embeddings.embed_documents(texts)

print(f"       Successfully created {len(vectors)} embeddings.")
print(f"       Vector dimensions: {len(vectors[0])}")


# ------------------------------------------------------------
# 5. Store pre-computed embeddings in Chroma
# ------------------------------------------------------------

print("[5/5] Creating Chroma database...")

vector_store = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
    persist_directory=CHROMA_DIR,
)

# Get the underlying Chroma collection
collection = vector_store._collection

# Create unique IDs for each document
ids = [
    f"clinic_section_{index}"
    for index in range(len(documents))
]

# Check whether documents are already stored
existing_count = collection.count()

print(f"       Existing records: {existing_count}")

if existing_count == 0:

    collection.add(
        ids=ids,
        embeddings=vectors,
        documents=texts,
        metadatas=[
            document.metadata
            for document in documents
        ],
    )

    print("       Added 10 documents to Chroma.")

else:

    print("       Chroma already contains documents.")
    print("       Skipping duplicate insertion.")


print("       Chroma database ready.")

# ------------------------------------------------------------
# Retrieval test
# ------------------------------------------------------------

print()
print("=" * 60)
print("CEYLONCARE RAG RETRIEVAL TEST")
print("=" * 60)

query = "What time does the CeylonCare clinic open?"

print(f"Question: {query}")
print()
print("Searching Chroma...")

results = vector_store.similarity_search(
    query,
    k=2
)

for index, document in enumerate(results, start=1):

    print()
    print(f"--- Result {index} ---")
    print(document.page_content)
    print(f"Source: {document.metadata}")


print()
print("=" * 60)
print("RAG BUILD COMPLETE")
print("=" * 60)