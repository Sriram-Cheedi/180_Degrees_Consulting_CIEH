
import json
from pathlib import Path
import hashlib
from src.database.connection import get_connection


def register_response(connection, response_group, council_name=None):
    connection.execute(
        """
        INSERT OR IGNORE INTO responses (response_group, council_name)
        VALUES (?, ?)
        """,
        (response_group, council_name)
    )

    row = connection.execute(
        "SELECT id FROM responses WHERE response_group = ?",
        (response_group,)
    ).fetchone()

    return row["id"]


def register_source_file(connection, response_id, parsed_document):
    source = parsed_document.get("source") or {}

    file_path = source.get("file_path")
    file_hash = source.get("file_hash")

    if not file_path or not file_hash:
        raise ValueError("Missing source file path or hash")

    connection.execute(
        """
        INSERT OR IGNORE INTO source_files (
            response_id, filename, file_path,
            file_hash, extension, file_size, status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            response_id,
            parsed_document.get("filename"),
            file_path,
            file_hash,
            parsed_document.get("file_type"),
            source.get("file_size"),
            "parsed"
        )
    )

    row = connection.execute(
        "SELECT id, file_hash FROM source_files WHERE file_path = ?",
        (file_path,)
    ).fetchone()

    if row["file_hash"] != file_hash:
        raise ValueError(
            "Source file has changed at an existing path. "
            "Version handling is required."
        )

    return row["id"]



def register_extraction(connection, source_file_id, extraction_data):
    provider = extraction_data.get("model_provider", "unknown")
    extraction = extraction_data.get("extraction", {})
    records = extraction.get("records", [])

    if not isinstance(records, list):
        raise ValueError("Extraction records must be a list")


    canonical_payload = json.dumps(
        {
            "provider": provider,
            "model_name": extraction_data.get("model_name"),
            "extraction": extraction
        },
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":")
    )

    result_hash = hashlib.sha256(
        canonical_payload.encode("utf-8")
    ).hexdigest()

    existing = connection.execute(
        """
        SELECT id
        FROM extraction_runs
        WHERE source_file_id = ?
          AND result_hash = ?
        """,
        (source_file_id, result_hash)
    ).fetchone()

    if existing:
        return existing["id"], False

    cursor = connection.execute(
        """
        INSERT INTO extraction_runs (
            source_file_id,
            model_provider,
            model_name,
            status,
            result_hash,
            completed_at
        )
        VALUES (?, ?, ?, 'completed', ?, CURRENT_TIMESTAMP)
        """,
        (
            source_file_id,
            provider,
            extraction_data.get("model_name"),
            result_hash
        )
    )

    run_id = cursor.lastrowid

    for record in records:
        connection.execute(
            """
            INSERT INTO extraction_records (
                extraction_run_id,
                year,
                category,
                metric_type,
                count,
                evidence_text,
                source_location,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                record.get("year"),
                record["category"],
                record["metric_type"],
                record["count"],
                record["evidence_text"],
                record.get("source_location"),
                record.get("notes")
            )
        )

    return run_id, True