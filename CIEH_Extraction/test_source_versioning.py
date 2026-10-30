
from src.database.connection import get_connection
from src.database.source_versioning import check_source_version


connection = get_connection()

row = connection.execute(
    """
    SELECT file_path, file_hash
    FROM source_files
    LIMIT 1
    """
).fetchone()

connection.close()

if row is None:
    raise ValueError("No source files registered yet")

file_path = row["file_path"]
file_hash = row["file_hash"]

print("TEST 1 — Existing source:")
print(check_source_version(file_path, file_hash))

print("\nTEST 2 — Changed contents:")
print(check_source_version(file_path, "different_hash_for_test"))

print("\nTEST 3 — New source:")
print(check_source_version(
    "test/new_file.pdf",
    "new_test_hash"
))
