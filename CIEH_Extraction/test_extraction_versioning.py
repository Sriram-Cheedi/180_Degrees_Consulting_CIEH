
from src.database.connection import get_connection
from src.database.migrations import add_extraction_result_hash
from src.database.import_data import register_extraction


add_extraction_result_hash()

connection = get_connection()

source = connection.execute(
    "SELECT id FROM source_files LIMIT 1"
).fetchone()

if source is None:
    raise ValueError("No source files registered")

source_file_id = source["id"]

sample_extraction = {
    "model_provider": "gemini_test",
    "model_name": "test-model",
    "extraction": {
        "records": [
            {
                "year": "2023",
                "category": "tattoo_premises",
                "metric_type": "new_registrations",
                "count": 18,
                "evidence_text": "2023 premises: 18",
                "source_location": "Test table",
                "notes": None
            }
        ]
    }
}

try:
    with connection:
        first_id, created1 = register_extraction(
            connection,
            source_file_id,
            sample_extraction
        )

        second_id, created2 = register_extraction(
            connection,
            source_file_id,
            sample_extraction
        )

    print("First import:", first_id, created1)
    print("Second import:", second_id, created2)

finally:
    connection.close()
