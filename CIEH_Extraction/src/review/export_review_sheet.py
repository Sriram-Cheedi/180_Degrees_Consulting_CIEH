
import json
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.datavalidation import DataValidation


HEADERS = [
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
    "Reviewer Notes"
]


def export_review_sheet(
    extracted_directory: Path,
    output_path: Path
) -> int:

    extracted_directory = Path(extracted_directory)
    output_path = Path(output_path)

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Review Records"

    sheet.append(HEADERS)
    seen_sources = set()
    total = 0

    for json_path in sorted(extracted_directory.glob("*.json")):

        data = json.loads(
            json_path.read_text(encoding="utf-8")
        )

        source = data.get("source") or {}
        file_hash = source.get("file_hash")

        if not file_hash:
            raise ValueError(
                f"Missing source hash: {json_path.name}"
            )

        # Prevent processing the same source twice.
        if file_hash in seen_sources:
            continue

        seen_sources.add(file_hash)

        extraction = data.get("extraction") or {}
        council = extraction.get("council_name")
        filename = data.get("filename")

        records = extraction.get("records", [])

        for index, record in enumerate(records, start=1):

            record_id = f"{file_hash}-{index:04d}"

            sheet.append([
                record_id,
                council,
                filename,
                record.get("year"),
                record["category"],
                record["metric_type"],
                record["count"],
                record["evidence_text"],
                record.get("source_location"),
                None, None, None, None, None, None, None
            ])

            total += 1

    # Header formatting
    for cell in sheet[1]:
        cell.font = Font(
            bold=True,
            color="FFFFFF"
        )
        cell.fill = PatternFill(
            fill_type="solid",
            fgColor="244062"
        )

    # Review decision dropdown
    validation = DataValidation(
        type="list",
        formula1='"approved,rejected,corrected"',
        allow_blank=True
    )

    sheet.add_data_validation(validation)
    validation.add(f"J2:J{max(2, total + 1)}")

    # Freeze useful columns
    sheet.freeze_panes = "D2"
    sheet.auto_filter.ref = sheet.dimensions

    widths = {
        "A": 28,
        "B": 30,
        "C": 30,
        "D": 15,
        "E": 30,
        "F": 26,
        "G": 12,
        "H": 65,
        "I": 35,
        "J": 20,
        "K": 18,
        "L": 30,
        "M": 26,
        "N": 20,
        "O": 22,
        "P": 45
    }

    for column, width in widths.items():
        sheet.column_dimensions[column].width = width

    # Keep text inside its cells.
    for row in sheet.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(
                wrap_text=True,
                vertical="top"
            )

    # Highlight editable review columns.
    yellow = PatternFill(
        fill_type="solid",
        fgColor="FFF2CC"
    )

    for row in sheet.iter_rows(
        min_row=2,
        min_col=10,
        max_col=16
    ):
        for cell in row:
            cell.fill = yellow

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # Never silently overwrite human review work.
    if output_path.exists():
        raise FileExistsError(
            f"Review workbook already exists: {output_path}"
        )

    workbook.save(output_path)

    return total
