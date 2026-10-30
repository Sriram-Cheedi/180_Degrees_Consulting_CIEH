
from pathlib import Path
from src.review.export_review_sheet import export_review_sheet


output_path = Path("data/review/cieh_review.xlsx")

total = export_review_sheet(output_path)

print(f"Exported {total} records")
print(f"Saved to: {output_path}")
