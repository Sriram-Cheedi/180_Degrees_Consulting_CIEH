
import csv
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

from src.database.connection import get_connection


HEADERS = [
    "Record ID",
    "Council",
    "Year",
    "Category",
    "Metric Type",
    "Count",
    "Evidence",
    "Source Location",
    "Source Filename",
    "Review Decision",
    "Reviewer",
    "Reviewer Notes"
]


def get_verified_records(connection) -> list[dict]:

    rows = connection.execute(
        """
        SELECT
            er.id AS record_id,
            r.council_name AS council,
            COALESCE(rr.corrected_year, er.year) AS year,
            COALESCE(
                rr.corrected_category, er.category
            ) AS category,
            COALESCE(
                rr.corrected_metric_type, er.metric_type
            ) AS metric_type,
            COALESCE(rr.corrected_count, er.count) AS count,
            er.evidence_text AS evidence,
            er.source_location,
            sf.filename AS source_filename,
            rr.decision AS review_decision,
            rr.reviewer,
            rr.reviewer_notes

        FROM extraction_records er

        JOIN extraction_runs run
            ON er.extraction_run_id = run.id

        JOIN source_files sf
            ON run.source_file_id = sf.id

        JOIN responses r
            ON sf.response_id = r.id

        JOIN record_reviews rr
            ON rr.id = (
                SELECT MAX(rr2.id)
                FROM record_reviews rr2
                WHERE rr2.extraction_record_id = er.id
            )

        WHERE rr.decision IN ('approved', 'corrected')
          AND er.review_status IN ('approved', 'corrected')
          AND run.status = 'completed'
          AND run.model_provider != 'gemini_test'

        ORDER BY r.council_name, year, er.id
        """
    ).fetchall()

    return [dict(row) for row in rows]


def safe_excel_value(value):
    # Prevent source text from being interpreted as a formula.
    if isinstance(value, str) and value.startswith(
        ("=", "+", "-", "@")
    ):
        return "'" + value

    return value


def export_verified_data(
    output_directory: Path,
    connection=None
) -> int:

    output_directory = Path(output_directory)
    output_directory.mkdir(parents=True, exist_ok=True)

    owns_connection = connection is None

    if owns_connection:
        connection = get_connection()

    try:
        records = get_verified_records(connection)
    finally:
        if owns_connection:
            connection.close()

    csv_path = output_directory / "cieh_verified.csv"
    excel_path = output_directory / "cieh_verified.xlsx"

    # Export CSV
    with csv_path.open(
        "w", newline="", encoding="utf-8-sig"
    ) as file:

        writer = csv.writer(file)
        writer.writerow(HEADERS)

        for record in records:
            writer.writerow([
                safe_excel_value(value)
                for value in record.values()
            ])

    # Export Excel
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Verified Data"

    sheet.append(HEADERS)

    for record in records:
        sheet.append([
            safe_excel_value(value)
            for value in record.values()
        ])

    for cell in sheet[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(
            fill_type="solid",
            fgColor="244062"
        )

    sheet.freeze_panes = "C2"
    sheet.auto_filter.ref = sheet.dimensions

    widths = {
        "A": 13, "B": 28, "C": 12,
        "D": 29, "E": 26, "F": 13,
        "G": 55, "H": 35, "I": 30,
        "J": 20, "K": 22, "L": 40
    }

    for column, width in widths.items():
        sheet.column_dimensions[column].width = width

    for row in sheet.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(
                vertical="top",
                wrap_text=True
            )

    workbook.save(excel_path)

    missing_councils = sum(
        not record["council"] for record in records
    )

    print(f"Verified records exported: {len(records)}")
    print(f"Records missing council: {missing_councils}")
    print(f"CSV: {csv_path}")
    print(f"Excel: {excel_path}")

    if missing_councils:
        print(
            "WARNING: Resolve missing council names "
            "before using this dataset for analysis."
        )

    return len(records)
