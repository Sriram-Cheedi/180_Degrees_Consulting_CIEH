
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.styles import Alignment, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

from src.review.export_review_sheet import export_review_sheet


def sync_review_sheet(
    extracted_directory: Path,
    review_path: Path
) -> dict:

    extracted_directory = Path(extracted_directory)
    review_path = Path(review_path)

    review_path.parent.mkdir(parents=True, exist_ok=True)

    # First run: create the workbook normally.
    if not review_path.exists():
        total = export_review_sheet(
            extracted_directory,
            review_path
        )

        return {
            "added": total,
            "existing": 0,
            "total": total
        }

    # Generate a temporary sheet from the current JSON files.
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir) / "new_records.xlsx"

        export_review_sheet(
            extracted_directory,
            temp_path
        )

        existing_book = load_workbook(review_path)
        new_book = load_workbook(temp_path, read_only=True)

        try:
            existing_sheet = existing_book["Review Records"]
            new_sheet = new_book["Review Records"]

            existing_ids = set()

            for row in existing_sheet.iter_rows(
                min_row=2,
                values_only=True
            ):
                record_id = row[0]

                if record_id:
                    if record_id in existing_ids:
                        raise ValueError(
                            f"Duplicate ID in review sheet: {record_id}"
                        )

                    existing_ids.add(record_id)

            added = 0
            previous_last_row = existing_sheet.max_row

            for row in new_sheet.iter_rows(
                min_row=2,
                values_only=True
            ):
                record_id = row[0]

                if record_id in existing_ids:
                    continue

                existing_sheet.append(row)
                existing_ids.add(record_id)
                added += 1

            if added:
                yellow = PatternFill(
                    fill_type="solid",
                    fgColor="FFF2CC"
                )

                for row in existing_sheet.iter_rows(
                    min_row=previous_last_row + 1
                ):
                    for cell in row:
                        cell.alignment = Alignment(
                            wrap_text=True,
                            vertical="top"
                        )

                    for cell in row[9:16]:
                        cell.fill = yellow

                # Add dropdown validation for new rows.
                validation = DataValidation(
                    type="list",
                    formula1='"approved,rejected,corrected"',
                    allow_blank=True
                )

                existing_sheet.add_data_validation(validation)

                validation.add(
                    f"J{previous_last_row + 1}:"
                    f"J{existing_sheet.max_row}"
                )

                # Back up the original workbook before saving.
                backup_dir = review_path.parent / "backups"
                backup_dir.mkdir(parents=True, exist_ok=True)

                timestamp = datetime.now().strftime(
                    "%Y%m%d_%H%M%S_%f"
                )

                backup_path = (
                    backup_dir / f"review_before_sync_{timestamp}.xlsx"
                )

                shutil.copy2(review_path, backup_path)

                # Save to a temporary file first.
                temp_output = review_path.with_name(
                    review_path.stem + "_updating.xlsx"
                )

                try:
                    existing_book.save(temp_output)
                    os.replace(temp_output, review_path)
                finally:
                    temp_output.unlink(missing_ok=True)

                print(f"Review backup: {backup_path}")

            return {
                "added": added,
                "existing": len(existing_ids) - added,
                "total": len(existing_ids)
            }

        finally:
            existing_book.close()
            new_book.close()
