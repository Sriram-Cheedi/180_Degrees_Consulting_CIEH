
from src.database.connection import get_connection


def add_extraction_result_hash():
    connection = get_connection()

    try:
        columns = connection.execute(
            "PRAGMA table_info(extraction_runs)"
        ).fetchall()

        column_names = {column["name"] for column in columns}

        if "result_hash" not in column_names:
            connection.execute(
                "ALTER TABLE extraction_runs ADD COLUMN result_hash TEXT"
            )

        connection.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS
            idx_extraction_result_hash
            ON extraction_runs(source_file_id, result_hash)
        """)

        connection.commit()

    finally:
        connection.close()
