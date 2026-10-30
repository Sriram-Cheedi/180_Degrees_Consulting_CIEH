
from pathlib import Path

from src.review.export_verified_data import export_verified_data


output_directory = Path("data/output")

total = export_verified_data(output_directory)

print(f"\nFinished. Total verified records: {total}")
