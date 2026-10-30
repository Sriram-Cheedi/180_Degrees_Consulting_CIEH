
from pathlib import Path

from src.ai.batch_extraction import extract_all_documents


summary = extract_all_documents(
    parsed_directory=Path("data/parsed"),
    extracted_directory=Path("data/extracted")
)

print("\n=== BATCH SUMMARY ===")

for key, value in summary.items():
    print(f"{key}: {value}")
