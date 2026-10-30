from src.database.connection import get_connection


def check_source_version(file_path: str, file_hash: str) -> dict:
    connection = get_connection()
    try:
        row = connection.execute(
            """
            SELECT id, file_hash
            FROM source_files
            WHERE file_path = ?
            """,
            (file_path,)
        ).fetchone()

        if row is None:
            return {
                "status": "new",
                "source_file_id": None
            }

        if row["file_hash"] == file_hash:
            return {
                "status": "unchanged",
                "source_file_id": row["id"]
            }

        return {
            "status": "changed",
            "source_file_id": row["id"]
        }

    finally:
        connection.close()
