from src.database.connection import get_connection


def start_extraction_run(source_file_id: int, model_provider: str, model_name: str | None = None) -> int:
    connection = get_connection()

    try:
        with connection:
            cursor = connection.execute(
                """
                INSERT INTO extraction_runs (
                    source_file_id,
                    model_provider,
                    model_name,
                    status
                )
                VALUES (?, ?, ?, 'processing')
                """,
                (
                    source_file_id,
                    model_provider,
                    model_name
                )
            )

            return cursor.lastrowid

    finally:
        connection.close()


def complete_extraction_run(run_id: int):
    connection = get_connection()

    try:
        with connection:
            cursor = connection.execute(
                """
                UPDATE extraction_runs
                SET status = 'completed',
                    completed_at = CURRENT_TIMESTAMP,
                    error_message = NULL
                WHERE id = ?
                  AND status = 'processing'
                """,
                (run_id,)
            )

            if cursor.rowcount != 1:
                raise ValueError(f"Run {run_id} is not in processing status")

    finally:
        connection.close()


def fail_extraction_run(run_id: int, error_message: str):
    connection = get_connection()
    try:
        with connection:
            cursor = connection.execute(
                """
                UPDATE extraction_runs
                SET status = 'failed',
                    error_message = ?,
                    completed_at = CURRENT_TIMESTAMP
                WHERE id = ?
                  AND status = 'processing'
                """,
                (str(error_message), run_id)
            )

            if cursor.rowcount != 1:
                raise ValueError(f"Run {run_id} is not in processing status")

    finally:
        connection.close()


def get_extraction_history(source_file_id: int) -> list[dict]:
    connection = get_connection()

    try:
        rows = connection.execute(
            """
            SELECT
                id,
                model_provider,
                model_name,
                status,
                error_message,
                started_at,
                completed_at
            FROM extraction_runs
            WHERE source_file_id = ?
            ORDER BY id DESC
            """,
            (source_file_id,)
        ).fetchall()

        return [dict(row) for row in rows]

    finally:
        connection.close()