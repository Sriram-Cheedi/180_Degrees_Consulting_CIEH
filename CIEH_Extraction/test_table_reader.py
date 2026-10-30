
import json
from pathlib import Path

from src.ai.table_reader import get_tables


parsed_directory = Path("data/parsed")

for file_path in parsed_directory.glob("*.json"):

    with file_path.open("r", encoding="utf-8") as file:
        parsed_document = json.load(file)

    if parsed_document.get("filename") != "image.png":
        continue

    tables = get_tables(parsed_document)

    print(f"Tables found: {len(tables)}")

    for table in tables:
        print(f"\nTable {table['table_index']}")

        for row in table["rows"]:
            print(row)

    break
else:
    print("image.png not found in parsed directory")
