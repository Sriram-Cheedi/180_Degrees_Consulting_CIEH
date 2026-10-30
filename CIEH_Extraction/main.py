
import csv
import subprocess
import sys
from pathlib import Path

from src.database.schema import create_tables
from src.database.migrations import add_extraction_result_hash
from src.ai.batch_extraction import extract_all_documents
from src.validation.data_quality import audit_database
from src.review.export_review_sheet import export_review_sheet


BASE_DIR = Path(__file__).resolve().parent

PARSED_DIR = BASE_DIR / "data" / "parsed"
EXTRACTED_DIR = BASE_DIR / "data" / "extracted"
REVIEW_DIR = BASE_DIR / "data" / "review"


def run_pipeline():

    print("\n=== CIEH AUTOMATED PIPELINE ===")

    # 1. Initialise database
    print("\n[1/5] Initialising database...")

    create_tables()
    add_extraction_result_hash()

    # 2. Discover and parse documents
    print("\n[2/5] Parsing documents...")

    subprocess.run(
        [sys.executable, str(BASE_DIR / "parse_pipeline.py")],
        cwd=BASE_DIR,
        check=True
    )

    # 3. Gemini extraction and SQLite storage
    print("\n[3/5] Extracting documents...")

    summary = extract_all_documents(
        PARSED_DIR,
        EXTRACTED_DIR
    )

    print("Extraction summary:", summary)

    # 4. Data quality audit
    print("\n[4/5] Running quality checks...")

    audit_summary, issues = audit_database()

    REVIEW_DIR.mkdir(parents=True, exist_ok=True)

    audit_path = REVIEW_DIR / "data_quality_issues.csv"

    with audit_path.open(
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "record_id",
                "filename",
                "issue_type",
                "message"
            ]
        )

        writer.writeheader()
        writer.writerows(issues)

    print("Quality summary:", audit_summary)

    # 5. Generate review sheet
    print("\n[5/5] Preparing Excel review sheet...")

    review_path = REVIEW_DIR / "cieh_review.xlsx"

    if review_path.exists():
        print("Existing review sheet preserved.")
    else:
        total = export_review_sheet(review_path)
        print(f"Exported {total} pending records.")

    print("\n=== PIPELINE FINISHED ===")


if __name__ == "__main__":
    run_pipeline()
