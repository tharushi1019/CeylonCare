import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY was not found.")

client = genai.Client(api_key=api_key)


def get_clinic_hours(day: str) -> str:
    """
    Returns the CeylonCare clinic opening hours for a given day.
    """

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


response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents="What are the CeylonCare clinic opening hours on Monday?",
    config={
        "tools": [get_clinic_hours]
    },
)

print("\n[FINAL GEMINI RESPONSE]")
print(response.text)