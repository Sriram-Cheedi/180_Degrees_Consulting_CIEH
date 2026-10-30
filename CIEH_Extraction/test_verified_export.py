
import sqlite3
import tempfile
from pathlib import Path

from src.database.connection import get_connection
from src.database.review_manager import review_record
from src.review.export_verified_data import (
    export_verified_data,
    get_verified_records
)


with tempfile.TemporaryDirectory() as temp_dir:
    temp_dir = Path(temp_dir)

    source = get_connection()
    connection = sqlite3.connect(temp_dir / "test.db")

    try:
        source.backup(connection)
    finally:
        source.close()

    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    try:
        records = connection.execute(
            """
            SELECT id, count
            FROM extraction_records
            WHERE review_status = 'pending'
            ORDER BY id
            LIMIT 3
            """
        ).fetchall()

        if len(records) < 3:
            raise ValueError("Need 3 pending records")

        with connection:
            review_record(
                connection,
                records[0]["id"],
                "approved",
                "Test Reviewer"
            )

            review_record(
                connection,
                records[1]["id"],
                "corrected",
                "Test Reviewer",
                corrections={
                    "count": records[1]["count"] + 1
                }
            )

            review_record(
                connection,
                records[2]["id"],
                "rejected",
                "Test Reviewer"
            )

        verified = get_verified_records(connection)

        exported_ids = {
            record["record_id"] for record in verified
        }

        assert records[0]["id"] in exported_ids
        assert records[1]["id"] in exported_ids
        assert records[2]["id"] not in exported_ids

        corrected = next(
            record for record in verified
            if record["record_id"] == records[1]["id"]
        )

        assert corrected["count"] == records[1]["count"] + 1

        total = export_verified_data(
            temp_dir / "output",
            connection
        )

        assert total == 2

        print("\nAll verified export tests passed!")

    finally:
        connection.close()
