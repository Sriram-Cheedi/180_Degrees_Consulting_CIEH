
from src.database.connection import get_connection

connection = get_connection()

try:
    rows = connection.execute(
        """
        SELECT
            r.id AS response_id,
            r.response_group,
            r.council_name,
            GROUP_CONCAT(sf.filename, ', ') AS filenames
        FROM responses r
        JOIN source_files sf
            ON sf.response_id = r.id
        WHERE r.council_name IS NULL
           OR TRIM(r.council_name) = ''
        GROUP BY r.id
        ORDER BY r.id
        """
    ).fetchall()

    print("=== RESPONSES MISSING COUNCIL NAMES ===")

    for row in rows:
        print(dict(row))

    print(f"\nTotal responses requiring identification: {len(rows)}")

finally:
    connection.close()
