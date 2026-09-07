import sqlite3
from pathlib import Path


# Get the project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Path to the SQLite database
DATABASE_PATH = BASE_DIR / "data" / "cricbuzz.db"


def initialize_database(include_sample_data=False):
    """Create the database schema, optionally loading the bundled sample data."""
    schema_path = BASE_DIR / "sql" / "schema.sql"
    sample_path = BASE_DIR / "sql" / "sample_data.sql"
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    try:
        connection.execute("PRAGMA foreign_keys = ON")
        has_schema = connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'player'"
        ).fetchone()
        if not has_schema:
            connection.executescript(schema_path.read_text(encoding="utf-8"))
        has_data = connection.execute("SELECT 1 FROM player LIMIT 1").fetchone()
        if include_sample_data and not has_data:
            connection.executescript(sample_path.read_text(encoding="utf-8"))
        connection.commit()
    finally:
        connection.close()


def get_connection():
    """
    Create and return a connection to the SQLite database.
    """
    connection = sqlite3.connect(DATABASE_PATH)

    # Enable foreign key constraints
    connection.execute("PRAGMA foreign_keys = ON")

    return connection