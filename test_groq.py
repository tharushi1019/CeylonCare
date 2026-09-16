from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
)

response = llm.invoke(
    "Classify this request as appointment, knowledge, triage, or unknown: "
    "I need to book an appointment with a cardiologist tomorrow."
)

print("\n[GROQ TEST]")
print(response.content)