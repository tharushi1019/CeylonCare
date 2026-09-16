import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI


# --------------------------------------------------
# Load environment variables
# --------------------------------------------------

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY was not found.")


# --------------------------------------------------
# Create the Gemini chat model
# --------------------------------------------------

model = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash",
    google_api_key=api_key,
    temperature=0,
)


# --------------------------------------------------
# Create a tool
# --------------------------------------------------

@tool
def get_clinic_hours(day: str) -> str:
    """Get the CeylonCare clinic opening hours for a given day."""

    print(f"\n[TOOL EXECUTED] get_clinic_hours(day='{day}')")

    hours = {
        "monday": "8:00 AM to 5:00 PM",
        "tuesday": "8:00 AM to 5:00 PM",
        "wednesday": "8:00 AM to 5:00 PM",
        "thursday": "8:00 AM to 5:00 PM",
        "friday": "8:00 AM to 5:00 PM",
        "saturday": "9:00 AM to 1:00 PM",
        "sunday": "Closed",
    }

    return hours.get(
        day.lower(),
        "Clinic hours are not available for that day."
    )


# --------------------------------------------------
# Create the agent
# --------------------------------------------------

agent = create_agent(
    model=model,
    tools=[get_clinic_hours],
    system_prompt=(
        "You are the CeylonCare clinic assistant. "
        "Use the clinic-hours tool whenever the user asks "
        "about clinic opening hours. "
        "Do not invent clinic hours."
    ),
)


# --------------------------------------------------
# Run the agent
# --------------------------------------------------

result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "What time is the CeylonCare clinic open on Monday?"
            }
        ]
    }
)


# --------------------------------------------------
# Display the final answer
# --------------------------------------------------

print("\n[FINAL AGENT RESPONSE]")

final_message = result["messages"][-1]

if isinstance(final_message.content, str):
    print(final_message.content)
else:
    for part in final_message.content:
        if isinstance(part, dict) and part.get("type") == "text":
            print(part.get("text", ""))