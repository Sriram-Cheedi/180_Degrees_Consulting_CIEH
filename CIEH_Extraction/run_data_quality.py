
import csv
from pathlib import Path

from src.validation.data_quality import audit_database


summary, issues = audit_database()

print("=== DATA QUALITY SUMMARY ===")

for key, value in summary.items():
    print(f"{key}: {value}")

output_path = Path("data/review/data_quality_issues.csv")
output_path.parent.mkdir(parents=True, exist_ok=True)

with output_path.open(
    "w",
    newline="",
    encoding="utf-8-sig"
) as file:
    writer = csv.DictWriter(
        file,
        fieldnames=[
            "record_id",
            "filename",
            "issue_type",
            "message"
        ]
    )

    writer.writeheader()
    writer.writerows(issues)

print(f"\nAudit report saved to: {output_path}")

for issue in issues[:10]:
    print(issue)
