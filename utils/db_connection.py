from database.connection import get_connection


def execute_query(query, parameters=()):
    """
    Execute a SELECT query and return all rows.
    """
    connection = get_connection()

    try:
        cursor = connection.cursor()
        cursor.execute(query, parameters)
        return cursor.fetchall()

    finally:
        connection.close()


def execute_command(query, parameters=()):
    """
    Execute INSERT, UPDATE, or DELETE query.
    """
    connection = get_connection()

    try:
        cursor = connection.cursor()
        cursor.execute(query, parameters)
        connection.commit()

    finally:
        connection.close()