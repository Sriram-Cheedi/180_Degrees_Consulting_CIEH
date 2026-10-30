
import json
from pathlib import Path

from src.ai.extraction_service import extract_document
from src.ai.save_extraction import save_extraction
from src.database.connection import get_connection
from src.database.schema import create_tables
from src.database.import_data import (
    register_response,
    register_source_file
)
from src.database.processing_history import (
    start_extraction_run,
    fail_extraction_run
)


BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = BASE_DIR / "data" / "raw"


def get_response_group(source_path: str) -> str:
    relative = Path(source_path).resolve().relative_to(RAW_DIR.resolve())
    if len(relative.parts) == 1:
        return f"file:{relative.as_posix()}"

    return f"folder:{relative.parts[0]}"


def register_document(parsed_document: dict) -> int:
    source = parsed_document.get("source") or {}
    source_path = source.get("file_path")
    if not source_path:
        raise ValueError("Missing source path")

    response_group = get_response_group(source_path)
    connection = get_connection()

    try:
        with connection:
            response_id = register_response(connection, response_group)
            source_file_id = register_source_file(connection, response_id, parsed_document)

        return source_file_id

    finally:
        connection.close()


def save_records_to_run(run_id: int, extraction_data: dict):
    records = extraction_data["extraction"]["records"]
    council_name = extraction_data["extraction"].get("council_name")
    connection = get_connection()

    try:
        with connection:
            if council_name and council_name.strip():
                connection.execute(
                    """
                    UPDATE responses
                    SET council_name = ?
                    WHERE id = (
                        SELECT sf.response_id
                        FROM source_files sf
                        JOIN extraction_runs run
                            ON run.source_file_id = sf.id
                        WHERE run.id = ?
                    )
                    """,
                    (council_name.strip(), run_id)
                )
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
                raise ValueError(f"Run {run_id} is not processing")

    finally:
        connection.close()


def extract_all_documents(parsed_directory: Path, extracted_directory: Path) -> dict:
    create_tables()
    parsed_directory = Path(parsed_directory)
    extracted_directory = Path(extracted_directory)

    extracted_directory.mkdir(parents=True, exist_ok=True)

    summary = {
        "total": 0,
        "completed": 0,
        "skipped": 0,
        "failed": 0,
        "errors": []
    }

    for file_path in sorted(parsed_directory.glob("*.json")):
        summary["total"] += 1
        run_id = None

        try:
            with file_path.open("r", encoding="utf-8") as file:
                parsed_document = json.load(file)

            source = parsed_document.get("source") or {}
            file_hash = source.get("file_hash")

            if not file_hash:
                raise ValueError("Missing source file hash")

            output_path = extracted_directory / f"{file_hash}.json"

            if output_path.exists():
                summary["skipped"] += 1
                print(f"Skipped: {file_path.name}")
                continue

            source_file_id = register_document(parsed_document)
            run_id = start_extraction_run(source_file_id=source_file_id, model_provider="gemini",  model_name="gemini")

            print(
                f"Extracting: {file_path.name} "
                f"(Run ID: {run_id})",
                flush=True
            )

            extraction_data = extract_document(parsed_document)
            save_extraction(extraction_data, extracted_directory)
            save_records_to_run(run_id,extraction_data)
            summary["completed"] += 1
            print(f"Completed: {file_path.name}")

        except Exception as error:
            summary["failed"] += 1
            error_message = str(error)
            summary["errors"].append({"file": file_path.name, "error": error_message})

            if run_id is not None:
                try:
                    fail_extraction_run(run_id,error_message)
                except Exception as db_error:
                    print(
                        f"Could not record failure for "
                        f"run {run_id}: {db_error}"
                    )

            print(f"Failed: {file_path.name} — {error}")

    return summary
