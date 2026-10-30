
import csv
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment

from src.ai.extraction_schema import ExtractionRecord


OUTPUT_HEADERS = [
    "Record ID",
    "Council",
    "Filename",
    "Year",
    "Category",
    "Metric Type",
    "Count",
    "Evidence",
    "Source Location",
    "Review Decision",
    "Reviewer",
    "Reviewer Notes",
]


def read_verified_records(review_path: Path) -> list[dict]:
    workbook = load_workbook(review_path, read_only=True, data_only=True)

    try:
        sheet = workbook["Review Records"]
        rows = sheet.iter_rows(values_only=True)
        headers = next(rows)
        column_index = {
            name: index
            for index, name in enumerate(headers)
            if name is not None
        }

        required_columns = {
            "Record ID",
            "Council",
            "Filename",
            "Year",
            "Category",
            "Metric Type",
            "Count",
            "Evidence",
            "Source Location",
            "Review Decision",
            "Corrected Year",
            "Corrected Category",
            "Corrected Metric Type",
            "Corrected Count",
            "Reviewer",
            "Reviewer Notes",
        }

        missing = required_columns - set(column_index)

        if missing:
            raise ValueError(
                f"Missing review columns: {sorted(missing)}"
            )

        verified = []
        seen_ids = set()

        for row_number, row in enumerate(rows, start=2):

            def get(name):
                return row[column_index[name]]

            record_id = get("Record ID")

            if not record_id:
                continue

            if record_id in seen_ids:
                raise ValueError(
                    f"Row {row_number}: Duplicate record ID"
                )

            seen_ids.add(record_id)

            decision = get("Review Decision")

            if decision is None or not str(decision).strip():
                continue

            decision = str(decision).strip().lower()

            if decision not in {
                "approved",
                "rejected",
                "corrected"
            }:
                raise ValueError(
                    f"Row {row_number}: Invalid review decision"
                )

            if decision == "rejected":
                continue

            reviewer = get("Reviewer")

            if reviewer is None or not str(reviewer).strip():
                raise ValueError(
                    f"Row {row_number}: Reviewer is required"
                )

            corrections = {
                "year": get("Corrected Year"),
                "category": get("Corrected Category"),
                "metric_type": get("Corrected Metric Type"),
                "count": get("Corrected Count"),
            }

            supplied_corrections = {
                key: value
                for key, value in corrections.items()
                if value is not None
                and not (
                    isinstance(value, str)
                    and not value.strip()
                )
            }

            if decision == "approved" and supplied_corrections:
                raise ValueError(
                    f"Row {row_number}: Approved record "
                    "must not contain corrections"
                )

            if decision == "corrected" and not supplied_corrections:
                raise ValueError(
                    f"Row {row_number}: Correction values required"
                )

            count = supplied_corrections.get(
                "count",
                get("Count")
            )

            if type(count) is not int or count < 0:
                raise ValueError(
                    f"Row {row_number}: Count must be a "
                    "nonnegative integer"
                )

            final_record = {
                "year": supplied_corrections.get(
                    "year", get("Year")
                ),
                "category": supplied_corrections.get(
                    "category", get("Category")
                ),
                "metric_type": supplied_corrections.get(
                    "metric_type", get("Metric Type")
                ),
                "count": count,
                "evidence_text": get("Evidence"),
                "source_location": get("Source Location"),
                "notes": None,
            }

            # Reuse the original Gemini extraction schema.
            validated = ExtractionRecord.model_validate(
                final_record
            )

            verified.append({
                "Record ID": record_id,
                "Council": get("Council"),
                "Filename": get("Filename"),
                "Year": validated.year,
                "Category": validated.category,
                "Metric Type": validated.metric_type,
                "Count": validated.count,
                "Evidence": validated.evidence_text,
                "Source Location": validated.source_location,
                "Review Decision": decision,
                "Reviewer": str(reviewer).strip(),
                "Reviewer Notes": get("Reviewer Notes"),
            })

        return verified

    finally:
        workbook.close()


def safe_excel_value(value):
    if isinstance(value, str) and value.startswith(
        ("=", "+", "-", "@")
    ):
        return "'" + value

    return value


def export_verified_data(
    review_path: Path,
    output_directory: Path
) -> int:

    records = read_verified_records(Path(review_path))

    output_directory = Path(output_directory)
    output_directory.mkdir(parents=True, exist_ok=True)

    csv_path = output_directory / "cieh_verified.csv"
    excel_path = output_directory / "cieh_verified.xlsx"

    # CSV
    with csv_path.open(
        "w", newline="", encoding="utf-8-sig"
    ) as file:
        writer = csv.writer(file)
        writer.writerow(OUTPUT_HEADERS)

        for record in records:
            writer.writerow([
                safe_excel_value(record[column])
                for column in OUTPUT_HEADERS
            ])

    # Excel
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Verified Data"
    sheet.append(OUTPUT_HEADERS)

    for record in records:
        sheet.append([
            safe_excel_value(record[column])
            for column in OUTPUT_HEADERS
        ])

    for cell in sheet[1]:
        cell.font = Font(
            bold=True, color="FFFFFF"
        )
        cell.fill = PatternFill(
            fill_type="solid",
            fgColor="244062"
        )

    sheet.freeze_panes = "D2"
    sheet.auto_filter.ref = sheet.dimensions

    widths = {
        "A": 35, "B": 28, "C": 30,
        "D": 15, "E": 30, "F": 26,
        "G": 12, "H": 65, "I": 35,
        "J": 20, "K": 22, "L": 45
    }

    for column, width in widths.items():
        sheet.column_dimensions[column].width = width

    for row in sheet.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(
                vertical="top", wrap_text=True
            )

    workbook.save(excel_path)

    print(f"Verified records: {len(records)}")
    print(f"CSV: {csv_path}")
    print(f"Excel: {excel_path}")

    return len(records)
