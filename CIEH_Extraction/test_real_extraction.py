
import json
from pathlib import Path

from src.ai.ollama_client import generate_response
from src.ai.extraction_prompt import build_extraction_prompt
from src.ai.extraction_schema import DocumentExtraction
from src.ai.gemini_client import generate_gemini_extraction


PARSED_DIRECTORY = Path("data/parsed")

# Locate the file by filename, not temporary source ID.
parsed_document = None

for file_path in PARSED_DIRECTORY.glob("*.json"):
    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if data.get("filename") == "image.png":
        parsed_document = data
        break

if parsed_document is None:
    raise FileNotFoundError(
        "Could not find the parsed JSON for image.png"
    )

document_text = parsed_document["content"]

prompt = build_extraction_prompt(document_text)


extraction = generate_gemini_extraction(prompt)

print("\n=== GEMINI EXTRACTION ===")
print(extraction.model_dump_json(indent=2))
