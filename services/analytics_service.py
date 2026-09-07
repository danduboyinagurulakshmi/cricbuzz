import re
from pathlib import Path

from utils.db_connection import execute_query


QUERY_FILE = Path(__file__).resolve().parent.parent / "sql" / "queries" / "all_queries.sql"


def load_analytics_queries():
    """Load the named SQL practice queries from the repository."""
    content = QUERY_FILE.read_text(encoding="utf-8")
    blocks = re.split(r"(?:^|\n)-- QUERY (\d{2}): (.+)\n", content)
    queries = {}
    for index in range(1, len(blocks), 3):
        query_number, title, query = blocks[index : index + 3]
        queries[f"{query_number} - {title}"] = query.strip().rstrip(";")
    return queries


def run_analytics_query(query):
    """Execute one read-only analytics query."""
    if not query.lstrip().upper().startswith(("SELECT", "WITH")):
        raise ValueError("Analytics queries must be read-only SELECT statements")
    return execute_query(query)