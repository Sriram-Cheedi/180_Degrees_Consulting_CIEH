
import json
from pathlib import Path

from src.database.connection import get_connection
from src.database.schema import create_tables
from src.database.import_data import (register_response, register_source_file, register_extraction)


BASE_DIR = Path(__file__).resolve().parent
PARSED_DIR = BASE_DIR / "data" / "parsed"
EXTRACTED_DIR = BASE_DIR / "data" / "extracted"
RAW_DIR = BASE_DIR / "data" / "raw"


def get_response_group(source_path):
    path = Path(source_path).resolve()
    raw = RAW_DIR.resolve()
    relative = path.relative_to(raw)

    if len(relative.parts) == 1:
        return f"file:{relative.as_posix()}"

    return f"folder:{relative.parts[0]}"


def import_existing_data():
    create_tables()
    summary = {
        "sources_registered": 0,
        "extractions_imported": 0,
        "extractions_skipped": 0,
        "missing_extractions": 0,
        "failed": 0
    }

    for parsed_path in sorted(PARSED_DIR.glob("*.json")):
        try:
            with parsed_path.open("r", encoding="utf-8") as file:
                parsed_document = json.load(file)

            source = parsed_document.get("source") or {}
            file_hash = source.get("file_hash")
            source_path = source.get("file_path")

            if not file_hash or not source_path:
                raise ValueError("Missing source metadata")

            response_group = get_response_group(source_path)
            extraction_path = EXTRACTED_DIR / f"{file_hash}.json"

            with get_connection() as connection:

                response_id = register_response(connection, response_group)
                source_file_id = register_source_file(connection, response_id, parsed_document)
                summary["sources_registered"] += 1

                if not extraction_path.exists():
                    summary["missing_extractions"] += 1
                    continue

                with extraction_path.open("r", encoding="utf-8") as file:
                    extraction_data = json.load(file)

                extraction_source = extraction_data.get("source") or {}
                if extraction_source.get("file_hash") != file_hash:
                    raise ValueError("Extraction source hash mismatch")

                _, created = register_extraction(connection,source_file_id,extraction_data)

                if created:
                    summary["extractions_imported"] += 1
                else:
                    summary["extractions_skipped"] += 1

        except Exception as error:
            summary["failed"] += 1
            print(f"Failed: {parsed_path.name}: {error}")

    return summary


if __name__ == "__main__":
    results = import_existing_data()

    print("\n=== DATABASE IMPORT SUMMARY ===")

    for key, value in results.items():
        print(f"{key}: {value}")
