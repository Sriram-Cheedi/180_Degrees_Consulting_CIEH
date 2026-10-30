
from pathlib import Path

from src.ai.save_extraction import save_extraction


sample_extraction = {
    "source_id": "Source_002",
    "response_id": "Response_002",
    "filename": "image.png",
    "source": {
        "file_hash": "test_hash_123"
    },
    "model_provider": "gemini",
    "extraction": {
        "council_name": None,
        "records": [],
        "review_required": True,
        "review_reason": "Test only"
    },
    "review_status": "pending",
    "validation_status": "schema_valid"
}

output_path = save_extraction(
    sample_extraction,
    Path("data/extracted")
)

print("Saved successfully:", output_path)
