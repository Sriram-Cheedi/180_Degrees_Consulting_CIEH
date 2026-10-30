
from src.database.connection import (
    get_connection,
    DATABASE_PATH
)


connection = get_connection()

print("Database path:", DATABASE_PATH)

result = connection.execute(
    "SELECT sqlite_version()"
).fetchone()

print("SQLite version:", result[0])

print("Connection successful!")

connection.close()
