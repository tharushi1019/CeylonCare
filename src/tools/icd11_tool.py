import os
import requests

from dotenv import load_dotenv
from langchain_core.tools import tool

# ============================================================
# CeylonCare WHO ICD-11 Tool
# ============================================================

load_dotenv()

CLIENT_ID = os.getenv("WHO_ICD_CLIENT_ID")
CLIENT_SECRET = os.getenv("WHO_ICD_CLIENT_SECRET")

TOKEN_URL = (
    "https://icdaccessmanagement.who.int/connect/token"
)

SEARCH_URL = (
    "https://id.who.int/icd/release/11/2025-01/mms/search"
)


# ============================================================
# Get WHO API access token
# ============================================================

def get_access_token():

    if not CLIENT_ID or not CLIENT_SECRET:
        raise ValueError(
            "WHO ICD-11 API credentials are missing. "
            "Please set WHO_ICD_CLIENT_ID and "
            "WHO_ICD_CLIENT_SECRET in .env."
        )

    response = requests.post(
        TOKEN_URL,
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "scope": "icdapi_access",
            "grant_type": "client_credentials",
        },
        headers={
            "Content-Type":
                "application/x-www-form-urlencoded"
        },
        timeout=30,
    )

    response.raise_for_status()

    return response.json()["access_token"]


# ============================================================
# Search WHO ICD-11
# ============================================================

def search_icd11(term: str):
    """
    Search the official WHO ICD-11 API for a medical term.

    This tool retrieves terminology/reference information only.
    It does not diagnose medical conditions.
    """

    print("\n[WHO ICD-11 TOOL]")
    print(f"Searching for: {term}")

    token = get_access_token()

    response = requests.get(
        SEARCH_URL,
        params={
            "q": term,
        },
        headers={
            "Authorization": f"Bearer {token}",
            "API-Version": "v2",
            "Accept-Language": "en",
        },
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    print(
        "[WHO ICD-11 TOOL] Search response received."
    )

    print(
        f"[WHO ICD-11 TOOL] Response type: "
        f"{type(data).__name__}"
    )

    # --------------------------------------------------------
    # Extract search results
    # --------------------------------------------------------

    results = data.get(
        "destinationEntities",
        []
    )

    print(
        f"[WHO ICD-11 TOOL] "
        f"Search results found: {len(results)}"
    )

    # --------------------------------------------------------
    # No results
    # --------------------------------------------------------

    if not results:

        return {
            "term": term,
            "found": False,
            "message": (
                f"No ICD-11 results were found "
                f"for '{term}'."
            ),
        }

    # --------------------------------------------------------
    # First matching result
    # --------------------------------------------------------

    first_result = results[0]

    title = first_result.get("title")

    code = first_result.get("theCode")

    entity_id = first_result.get("id")

    uri = first_result.get("uri")

    # --------------------------------------------------------
    # Browser URL
    # --------------------------------------------------------

    browser_url = None

    if entity_id:

        browser_url = (
            "https://icd.who.int/browse/2025-01/mms/en"
            f"#{entity_id}"
        )

    # --------------------------------------------------------
    # Build clean result
    # --------------------------------------------------------

    result = {
        "term": term,
        "found": True,
        "title": title,
        "code": code,
        "entity_id": entity_id,
        "uri": uri,
        "browser_url": browser_url,
    }

    print(
        "[WHO ICD-11 TOOL] "
        "Useful information extracted."
    )

    print(
        f"[WHO ICD-11 TOOL] Matched title: {title}"
    )

    print(
        f"[WHO ICD-11 TOOL] Matched code: {code}"
    )

    return result


# ============================================================
# LangChain Tool
# ============================================================

@tool
def icd11_search_tool(term: str) -> dict:
    """
    Search the official WHO ICD-11 API for a medical term.

    Use this tool when the user asks for ICD-11 terminology
    or reference information.

    This tool does not diagnose medical conditions.
    """

    return search_icd11(term)


# ============================================================
# Simple test
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("CEYLONCARE WHO ICD-11 LANGCHAIN TOOL TEST")
    print("=" * 60)

    print(
        "\n[TEST] Searching WHO ICD-11 "
        "using LangChain tool..."
    )

    result = icd11_search_tool.invoke(
        {"term": "asthma"}
    )

    print(
        "\n[LANGCHAIN TOOL] Response received."
    )

    print(
        f"Response type: {type(result).__name__}"
    )

    print("\nResult:")

    for key, value in result.items():
        print(f"{key}: {value}")

    print(
        "\nWHO ICD-11 LANGCHAIN TOOL TEST COMPLETE"
    )