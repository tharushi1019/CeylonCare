import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY was not found.")

client = genai.Client(api_key=api_key)

print("Models available to this API key:")
print("-" * 60)

for model in client.models.list():
    name = model.name or ""

    if "generateContent" in (model.supported_actions or []):
        print(name)