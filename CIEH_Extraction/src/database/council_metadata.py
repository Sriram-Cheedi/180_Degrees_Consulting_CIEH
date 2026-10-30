
from src.database.connection import get_connection


def update_council_name(response_id: int, council_name: str):
    council_name = council_name.strip()

    if not council_name:
        raise ValueError("Council name cannot be empty")

    connection = get_connection()

    try:
        with connection:
            cursor = connection.execute(
                """
                UPDATE responses
                SET council_name = ?
                WHERE id = ?
                """,
                (council_name, response_id)
            )

            if cursor.rowcount != 1:
                raise ValueError(
                    f"Response {response_id} does not exist"
                )

    finally:
        connection.close()
