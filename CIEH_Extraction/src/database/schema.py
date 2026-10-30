from src.database.connection import get_connection

def create_tables():
    connection = get_connection()

    try:
        connection.executescript("""
            CREATE TABLE IF NOT EXISTS responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                response_group TEXT NOT NULL UNIQUE,
                council_name TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS source_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                response_id INTEGER NOT NULL,
                filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_hash TEXT NOT NULL,
                extension TEXT,
                file_size INTEGER,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                UNIQUE(file_path),

                FOREIGN KEY (response_id)
                    REFERENCES responses(id)
            );

            CREATE INDEX IF NOT EXISTS idx_source_file_hash
                ON source_files(file_hash);

            CREATE TABLE IF NOT EXISTS extraction_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_file_id INTEGER NOT NULL,
                model_provider TEXT NOT NULL,
                model_name TEXT,
                status TEXT NOT NULL DEFAULT 'pending',
                error_message TEXT,
                started_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                completed_at TEXT,

                FOREIGN KEY (source_file_id)
                    REFERENCES source_files(id)
            );

            CREATE TABLE IF NOT EXISTS extraction_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                extraction_run_id INTEGER NOT NULL,
                year TEXT,
                category TEXT NOT NULL,
                metric_type TEXT NOT NULL,
                count INTEGER NOT NULL CHECK(count >= 0),
                evidence_text TEXT NOT NULL,
                source_location TEXT,
                notes TEXT,
                review_status TEXT NOT NULL DEFAULT 'pending',

                FOREIGN KEY (extraction_run_id)
                    REFERENCES extraction_runs(id)
            );

            CREATE TABLE IF NOT EXISTS record_reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                extraction_record_id INTEGER NOT NULL,
                decision TEXT NOT NULL CHECK(
                    decision IN ('approved', 'rejected', 'corrected')
                ),
                corrected_year TEXT,
                corrected_category TEXT,
                corrected_metric_type TEXT,
                corrected_count INTEGER CHECK(
                    corrected_count IS NULL OR corrected_count >= 0
                ),
                reviewer TEXT,
                reviewer_notes TEXT,
                reviewed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (extraction_record_id)
                    REFERENCES extraction_records(id)
            );
        """)

        connection.commit()

    finally:
        connection.close()
