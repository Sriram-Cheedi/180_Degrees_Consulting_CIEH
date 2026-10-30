
from src.database.connection import get_connection


connection = get_connection()

try:
    source = connection.execute(
        "SELECT id FROM source_files LIMIT 1"
    ).fetchone()

    if source is None:
        raise ValueError("No source files registered")

    source_id = source["id"]

    connection.execute("SAVEPOINT test_history")

    try:
        cursor = connection.execute(
            """
            INSERT INTO extraction_runs (
                source_file_id, model_provider,
                model_name, status
            )
            VALUES (?, 'gemini_test', 'test-model', 'processing')
            """,
            (source_id,)
        )

        run_id = cursor.lastrowid

        print("Created test run:", run_id)

        connection.execute(
            """
            UPDATE extraction_runs
            SET status = 'failed',
                error_message = 'Simulated API failure',
                completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (run_id,)
        )

        row = connection.execute(
            """
            SELECT status, error_message
            FROM extraction_runs
            WHERE id = ?
            """,
            (run_id,)
        ).fetchone()

        print("Status:", row["status"])
        print("Error:", row["error_message"])

        assert row["status"] == "failed"

    finally:
        connection.execute("ROLLBACK TO SAVEPOINT test_history")
        connection.execute("RELEASE SAVEPOINT test_history")

finally:
    connection.close()

print("Test completed. No test run was saved.")
