import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from api.client import CricketAPIClient
from config import API_BASE_URL, API_KEY, API_HOST


client = CricketAPIClient(
    base_url=API_BASE_URL,
    api_key=API_KEY,
    api_host=API_HOST,
)

print("API Base URL configured:", bool(API_BASE_URL))
print("API Key configured:", bool(API_KEY))
print("API Host configured:", bool(API_HOST))

print("Testing Cricbuzz API...")

try:
    data = client.get_live_matches()

    print("API request successful!")
    print("Response type:", type(data).__name__)
    print("Response keys:", ", ".join(data.keys()))
    print("Match groups:", len(data.get("typeMatches", [])))

except Exception as error:
    print("API request failed.")
    print("Error:", error)