import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from utils.db_connection import execute_query


def test_database_helper():
    query = "SELECT full_name, country FROM player"

    players = execute_query(query)

    print("Database helper working successfully!")
    print(f"Players found: {len(players)}")

    for player in players[:3]:
        print(player)


if __name__ == "__main__":
    test_database_helper()