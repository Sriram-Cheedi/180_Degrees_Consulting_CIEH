
from src.database.connection import get_connection


connection = get_connection()

tables = [
    "responses",
    "source_files",
    "extraction_runs",
    "extraction_records",
    "record_reviews"
]

for table in tables:
    result = connection.execute(
        f"SELECT COUNT(*) AS total FROM {table}"
    ).fetchone()

    print(f"{table}: {result['total']}")


print("\n=== SAMPLE EXTRACTION RECORDS ===")

rows = connection.execute("""
    SELECT
        sf.filename,
        er.year,
        er.category,
        er.metric_type,
        er.count,
        er.review_status
    FROM extraction_records er
    JOIN extraction_runs run
      ON er.extraction_run_id = run.id
    JOIN source_files sf
      ON run.source_file_id = sf.id
    LIMIT 10
""").fetchall()

for row in rows:
    print(dict(row))

connection.close()
