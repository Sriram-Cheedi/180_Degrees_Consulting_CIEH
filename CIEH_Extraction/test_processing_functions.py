
from src.database.connection import get_connection
from src.database.processing_history import (
    start_extraction_run,
    fail_extraction_run,
    get_extraction_history
)


with get_connection() as connection:
    source = connection.execute(
        "SELECT id FROM source_files LIMIT 1"
    ).fetchone()

if source is None:
    raise ValueError("No registered source files")

source_id = source["id"]

run_id = start_extraction_run(
    source_file_id=source_id,
    model_provider="gemini_test",
    model_name="test-model"
)

fail_extraction_run(
    run_id,
    "Simulated API failure"
)

history = get_extraction_history(source_id)

test_run = next(
    item for item in history
    if item["id"] == run_id
)

print("Run ID:", test_run["id"])
print("Status:", test_run["status"])
print("Error:", test_run["error_message"])

assert test_run["status"] == "failed"
print("Processing history functions passed!")
