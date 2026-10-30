
from src.database.connection import get_connection


connection = get_connection()

try:
    print("=== EXTRACTION RUNS ===")

    runs = connection.execute("""
        SELECT
            run.id,
            sf.filename,
            run.model_provider,
            run.status,
            run.error_message,
            run.started_at,
            run.completed_at,
            COUNT(er.id) AS record_count
        FROM extraction_runs run
        JOIN source_files sf
            ON run.source_file_id = sf.id
        LEFT JOIN extraction_records er
            ON er.extraction_run_id = run.id
        GROUP BY run.id
        ORDER BY run.id
    """).fetchall()

    for run in runs:
        print(dict(run))

    print("\n=== FOREIGN KEY CHECK ===")

    problems = connection.execute(
        "PRAGMA foreign_key_check"
    ).fetchall()

    if problems:
        for problem in problems:
            print(tuple(problem))
    else:
        print("All foreign key relationships are valid.")

finally:
    connection.close()
