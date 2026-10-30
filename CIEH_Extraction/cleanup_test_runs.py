
from src.database.connection import get_connection

connection = get_connection()

try:
    with connection:
        test_runs = connection.execute(
            """
            SELECT id
            FROM extraction_runs
            WHERE model_provider = 'gemini_test'
            """
        ).fetchall()

        run_ids = [row["id"] for row in test_runs]

        if run_ids:
            placeholders = ",".join("?" for _ in run_ids)

            connection.execute(
                f"""
                DELETE FROM record_reviews
                WHERE extraction_record_id IN (
                    SELECT id
                    FROM extraction_records
                    WHERE extraction_run_id IN ({placeholders})
                )
                """,
                run_ids
            )

            connection.execute(
                f"""
                DELETE FROM extraction_records
                WHERE extraction_run_id IN ({placeholders})
                """,
                run_ids
            )

            connection.execute(
                f"""
                DELETE FROM extraction_runs
                WHERE id IN ({placeholders})
                """,
                run_ids
            )

        print(f"Removed {len(run_ids)} test runs.")

finally:
    connection.close()
