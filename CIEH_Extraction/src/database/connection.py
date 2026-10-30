
import sqlite3
from pathlib import Path


BASE_DIRECTORY = Path(__file__).resolve().parents[2]

DATABASE_PATH = BASE_DIRECTORY / "data" / "database" / "cieh.db"


def get_connection():
    DATABASE_PATH.parent.mkdir(parents=True,exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection
