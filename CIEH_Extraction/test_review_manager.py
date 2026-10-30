
from src.database.connection import get_connection
from src.database.review_manager import (
    get_pending_reviews,
    review_record
)


connection = get_connection()

try:
    pending = get_pending_reviews(connection)

    print("Pending records:", len(pending))

    if not pending:
        raise ValueError("No pending records available for testing")

    record = pending[0]
    record_id = record["record_id"]

    print("\nTesting record:", record_id)
    print("Original count:", record["count"])

    connection.execute("SAVEPOINT test_review")

    try:
        review_record(
            connection=connection,
            record_id=record_id,
            decision="corrected",
            reviewer="test_reviewer",
            notes="Testing correction workflow",
            corrections={
                "count": record["count"] + 1
            }
        )

        result = connection.execute(
            """
            SELECT
                er.count AS original_count,
                er.review_status,
                rr.corrected_count,
                rr.decision
            FROM extraction_records er
            JOIN record_reviews rr
                ON rr.extraction_record_id = er.id
            WHERE er.id = ?
            ORDER BY rr.id DESC
            LIMIT 1
            """,
            (record_id,)
        ).fetchone()

        print("\n=== REVIEW RESULT ===")
        print(dict(result))

        assert result["original_count"] == record["count"]
        assert result["corrected_count"] == record["count"] + 1
        assert result["review_status"] == "corrected"

    finally:
        connection.execute("ROLLBACK TO SAVEPOINT test_review")
        connection.execute("RELEASE SAVEPOINT test_review")

    print("\nTest passed. Changes rolled back.")

finally:
    connection.close()
