import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Load environment variables
load_dotenv()

print("[EMBEDDING TEST]")

# Create Gemini embedding model
embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-2-preview"
)

# Create an embedding for a test sentence
text = "The CeylonCare clinic is open from 8:00 AM to 5:00 PM."

vector = embeddings.embed_query(text)

print("Embedding created successfully!")
print(f"Vector dimensions: {len(vector)}")
print(f"First 5 values: {vector[:5]}")