
from datetime import datetime
from pathlib import Path
import shutil

from import_reviews import import_real_reviews

from src.review.export_verified_data import export_verified_data
from src.review.export_review_sheet import export_review_sheet


BASE_DIR = Path(__file__).resolve().parent

REVIEW_DIR = BASE_DIR / "data" / "review"
OUTPUT_DIR = BASE_DIR / "data" / "output"

REVIEW_FILE = REVIEW_DIR / "cieh_review.xlsx"
ARCHIVE_DIR = REVIEW_DIR / "archive"


def finalize_pipeline():

    print("\n=== CIEH REVIEW FINALISATION ===")

    if not REVIEW_FILE.exists():
        raise FileNotFoundError(
            f"Missing review workbook: {REVIEW_FILE}"
        )

    # STEP 1 — Import verified decisions into SQLite.
    # This function creates a DB backup before importing.
    print("\n[1/4] Importing human reviews...")

    import_real_reviews()

    # STEP 2 — Archive the reviewed workbook.
    print("\n[2/4] Archiving review workbook...")

    ARCHIVE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    archive_path = (
        ARCHIVE_DIR / f"review_{timestamp}.xlsx"
    )

    shutil.copy2(REVIEW_FILE, archive_path)

    print(f"Archived to: {archive_path}")

    # STEP 3 — Export the verified dataset.
    print("\n[3/4] Exporting verified records...")

    total = export_verified_data(OUTPUT_DIR)

    print(f"Verified records: {total}")

    # STEP 4 — Generate a new pending-only review sheet.
    print("\n[4/4] Preparing next review batch...")

    pending = export_review_sheet(REVIEW_FILE)

    print(f"Pending review records: {pending}")

    print("\n=== FINALISATION COMPLETE ===")


if __name__ == "__main__":
    finalize_pipeline()
