import json
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


try:
    data = client.get_live_matches()

    print("API request successful!")
    print("")

    print("Top-level keys:")
    for key in data.keys():
        print("-", key)

    print("")
    print("Formatted response:")

    print(json.dumps(data, indent=4))

except Exception as error:
    print("API request failed.")
    print("Error:", error)