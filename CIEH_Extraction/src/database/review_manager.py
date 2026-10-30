
from typing import Literal


ReviewDecision = Literal[
    "approved",
    "rejected",
    "corrected"
]


def review_record(
    connection,
    record_id: int,
    decision: ReviewDecision,
    reviewer: str,
    notes: str | None = None,
    corrections: dict | None = None
):
    if decision not in {"approved", "rejected", "corrected"}:
        raise ValueError("Invalid review decision")

    if not reviewer.strip():
        raise ValueError("Reviewer name is required")

    record = connection.execute(
        """
        SELECT id, review_status
        FROM extraction_records
        WHERE id = ?
        """,
        (record_id,)
    ).fetchone()

    if record is None:
        raise ValueError(f"Record {record_id} not found")

    corrections = corrections or {}

    allowed_fields = {
        "year",
        "category",
        "metric_type",
        "count"
    }

    if set(corrections) - allowed_fields:
        raise ValueError("Unsupported correction fields")

    if decision == "corrected":
        if not corrections:
            raise ValueError(
                "Corrected records require correction values"
            )

        if "count" in corrections:
            count = corrections["count"]

            if type(count) is not int or count < 0:
                raise ValueError("Corrected count must be nonnegative")

    elif corrections:
        raise ValueError(
            "Corrections are only allowed for corrected decisions"
        )

    connection.execute(
        """
        INSERT INTO record_reviews (
            extraction_record_id,
            decision,
            corrected_year,
            corrected_category,
            corrected_metric_type,
            corrected_count,
            reviewer,
            reviewer_notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            record_id,
            decision,
            corrections.get("year"),
            corrections.get("category"),
            corrections.get("metric_type"),
            corrections.get("count"),
            reviewer,
            notes
        )
    )

    connection.execute(
        """
        UPDATE extraction_records
        SET review_status = ?
        WHERE id = ?
        """,
        (decision, record_id)
    )



def get_pending_reviews(connection) -> list[dict]:
    rows = connection.execute(
        """
        SELECT
            er.id AS record_id,
            sf.filename,
            sf.file_path,
            er.year,
            er.category,
            er.metric_type,
            er.count,
            er.evidence_text,
            er.source_location,
            er.review_status
        FROM extraction_records er
        JOIN extraction_runs run
            ON er.extraction_run_id = run.id
        JOIN source_files sf
            ON run.source_file_id = sf.id
        WHERE er.review_status = 'pending'
          AND run.status = 'completed'
        ORDER BY sf.filename, er.id
        """
    ).fetchall()

    return [dict(row) for row in rows]
