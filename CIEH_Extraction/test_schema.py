
from pydantic import ValidationError

from src.ai.extraction_schema import (
    ExtractionRecord,
    DocumentExtraction
)


record = ExtractionRecord(
    year="2023",
    category="tattoo_premises",
    metric_type="new_registrations",
    count=18,
    evidence_text="2023 | 16 | 64 | 18 | 98",
    source_location="Table 1, row 2023, PREMISES column",
    notes="The document describes applicants registered during the financial year."
)

result = DocumentExtraction(
    council_name=None,
    records=[record],
    review_required=False
)

print("VALID EXTRACTION:")
print(result.model_dump_json(indent=2))


print("\nTEST INVALID COUNT:")

try:
    invalid_record = ExtractionRecord(
        year="2023",
        category="tattoo_premises",
        metric_type="new_registrations",
        count=-18,
        evidence_text="Test"
    )

except ValidationError as error:
    print(error)