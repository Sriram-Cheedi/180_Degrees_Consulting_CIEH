
from pathlib import Path
from datetime import datetime
import sqlite3

from src.database.connection import (
    get_connection,
    DATABASE_PATH
)
from src.review.import_review_sheet import import_review_sheet


BASE_DIR = Path(__file__).resolve().parent
REVIEW_FILE = BASE_DIR / "data" / "review" / "cieh_review.xlsx"
BACKUP_DIR = BASE_DIR / "data" / "database" / "backups"


def create_database_backup() -> Path:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    backup_path = BACKUP_DIR / f"cieh_before_review_{timestamp}.db"

    source = get_connection()
    destination = sqlite3.connect(backup_path)

    try:
        source.backup(destination)
    finally:
        destination.close()
        source.close()

    return backup_path


def import_real_reviews():
    if not REVIEW_FILE.exists():
        raise FileNotFoundError(
            f"Review sheet not found: {REVIEW_FILE}"
        )

    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"Database not found: {DATABASE_PATH}"
        )

    backup_path = create_database_backup()

    print(f"Database backup created: {backup_path}")

    connection = get_connection()

    try:
        summary = import_review_sheet(
            REVIEW_FILE,
            connection
        )

        print("\n=== REVIEW IMPORT SUMMARY ===")

        for key, value in summary.items():
            print(f"{key}: {value}")

        print("\nReview import completed successfully.")

    finally:
        connection.close()


if __name__ == "__main__":
    import_real_reviews()
