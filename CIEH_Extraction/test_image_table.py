
from pathlib import Path

from docling.document_converter import DocumentConverter, ImageFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, RapidOcrOptions


image_path = Path("data/raw/Response_A/image.png")

options = PdfPipelineOptions()
options.do_ocr = True
options.do_table_structure = True
options.ocr_options = RapidOcrOptions()

converter = DocumentConverter(
    allowed_formats=[InputFormat.IMAGE],
    format_options={
        InputFormat.IMAGE: ImageFormatOption(
            pipeline_options=options
        )
    }
)

result = converter.convert(image_path)
document = result.document

print("\n=== EXTRACTED CONTENT ===")
print(document.export_to_markdown())

print("\n=== TABLES DETECTED ===")
print(len(document.tables))

for i, table in enumerate(document.tables, start=1):
    print(f"\nTable {i}")
    print(table.export_to_dataframe().to_string(index=False))
