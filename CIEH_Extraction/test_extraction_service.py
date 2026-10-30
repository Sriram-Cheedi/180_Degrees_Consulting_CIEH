
import json
from pathlib import Path

from src.ai.extraction_service import extract_document


PARSED_DIRECTORY = Path("data/parsed")

for file_path in PARSED_DIRECTORY.glob("*.json"):

    with file_path.open("r", encoding="utf-8") as file:
        document = json.load(file)

    if document.get("filename") == "image.png":
        break

else:
    raise FileNotFoundError("Parsed image.png not found")


result = extract_document(document)

print("\n=== EXTRACTION SUMMARY ===")
print("Filename:", result["filename"])
print("Provider:", result["model_provider"])
print("Review status:", result["review_status"])
print("Validation:", result["validation_status"])
print("Records:", len(result["extraction"]["records"]))

print("\n=== FIRST THREE RECORDS ===")
for record in result["extraction"]["records"][:3]:
    print(json.dumps(record, indent=2))
