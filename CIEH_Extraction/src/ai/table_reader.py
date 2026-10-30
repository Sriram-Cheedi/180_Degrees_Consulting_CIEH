
def get_tables(parsed_document: dict) -> list[dict]:
    structure = parsed_document.get("structure", {})

    tables = structure.get("tables", [])

    extracted_tables = []

    for table_index, table in enumerate(tables, start=1):
        table_data = table.get("data", {})

        grid = table_data.get("grid", [])

        rows = []

        for row in grid:
            values = []

            for cell in row:
                values.append(cell.get("text", ""))

            rows.append(values)

        extracted_tables.append({
            "table_index": table_index,
            "rows": rows
        })

    return extracted_tables
