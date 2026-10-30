
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.styles import Alignment

from src.database.connection import get_connection


def export_review_sheet(output_path: Path):
    connection = get_connection()

    try:
        rows = connection.execute("""
            SELECT
                er.id AS record_id,
                r.council_name,
                sf.filename,
                er.year,
                er.category,
                er.metric_type,
                er.count,
                er.evidence_text,
                er.source_location
            FROM extraction_records er
            JOIN extraction_runs run
                ON er.extraction_run_id = run.id
            JOIN source_files sf
                ON run.source_file_id = sf.id
            JOIN responses r
                ON sf.response_id = r.id
            WHERE er.review_status = 'pending'
              AND run.status = 'completed'
              AND run.model_provider != 'gemini_test'
            ORDER BY sf.filename, er.id
        """).fetchall()

    finally:
        connection.close()

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Review Records"

    headers = [
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

    sheet.append(headers)

    for row in rows:
        sheet.append([
            row["record_id"],
            row["council_name"],
            row["filename"],
            row["year"],
            row["category"],
            row["metric_type"],
            row["count"],
            row["evidence_text"],
            row["source_location"],
            None, None, None, None, None, None, None
        ])

    # Style the header row
    for cell in sheet[1]:
        cell.font = Font(color="FFFFFF", bold=True)
        cell.fill = PatternFill(
            start_color="244062",
            end_color="244062",
            fill_type="solid"
        )

    # Decision dropdown
    decision_validation = DataValidation(
        type="list",
        formula1='"approved,rejected,corrected"',
        allow_blank=True
    )
    sheet.add_data_validation(decision_validation)
    decision_validation.add("J2:J1048576")

    # Useful formatting
    sheet.freeze_panes = "D2"
    sheet.auto_filter.ref = sheet.dimensions

    widths = {
        "A": 12, "B": 22, "C": 28,
        "D": 12, "E": 26, "F": 25,
        "G": 12, "H": 60, "I": 25,
        "J": 20, "K": 18, "L": 25,
        "M": 25, "N": 20, "O": 20,
        "P": 45
    }

    for column, width in widths.items():
        sheet.column_dimensions[column].width = width

    # Highlight editable columns
    for row in sheet.iter_rows(
        min_row=2,
        min_col=10,
        max_col=16
    ):
        for cell in row:
            cell.fill = PatternFill(
                start_color="FFF2CC",
                end_color="FFF2CC",
                fill_type="solid"
            )

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    for row in sheet.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(vertical="top",wrap_text=True)
    workbook.save(output_path)

    return len(rows)
