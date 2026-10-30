
from collections import defaultdict
from datetime import datetime
import re
from src.database.connection import get_connection


VALID_CATEGORIES = {
    "tattoo_premises",
    "tattoo_practitioners",
    "combined_premises_and_practitioners",
    "other",
    "unknown"
}

VALID_METRICS = {
    "active_register_total",
    "new_registrations",
    "applications",
    "other",
    "unknown"
}


def audit_database():
    connection = get_connection()

    try:
        records = connection.execute(
            """
            SELECT
                er.id,
                r.council_name,
                sf.filename,
                sf.file_hash,
                er.year,
                er.category,
                er.metric_type,
                er.count,
                er.evidence_text,
                er.review_status,
                run.id AS run_id
            FROM extraction_records er
            JOIN extraction_runs run
                ON er.extraction_run_id = run.id
            JOIN source_files sf
                ON run.source_file_id = sf.id
            JOIN responses r
                ON sf.response_id = r.id
            WHERE run.status = 'completed'
              AND run.model_provider != 'gemini_test'
            ORDER BY er.id
            """
        ).fetchall()

    finally:
        connection.close()

    issues = []
    duplicate_groups = defaultdict(list)

    current_year = datetime.now().year

    for record in records:
        record = dict(record)
        record_id = record["id"]

        def flag(issue_type, message):
            issues.append({
                "record_id": record_id,
                "filename": record["filename"],
                "issue_type": issue_type,
                "message": message
            })

        # 1. Missing council
        if not record["council_name"] or not record["council_name"].strip():
            flag("missing_council", "Council name not identified")

        # 2. Invalid or missing year
        year = record["year"]
        if year is None or not str(year).strip():
            flag("missing_year", "Year is missing")
        else:
            year_text = str(year).strip()

            calendar_year = re.fullmatch(r"\d{4}", year_text)
            financial_year = re.fullmatch(
                r"(\d{4})/(\d{2})",
                year_text
                )

            if calendar_year:
                valid = 1900 <= int(year_text) <= current_year

            elif financial_year:
                start_year = int(financial_year.group(1))
                end_year = int(financial_year.group(2))

                valid = (
                    1900 <= start_year <= current_year
                    and end_year == (start_year + 1) % 100
                )

            else:
                valid = False

            if not valid:
                flag("review_year", f"Check year: {year_text}")

        # 3. Categories
        if record["category"] not in VALID_CATEGORIES:
            flag("invalid_category", str(record["category"]))

        elif record["category"] in {"other", "unknown"}:
            flag(
                "ambiguous_category",
                f"Category: {record['category']}"
            )

        # 4. Metric types
        if record["metric_type"] not in VALID_METRICS:
            flag("invalid_metric", str(record["metric_type"]))

        elif record["metric_type"] in {"other", "unknown"}:
            flag(
                "ambiguous_metric",
                f"Metric: {record['metric_type']}"
            )

        # 5. Counts
        if (
            type(record["count"]) is not int
            or record["count"] < 0
        ):
            flag("invalid_count", "Count is invalid")

        # 6. Evidence
        if not record["evidence_text"] or not record["evidence_text"].strip():
            flag("missing_evidence", "Supporting evidence is missing")

        # 7. Detect potentially repeated observations
        key = (
            record["council_name"],
            record["year"],
            record["category"],
            record["metric_type"],
            record["count"]
        )

        duplicate_groups[key].append(record_id)

    for record_ids in duplicate_groups.values():
        if len(record_ids) > 1:
            issues.append({
                "record_id": ", ".join(map(str, record_ids)),
                "filename": "Multiple records",
                "issue_type": "possible_duplicate",
                "message": (
                    "Same council, year, category, "
                    "metric and count"
                )
            })

    summary = {
        "records_checked": len(records),
        "issues_found": len(issues),
        "records_flagged": len({
            item["record_id"]
            for item in issues
            if isinstance(item["record_id"], int)
        })
    }

    return summary, issues
