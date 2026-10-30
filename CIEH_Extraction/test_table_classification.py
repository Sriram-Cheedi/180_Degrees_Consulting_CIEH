
import json
from pathlib import Path

from src.ai.table_reader import get_tables
from src.ai.ollama_client import generate_response
from src.ai.table_classification_prompt import (
    build_table_classification_prompt
)
from src.ai.table_classification_schema import TableClassification


parsed_directory = Path("data/parsed")

for file_path in parsed_directory.glob("*.json"):
    with file_path.open("r", encoding="utf-8") as file:
        parsed_document = json.load(file)

    if parsed_document.get("filename") == "image.png":
        break
else:
    raise FileNotFoundError("image.png parsed JSON not found")


tables = get_tables(parsed_document)

for table in tables:
    prompt = build_table_classification_prompt(
        table,
        parsed_document["content"]
    )

    response = generate_response(
        prompt,
        TableClassification.model_json_schema()
    )

    classification = TableClassification.model_validate_json(
        response
    )

    print(classification.model_dump_json(indent=2))
