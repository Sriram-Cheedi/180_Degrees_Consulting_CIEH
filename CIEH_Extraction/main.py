from pathlib import Path
from src.ingestion.file_identification import identify_files
from src.ingestion.file_manager import prepare_files, get_pending_files


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

    files_data = prepare_files(RAW_DATA_DIRECTORY, EXTENSIONS)
    pending_files = get_pending_files(files_data)

    for file_metadata in files_data:
        print(file_metadata)

    print("\nTotal files:", len(files_data))
    print("Pending files:", len(pending_files))
    print("Duplicate files:", len(files_data) - len(pending_files))