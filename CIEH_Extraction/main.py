from pathlib import Path
from src.ingestion.file_identification import identify_files

BASE_DIRECTORY = Path(__file__).resolve().parent

DATA_DIRECTORY = BASE_DIRECTORY / "data"
RAW_DATA_DIRECTORY = DATA_DIRECTORY / "raw"
PARSED_DATA_DIRECTORY = DATA_DIRECTORY / "parsed"
REVIEW_DATA_DIRECTORY = DATA_DIRECTORY / "review"
OUTPUT_DIRECTORY = DATA_DIRECTORY / "output"
DATABASE_DIRECTORY = DATA_DIRECTORY / "database"

def create_directories():
    for folder in [DATA_DIRECTORY, RAW_DATA_DIRECTORY, PARSED_DATA_DIRECTORY, REVIEW_DATA_DIRECTORY, OUTPUT_DIRECTORY, DATABASE_DIRECTORY]:
        folder.mkdir(parents=True, exist_ok=True)

EXTENSIONS = ['.pdf', ".docx", ".xlsx", '.xls', ".csv", ".txt", ".png", ".jpg", ".jpeg"]


def find_raw_files_paths(extenstions, raw_data_directory):
    raw_data_paths = []
    for item in raw_data_directory.rglob("*"):
        if item.is_dir():
            continue
        else:
            if item.suffix.lower() in extenstions:
                raw_data_paths.append(item)
    
    return raw_data_paths


if __name__ == "__main__":
    create_directories()

    file_paths = find_raw_files_paths(EXTENSIONS,RAW_DATA_DIRECTORY)
    
    files_metadata = identify_files(file_paths, RAW_DATA_DIRECTORY)

    for file in file_paths:
        print(file)

    for metadata in files_metadata:
        print(metadata)